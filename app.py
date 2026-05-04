import streamlit as st
import pandas as pd
import re
from PyPDF2 import PdfReader
from io import BytesIO

# =============================
# CONFIG STREAMLIT
# =============================
st.set_page_config(page_title="PDF Facturas a Excel", layout="wide")
st.title("📄 PDFs de Facturas → Excel único")

# =============================
# LEER PDF (SOLO HOJA 1)
# =============================
def leer_pdf(archivo):
    reader = PdfReader(archivo)
    pagina = reader.pages[0]
    texto = pagina.extract_text()
    return texto.strip() if texto else ""

# =============================
# BUSCAR CON REGEX
# =============================
def buscar(patron, texto):
    m = re.search(patron, texto, re.IGNORECASE | re.DOTALL)
    return m.group(1).strip() if m else ""

# =============================
# PROCESAR UN PDF
# =============================
def procesar_pdf(pdf):
    texto = leer_pdf(pdf)

    # 👉 SOLO PARA VER QUÉ LEE (después se puede sacar)
    st.text_area("Texto detectado en el PDF", texto, height=250)

    # -------------------------
    # DATOS DEL ENCABEZADO
    # -------------------------
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

    # -------------------------
    # DETALLE DE PRODUCTOS
    # -------------------------
    productos = re.findall(
        r"\n([A-Z0-9 /().+-]{10,100})\s+(\d+)\s+unidades\s+([\d.,]+)\s+0,00\s+([\d.,]+)",
        texto
    )

    for p in productos:
        filas.append({
            **datos_base,
            "Producto": p[0].strip(),
            "Cantidad": int(p[1]),
            "Unidad": "unidades",
            "Precio Unitario": float(p[2].replace(",", ".")),
            "Subtotal": float(p[3].replace(",", ".")),
            "IVA %": 21,
            "Total c/ IVA": float(p[3].replace(",", ".")),
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
# PROCESAR Y EXPORTAR
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
            "⬇️ Descargar Excel",
            buffer.getvalue(),
            "facturas.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("⚠️ No se detectaron productos en los PDFs.")
