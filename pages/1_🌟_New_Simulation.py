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

@st.cache_resource
def getDB(path):
    return db.getDb(path)

st.session_state["database"] = getDB("database.json")

if "params" not in st.session_state:
    st.session_state["params"] = {"length_x": 5.0,"length_y": 0.2,"length_z": 0.2,
                                  "element_size": 0.3, "meshDensity": "Medium", "show_mesh": True,
                                  "force_x": 0.,"force_y": -1.,"force_z": 0.,
                                  "material": "Steel",
                                  "young_modulus": 210000.,"poisson_ratio": 0.3,
                                  "nproc": 2,"order": 2,
                                  "warp_field": "","warp_factor": 1,
                                  "formulation": "Mixed",
                                  "rotations": "small","stretches": "linear",
                                  "show_mesh": True,"convert_result": True,      # convert the results to vtk for visualisation
                                  "order": 2}                  # set approximation order
if "simDescription" not in st.session_state:
    st.session_state["simDescription"] = ""


params = st.session_state["params"].copy()

st.write("""# Define a simulation - Cantilever beam""")
# st.write([key for key in st.session_state.keys()])

chosen_id = stx.tab_bar(data=[
    stx.TabBarItemData(id="Geometry", title="Geometry", description="Define the dimensions of the cantilever"),
    stx.TabBarItemData(id="Loads", title="Loads and material", description="Define the loads and material of the cantilever"),
    stx.TabBarItemData(id="Settings", title="Solver settings", description="Expert settings for the solver"),], default="Geometry")

if chosen_id == "Geometry":
    # add the slider widgets for the geometry
    st.session_state["params"]["length_x"] = st.slider("Length", min_value=1.0, max_value=10.0, value=params["length_x"])
    st.session_state["params"]["length_y"] = st.slider("Width", min_value=0.1, max_value=1.0, value=params["length_y"])
    st.session_state["params"]["length_z"] = st.slider("Depth", min_value=0.1, max_value=1.0, value=params["length_z"])

    refresh = st.button("Refresh 3D Plot")
    # st.write(refresh)
    if refresh:
        key = {}
    else:
        key = {"key": "cantilever"}

    ## Initialize a plotter object
    plotter = pv.Plotter(window_size=[400,400])

    ## Create a mesh with a cube 
    mesh = pv.Cube(center=(0,0,0), x_length=st.session_state["params"]["length_x"], 
                   y_length=st.session_state["params"]["length_y"], 
                   z_length=st.session_state["params"]["length_z"])

    ## Add some scalar field associated to the mesh
    # mesh['myscalar'] = mesh.points[:, 2] * mesh.points[:, 0]

    ## Add mesh to the plotter
    #plotter.add_mesh(mesh, scalars='myscalar', cmap='bwr')
    plotter.add_mesh(mesh, show_edges=True)
    ## Final touches
    plotter.view_isometric()
    plotter.set_background('white')
    # key = st.session_state["key"]
    ## Send to streamlit

    stpyvista(plotter, 
              panel_kwargs=dict(orientation_widget=True,
                                interactive_orientation_widget=True), 
                                **key)

elif chosen_id == "Loads":
    st.write("## Tractions")
    st.write("remark: the x-direction is the length-direction of the beam")
    tractions = {}
    for dir in ["x", "y", "z"]:
        if f"t{dir}" not in st.session_state:
            st.session_state[f"t{dir}"] = params[f"force_{dir}"]
        st.number_input(f"traction in {dir}", step=0.1, key=f"t{dir}")
        st.session_state["params"][f"force_{dir}"] = st.session_state[f"t{dir}"]
    
    st.write("## Material")
    # add dropdow menu for material selection
    elem = {"key": "material", "Name": "Material", "args": [["Steel", "Aluminium", "Plastic", "Rubber"]], "widget": st.selectbox}
    # st.session_state["params"]["formulation"] = st.radio("Formulation", options, index=options.index(params["formulation"]))
    if elem["key"] not in st.session_state:
        st.session_state[elem["key"]] = params[elem["key"]]
    elem["widget"](elem["Name"], *elem["args"], key=elem["key"])
    st.session_state["params"][elem["key"]] = st.session_state[elem["key"]]

elif chosen_id == "Settings":
    # for val in ["formulation", "y", "z"]:
    #     if f"t{dir}" not in st.session_state:
    #         st.session_state[f"t{dir}"] = params[f"force_{dir}"]
    nElem = {"Coarse": 100.0, "Medium": 1000.0, "Fine": 10000.0, "Very Fine": 100000.0}

    elements = [{"key": "nproc", "Name": "Number of CPUs", "args": [1, 4], "widget": st.slider},
                {"key": "meshDensity", "Name": "Mesh density", "args": [[key for key in nElem.keys()]], "widget": st.select_slider},
                {"key": "order", "Name": "Approximation order", "args": [1, 5], "widget": st.slider},
                {"key": "formulation", "Name": "Finite Element Formulation", "args": [["Standard", "Mixed"]], "widget": st.radio}]
    # st.session_state["params"]["formulation"] = st.radio("Formulation", options, index=options.index(params["formulation"]))
    for elem in elements:
        if elem["key"] not in st.session_state:
            st.session_state[elem["key"]] = params[elem["key"]]
        elem["widget"](elem["Name"], *elem["args"], key=elem["key"])
        st.session_state["params"][elem["key"]] = st.session_state[elem["key"]]
    
    if st.session_state["params"]["formulation"] == "Mixed":
        elements = [{"key": "rotations", "Name": "Rotations", "args": [["small", "medium", "large"]], "widget": st.selectbox},
                    {"key": "stretches", "Name": "Stretches", "args": [["linear", "log"]], "widget": st.selectbox}]
        for elem in elements:
            if elem["key"] not in st.session_state:
                st.session_state[elem["key"]] = params[elem["key"]]
            elem["widget"](elem["Name"], *elem["args"], key=elem["key"])
            st.session_state["params"][elem["key"]] = st.session_state[elem["key"]]
    
    if "description" not in st.session_state:
        st.session_state["description"] = st.session_state["simDescription"]
    st.text_area("Description", key="description")
    st.session_state["simDescription"] = st.session_state["description"]


    # estimate the element size based on the number of elements
    volume = st.session_state["params"]["length_x"] * st.session_state["params"]["length_y"] * st.session_state["params"]["length_z"]
    st.session_state["params"]["element_size"] = ((volume)/nElem[st.session_state["params"]["meshDensity"]]*6.0*sqrt(2.0))**(1/3)
    
    

        
    # TODO: create a run button that is deactivated after clicking
    if st.button("Run simulation"):
        # TODO: create pysondb entry
        ID = st.session_state["database"].add({"params": st.session_state["params"], 
                                               "submitTime": str(datetime.now()), 
                                               "description": st.session_state["simDescription"],
                                               "status": "started"})
        # TODO: create working directory
        # TODO: create config file
        # TODO: 
        st.write(f":rocket: simulation with ID {ID} started :rocket:")

# st.write(st.session_state.params)
# if "tx" in st.session_state:
#     st.write(st.session_state.tx)
