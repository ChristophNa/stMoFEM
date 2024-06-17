import streamlit as st

st.set_page_config(
    page_title="MoFEM tutorial on mixed hyperelasticity",
    page_icon="🪼",
)

st.write("# Welcome to the MoFEM tutorial on mixed hyperelasticity! 👋")

st.image("http://mofem.eng.gla.ac.uk/mofem/html/mofem_logo.png")
st.markdown(
"""
[MoFEM](http://mofem.eng.gla.ac.uk/mofem/html/) is an open source [MIT license](https://en.wikipedia.org/wiki/MIT_License#Ambiguity_and_variants) C++ finite element library. It is capable of dealing with complex multi-physics problems with arbitrary levels of approximation and refinement.
"""
)