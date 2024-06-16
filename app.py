import streamlit as st

st.title("Hello World")

data = st.data_editor({"name": "Christoph", "age": 39})

st.write(data)