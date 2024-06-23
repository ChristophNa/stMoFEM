import streamlit as st

st.title("Hello World")

data = st.data_editor({"name": "John", "age": 25})

st.write(data)