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
        "Fecha": buscar(r"(\d{2}/\d{2}/\d{4})", texto),
        "Tipo": "FACTURA A",
        "Punto de Venta": "0020",
        "Número": buscar(r"(\d{8})", texto),
    }

    filas = []
    descripcion = []

    lineas = [l.strip() for l in texto.split("\n") if l.strip()]

    for linea in lineas:
        # Acumulamos descripción
        if "unidades" not in linea or "%" not in linea:
            descripcion.append(linea)
            continue

        # ===== LÍNEA DE DETALLE =====

        # Cantidad (X 48,00)
        m_cant = re.search(r"X\s*(\d+),", linea)
        cantidad = int(m_cant.group(1)) if m_cant else 0

        # Todos los importes numéricos
        nums = re.findall(r"\d+,\d+", linea)

        # Validación de seguridad
        if len(nums) < 3:
            descripcion = []
            continue

        # Precio unitario = primer importe después de unidades
        precio_unit = float(nums[1].replace(",", "."))

        # Subtotal sin IVA = penúltimo
        subtotal = float(nums[-2].replace(",", "."))

        # Total con IVA = último
        total = float(nums[-1].replace(",", "."))

        filas.append({
            **datos_base,
            "Producto": " ".join(descripcion),
            "Cantidad": cantidad,
            "Unidad": "unidades",
            "Precio Unitario": precio_unit,
            "Subtotal": subtotal,
            "IVA %": 21,
            "Total c/ IVA": total,
        })

        descripcion = []

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
