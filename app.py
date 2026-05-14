import streamlit as st
from PyPDF2 import PdfReader
import pandas as pd
from io import BytesIO
import re

st.title("PDF a Excel - Facturas PAPUS")

archivo = st.file_uploader("Subí un PDF", type="pdf")

if archivo:
    reader = PdfReader(archivo)
    texto = reader.pages[0].extract_text()

    st.text_area("Texto detectado", texto, height=300)

    lineas = [l.strip() for l in texto.split("\n") if l.strip()]

    filas = []
    buffer_descripcion = []

    for linea in lineas:

        # ✅ DETECTA SOLO LA LINEA CORRECTA (X 48,00 unidades)
        if re.search(r"^X\s*\d+,\d+\s+unidades", linea):

            # 🔢 cantidad
            m = re.search(r"X\s*(\d+),", linea)
            cantidad = int(m.group(1)) if m else 0

            # 💲 numeros
            nums = re.findall(r"\d+,\d+", linea)

            if len(nums) >= 4:
                precio = float(nums[1].replace(",", "."))
                subtotal = float(nums[3].replace(",", "."))
                total = float(nums[-1].replace(",", "."))
            else:
                precio = subtotal = total = 0

            producto = " ".join(buffer_descripcion)

            filas.append({
                "Producto": producto,
                "Cantidad": cantidad,
                "Precio Unitario": precio,
                "Subtotal": subtotal,
                "Total c/ IVA": total
            })

            buffer_descripcion = []

        else:
            buffer_descripcion.append(linea)

    # ✅ MOSTRAR RESULTADO
    if filas:
        df = pd.DataFrame(filas)
        st.dataframe(df)

        # ✅ EXPORTAR A EXCEL
        buffer = BytesIO()
        df.to_excel(buffer, index=False, engine="openpyxl")

        st.download_button(
            "⬇️ Descargar Excel",
            buffer.getvalue(),
            "facturas.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    else:
        st.warning("No se detectaron productos.")
