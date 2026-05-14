import streamlit as st

st.title("TEST APP")

st.write("Si ves esto, la app funciona")

archivo = st.file_uploader("Subí un PDF", type="pdf")

if archivo:
    st.success("Archivo cargado correctamente")
