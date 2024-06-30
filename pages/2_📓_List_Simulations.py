from datetime import datetime
from pysondb import db
import pyvista as pv
from numpy import sqrt
import streamlit as st
st.set_page_config(layout="wide")
from stpyvista import stpyvista
import extra_streamlit_components as stx
from pathlib import Path
# def setKey():
#     st.session_state["key"] = {"key": "cantilever"}

@st.cache_data()
def getBaseDir():
    baseDir = Path("simulations/user/")
    baseDir.mkdir(parents=True, exist_ok=True)
    return baseDir

baseDir = getBaseDir()

st.session_state["database"] = db.getDb("simulations/user/database.json")

datas = st.session_state["database"].getAll()

simList = []
for data in datas:
    simList.append({"ID": str(data["id"]), "description": data["description"], 
                    "submit time": data["submitTime"], "status": data["status"]})

st.dataframe(simList)

# TODO: this can be done with containers and images
