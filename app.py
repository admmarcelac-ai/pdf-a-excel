import streamlit as st
import pandas as pd
import re
from PyPDF2 import PdfReader
from io import BytesIO

st.set_page_config(page_title="PDFs de Facturas a Excel", layout="wide")
st.title("📄 PDFs de Facturas → Excel único")

def leer_pdf(archivo):
    reader = PdfReader(archivo)
    pagina = reader.pages[0]
    texto = pagina.extract_text()
    return texto if texto else ""

def buscar(patron, texto):
    m = re.search(patron, texto, re.IGNORECASE | re.DOTALL)
    return m.group(1).strip() if m else ""

def procesar_pdf(pdf):
    texto = leer_pdf(pdf)

    st.text_area("Texto detectado en el PDF", texto, height=300)

    datos_base = {
        "Receptor": "SALUD METROPOLITANA SA",
        "CUIT Receptor": "30715602012",
        "Emisor": "PAPUS SRL",
        "CUIT Emisor": "30714997234",
        "Fecha": buscar(r"(\\d{2}/\\d{2}/\\d{4})", texto),
        "Tipo": "FACTURA A",
        "Punto de Venta": buscar(r"Punto de Venta\\s*(\\d+)", texto),
        "Número": buscar(r"Comp\\.?\\s*Nro\\.?\\s*(\\d+)", texto),
    }

    filas = []

    productos = re.findall(
        r"([A-Z0-9 /().+-]{10,120})\\n.*?X\\s*(\\d+),\\d+\\s+unidades\\s+([\\d.,]+)\\s+0,00\\s+([\\d.,]+)\\s+21%",
        texto,
        re.DOTALL
    )

    for prod in productos:
        filas.append({
            "Receptor": datos_base["Receptor"],
            "CUIT Receptor": datos_base["CUIT Receptor"],
            "Emisor": datos_base["Emisor"],
            "CUIT Emisor": datos_base["CUIT Emisor"],
            "Fecha": datos_base["Fecha"],
            "Tipo": datos_base["Tipo"],
            "Punto de Venta": datos_base["Punto de Venta"],
            "Número": datos_base["Número"],
            "Producto": prod[0].strip(),
            "Cantidad": int(prod[1]),
            "Unidad": "unidades",
            "Precio Unitario": float(prod[2].replace(",", ".")),
            "Subtotal": float(prod[3].replace(",", ".")),
            "IVA %": 21,
            "Total c/ IVA": float(prod[3].replace(",", ".")),
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
        st.warning("No se detectaron productos.")
