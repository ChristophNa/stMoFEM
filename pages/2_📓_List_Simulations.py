from datetime import datetime
from pysondb import db
import pyvista as pv
from numpy import sqrt
import streamlit as st
st.set_page_config(layout="wide")
from stpyvista import stpyvista
import extra_streamlit_components as stx
# def setKey():
#     st.session_state["key"] = {"key": "cantilever"}

st.session_state["database"] = db.getDb("database.json")

datas = st.session_state["database"].getAll()

simList = []
for data in datas:
    simList.append({"ID": str(data["id"]), "description": data["description"], 
                    "submit time": data["submitTime"], "status": data["status"]})

st.dataframe(simList)

# TODO: this can be done with containers and images
