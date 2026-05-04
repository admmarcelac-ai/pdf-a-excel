import streamlit as st
import pandas as pd
import re
from PyPDF2 import PdfReader
from io import BytesIO

# =============================
# CONFIGURACIÓN STREAMLIT
# =============================
st.set_page_config(page_title="PDFs de Facturas a Excel", layout="wide")
st.title("📄 PDFs de Facturas → Excel único")

# =============================
# LEER PDF (SOLO HOJA 1)
# =============================
def leer_pdf(archivo):
    reader = PdfReader(archivo)
    pagina = reader.pages[0]
    texto = pagina.extract_text()
    if texto:
        return texto
    return ""

# =============================
# FUNCIÓN REGEX AUXILIAR
# =============================
def buscar(patron, texto):
    resultado = re.search(patron, texto, re.IGNORECASE | re.DOTALL)
    if resultado:
        return resultado.group(1).strip()
    return ""

# =============================
# PROCESAR UN PDF
# =============================
def procesar_pdf(pdf):
    texto = leer_pdf(pdf)

    # Mostrar texto leído (debug)
    st.text_area("Texto detectado en el PDF", texto, height=300)

    datos_base = {
        "Receptor": "SALUD METROPOLITANA SA",
        "CUIT Receptor": "30715602012",
        "Emisor": "PAPUS SRL",
        "CUIT Emisor": "30714997234",
        "Fecha": buscar(r"(\d{2}/\d{2}/\d{4})", texto),
        "Tipo": "FACTURA A",
        "Punto de Venta": buscar(r"Punto de Venta\s*(\d+)", texto),
        "Número": buscar(r"Comp\.?\s*Nro\.?\s*(\d+)", texto),
    }

    filas = []

    productos = re.findall(
        r"([A-Z0-9 /().+-]{10,120})\n.*?X\s*(\d+),\d+\s+unidades\s+([\d.,]+)\s+0,00\s+([\d.,]+)\s+21%",
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

# =============================
# SUBIDA DE ARCHIVOS
# =============================
archivos = st.file_uploader(
    "Subí uno o varios PDFs",
    type="pdf",
    accept_multiple_files=True
)

# =============================
# EJECUCIÓN PRINCIPAL
# =============================
if archivos:
    todas_las_filas = []

    for pdf in archivos:
        todas_las_filas.extend(procesar_pdf(pdf))

    if todas_las_filas:
        df = pd.DataFrame(todas_las_filas)
        st.subheader("📊 Datos extraídos")
        st.dataframe(df)

        buffer = BytesIO()
        df.to_excel(buffer, index=False, engine="openpyxl")

        st.download_button(
            label="⬇️ Descargar Excel",
            data=buffer.getvalue(),
            file_name="facturas.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("⚠️ No se detectaron productos en los PDFs.")
``
