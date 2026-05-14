import streamlit as st
from PyPDF2 import PdfReader
import pandas as pd
from io import BytesIO
import re

st.title("PDF a Excel")

archivo = st.file_uploader("Subí un PDF", type="pdf")

if archivo:
    reader = PdfReader(archivo)
    texto = reader.pages[0].extract_text()

    # ✅ cortar encabezado correctamente
    if "Código Producto" in texto:
        texto = texto.split("Código Producto", 1)[1]

    st.text_area("Texto", texto, height=300)

    lineas = [l.strip() for l in texto.split("\n") if l.strip()]

    filas = []
    descripcion = []

    for linea in lineas:

        # ✅ SOLO líneas válidas (las que tienen cantidad real)
        if re.search(r"X\s*\d+,\d+\s+unidades", linea):

            # ✅ cantidad correcta (48, 36, etc.)
            match = re.search(r"X\s*(\d+),", linea)
            cantidad = int(match.group(1)) if match else 0

            numeros = re.findall(r"\d+,\d+", linea)

            if len(numeros) >= 4:
                precio = float(numeros[1].replace(",", "."))
                subtotal = float(numeros[3].replace(",", "."))
                total = float(numeros[-1].replace(",", "."))
            else:
                precio = subtotal = total = 0

            producto = " ".join(descripcion).strip()

            filas.append({
                "Producto": producto,
                "Cantidad": cantidad,
                "Precio Unitario": precio,
                "Subtotal": subtotal,
                "Total c/ IVA": total
            })

            descripcion = []

        else:
            # ✅ evitar meter encabezado
            if "Subtotal" not in linea and "Código" not in linea:
                descripcion.append(linea)

    if filas:
        df = pd.DataFrame(filas)
        st.dataframe(df)

        buffer = BytesIO()
        df.to_excel(buffer, index=False, engine="openpyxl")

        st.download_button(
            "Descargar Excel",
            buffer.getvalue(),
            "facturas.xlsx"
        )
    else:
        st.warning("No se detectaron productos.")
