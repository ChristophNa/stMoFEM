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
def getResultNames():
    return {"Standard": {"Displacement": "U", "first Piola Stress": "FIRST_PIOLA", "displacement gradient": "GRAD"},
            "Mixed": {"Displacement L2": "SpatialDisplacement", "Displacement H1": "U", "first Piola Stress": "Piola1Stress", "Error in displacements": "U_ERROR", "Cauchy stress": "CauchyStress", "Logarithmic Spatial Stress": "LogSpatialStress", "Spatial Stretch": "SpatialStretch"}}

@st.cache_data()
def getSimulations(databasePath):
    database = db.getDb(databasePath)
    return database.getAll()

@st.cache_resource()
def getDb(databasePath):
    return db.getDb(databasePath)

resultNames = getResultNames()
database = getDb("simulations/user/database.json")
simulations = getSimulations("simulations/user/database.json")
baseDir = Path("simulations/user/")



simList = []
for sim in simulations:
    # if sim["status"] == "Finished":
        simList.append(str(sim["id"]))

if len(simList) == 0:
    st.warning("No finished simulations found.")
else:
    try:
        # Create a dropdown menu to select an ID
        selected_id = st.selectbox("Select a simulation ID", simList)
        # Construct the file path and read the file
        simPath = baseDir / selected_id

        vtkFiles = list(simPath.glob('*.vtk'))
        lastFile = vtkFiles[-1]

        mesh = pv.read(lastFile)
        plotter = pv.Plotter(window_size=[400,400])
        results = resultNames[database.getById(int(selected_id))["params"]["formulation"]]
        selectedResult = st.selectbox("Select a simulation result", list(results.keys()))
        warp = st.checkbox("Show deformed configuration")
        if warp:
            factor = st.number_input("Deformation factor", min_value=0.0, value=1.0, step=1.0)
            mesh = mesh.warp_by_vector(vectors="U", factor=factor)
        plotter.add_mesh(mesh, scalars=results[selectedResult], component=None, smooth_shading=True, cmap="turbo")
        plotter.view_isometric()
        plotter.enable_image_style()
        stpyvista(plotter)
    except Exception as e:
        st.error(e)

    logFile = simPath / "MoFEM.log"
    # Check if the logfile exists
    if logFile.exists():
        with open(logFile, 'r') as f:
            logContent = f.read()
    else:
        logContent = "File not found."
    # Display the content of the file in an expander menu
    with st.expander("MoFEM logfile"):
        st.text(logContent)
