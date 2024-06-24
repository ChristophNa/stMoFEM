import streamlit as st

st.title("Test: File reader")

def readFile():
    try:
        with open("hello.txt", "r") as f:
            return f.read()
    except:
        return "Could not read file"


if st.button("refresh"):
    st.write(readFile())
