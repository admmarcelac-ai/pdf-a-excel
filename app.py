import streamlit as st
from PyPDF2 import PdfReader

st.title("PDF a Excel - Test")

archivo = st.file_uploader("Subí un PDF", type="pdf")

if archivo:
    reader = PdfReader(archivo)
    texto = reader.pages[0].extract_text()

    st.success("PDF leído correctamente")

    st.text_area("Texto detectado", texto, height=300)
