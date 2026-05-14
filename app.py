import streamlit as st
from PyPDF2 import PdfReader
import re

st.title("PDF a Excel")

archivo = st.file_uploader("Subí un PDF", type="pdf")

if archivo:
    reader = PdfReader(archivo)
    texto = reader.pages[0].extract_text()

    st.text_area("Texto detectado", texto, height=300)

    lineas = texto.split("\n")

   buffer_descripcion = []

for linea in lineas:
    linea = linea.strip()

    # ✅ Detecta SOLO las líneas reales de detalle
    if re.search(r"^X\s*\d+,\d+\s+unidades", linea):

        st.write("✅ LINEA CORRECTA:", linea)

        # ✅ Cantidad (X 48,00 → 48)
        m = re.search(r"X\s*(\d+),", linea)
        cantidad = int(m.group(1)) if m else 0

        # ✅ Importes
        nums = re.findall(r"\d+,\d+", linea)

        precio = float(nums[1].replace(",", ".")) if len(nums) > 1 else 0
        subtotal = float(nums[3].replace(",", ".")) if len(nums) > 3 else 0
        total = float(nums[-1].replace(",", ".")) if len(nums) > 0 else 0

        producto = " ".join(buffer_descripcion)

        st.write("📦 Producto:", producto)
        st.write("Cantidad:", cantidad)
        st.write("Precio:", precio)
        st.write("Subtotal:", subtotal)
        st.write("Total:", total)
        st.write("-----")

        buffer_descripcion = []

    else:
        buffer_descripcion.append(linea)
