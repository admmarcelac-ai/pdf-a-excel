import streamlit as st
import pandas as pd
from PyPDF2 import PdfReader
from io import BytesIO
import re

st.set_page_config(page_title="PDFs de Facturas a Excel", layout="wide")
st.title("📄 PDFs de Facturas → Excel único")

def leer_pdf(archivo):
    reader = PdfReader(archivo)
    return reader.pages[0].extract_text() or ""

def buscar(patron, texto):
    m = re.search(patron, texto)
    return m.group(1) if m else ""

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
        "Punto de Venta": "0020",
        "Número": buscar(r"(\\d{8})", texto),
    }

    filas = []
    descripcion = []

    for linea in texto.split("\n"):
        linea = linea.strip()
        if not linea:
            continue

        if "unidades" in linea and "%" in linea:
            cant = re.search(r"X\\s*(\\d+),", linea)
            cantidad = int(cant.group(1)) if cant else 0

            nums = re.findall(r"([\\d.,]+)", linea)
            precio = float(nums[1].replace(",", ".")) if len(nums) > 1 else 0
            subtotal = float(nums[-3].replace(",", "."))
            total = float(nums[-1].replace(",", "."))

            filas.append({
                **datos_base,
                "Producto": " ".join(descripcion),
                "Cantidad": cantidad,
                "Unidad": "unidades",
                "Precio Unitario": precio,
                "Subtotal": subtotal,
                "IVA %": 21,
                "Total c/ IVA": total,
            })

            descripcion = []
        else:
            descripcion.append(linea)

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

    if todo:
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
    else:
        st.warning("No se detectaron productos.")
