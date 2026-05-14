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

    for linea in lineas:
        if "unidades" in linea:
            st.write("Detectado:", linea)
