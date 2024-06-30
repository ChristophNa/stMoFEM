import streamlit as st
import extra_streamlit_components as stx
import pyvista as pv
from stpyvista import stpyvista
pv.start_xvfb()
# st.title("Test: File reader")

# def readFile():
#     try:
#         with open("hello.txt", "r") as f:
#             return f.read()
#     except:
#         return "Could not read file"


# if st.button("refresh"):
#     st.write(readFile())



chosen_id = stx.tab_bar(data=[
    stx.TabBarItemData(id="Geometry", title="Geometry", description="Define the dimensions of the cantilever"),
    stx.TabBarItemData(id="Loads", title="Loads and material", description="Define the loads and material of the cantilever"),
    stx.TabBarItemData(id="Settings", title="Solver settings", description="Expert settings for the solver"),], default="Geometry")

st.write(chosen_id)

if chosen_id == "Geometry":
    ## Initialize a plotter object
    plotter = pv.Plotter(window_size=[400,400])

    ## Create a mesh with a cube 
    mesh = pv.Cube(center=(0,0,0), x_length=10., 
                   y_length=0.1, 
                   z_length=0.1)

    # Add some scalar field associated to the mesh
    mesh['myscalar'] = mesh.points[:, 2] * mesh.points[:, 0]

    # Add mesh to the plotter
    plotter.add_mesh(mesh, scalars='myscalar', cmap='bwr')
    plotter.add_mesh(mesh, show_edges=True)
    plotter.view_isometric()
    plotter.set_background('white')

    stpyvista(plotter, key="plotter")
