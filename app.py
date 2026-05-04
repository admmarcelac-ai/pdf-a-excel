import streamlit as st
import pandas as pd
import re
from PyPDF2 import PdfReader
from io import BytesIO

st.set_page_config(page_title="PDF Facturas a Excel", layout="wide")
st.title("📄 PDFs de Facturas → Excel único")

def leer_pdf(archivo):
    reader = PdfReader(archivo)
    texto = ""

    # ✅ SOLO HOJA 1 (índice 0)
    pagina = reader.pages[0]
    page_text = pagina.extract_text()

    if page_text:
        texto = page_text

    return texto.strip()

def buscar(patron, texto):
    import re
    m = re.search(patron, texto, re.IGNORECASE | re.DOTALL)
    return m.group(1).strip() if m else ""

def procesar_pdf(pdf):
    texto = leer_pdf(pdf)
    st.text_area("Texto detectado en el PDF", texto, height=300)

    datos = {
        "Receptor": "SALUD METROPOLITANA SA",
        "CUIT Receptor": "30715602012",
        "Emisor": "PAPUS SRL",
        "CUIT Emisor": "30714997234",
        "Fecha": buscar(r"(\d{2}/\d{2}/\d{4})", texto),
        "Tipo": "FACTURA A",
        "Punto de Venta": buscar(r"Punto de Venta:\s*(\d+)", texto),
        "Número": buscar(r"Comp. Nro:\s*\d+\s*(\d+)", texto),
    }

    filas = []

    productos = re.findall(
    r"(.*?)\s+X\s+(\d+[.,]\d+|\d+).*?([\d,]+).*?(0,00).*?([\d,]+)",
    texto,
    re.DOTALL
)

    for p in productos:
        filas.append({
            **datos,
            "Producto": p[0].strip(),
            "Cantidad": float(p[1].replace(",", ".")),
            "Unidad": "unidades",
            "Precio Unitario": float(p[2].replace(",", ".")),
            "Subtotal": float(p[3].replace(",", ".")),
            "IVA %": 21,
            "Total c/ IVA": float(p[4].replace(",", ".")),
        })

    return filas

archivos = st.file_uploader(
    "Subí uno o varios PDFs",
    type="pdf",
    accept_multiple_files=True
)

if archivos:
    todo = []
    for pdf in archivos:
        todo.extend(procesar_pdf(pdf))

    df = pd.DataFrame(todo)
    st.dataframe(df)

    buffer = BytesIO()
    df.to_excel(buffer, index=False, engine="openpyxl")

    st.download_button(
        "⬇️ Descargar Excel",
        buffer.getvalue(),
        "facturas.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
