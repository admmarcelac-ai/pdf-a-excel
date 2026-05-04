import streamlit as st
import pandas as pd
from PyPDF2 import PdfReader
from io import BytesIO
import re

st.set_page_config(page_title="PDFs de Facturas a Excel", layout="wide")
st.title("📄 PDFs de Facturas → Excel único")

def leer_pdf(archivo):
    reader = PdfReader(archivo)
    texto = reader.pages[0].extract_text()
    return texto if texto else ""

def buscar(patron, texto):
    m = re.search(patron, texto, re.IGNORECASE)
    return m.group(1).strip() if m else ""

def procesar_pdf(pdf):
    texto = leer_pdf(pdf)
    st.text_area("Texto detectado en el PDF", texto, height=300)

    datos_base = {
        "Receptor": "SALUD METROPOLITANA SA",
        "CUIT Receptor": "30715602012",
        "Emisor": "PAPUS SRL",
        "CUIT Emisor": "30714997234",
        "Fecha": buscar(r"(\d{2}/\d{2}/\d{4})", texto),
        "Tipo": "FACTURA A",
        "Punto de Venta": "0020",
        "Número": buscar(r"(\d{8})", texto),
    }

    filas = []

    lineas = [l.strip() for l in texto.split("\n") if l.strip()]

    for i in range(1, len(lineas)):
        linea = lineas[i]

        if "unidades" in linea and "%" in linea:
            producto = lineas[i - 1]

            nums = re.findall(r"([\d.,]+)", linea)

            if len(nums) >= 4:
                cantidad = int(float(nums[0].replace(",", ".")))
                precio = float(nums[1].replace(",", "."))
                subtotal = float(nums[3].replace(",", "."))

                filas.append({
                    **datos_base,
                    "Producto": producto,
                    "Cantidad": cantidad,
                    "Unidad": "unidades",
                    "Precio Unitario": precio,
                    "Subtotal": subtotal,
                    "IVA %": 21,
                    "Total c/ IVA": subtotal,
                })

    return filas

archivos = st.file_uploader(
    "Subí uno o varios PDFs",
    type="pdf",
    accept_multiple_files=True
)

if archivos:
    todas = []

    for pdf in archivos:
        todas.extend(procesar_pdf(pdf))

    if todas:
        df = pd.DataFrame(todas)
        st.dataframe(df)

        buffer = BytesIO()
        df.to_excel(buffer, index=False, engine="openpyxl")

        st.download_button(
            "⬇️ Descargar Excel",
            buffer.getvalue(),
            "facturas.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("⚠️ No se detectaron productos.")
