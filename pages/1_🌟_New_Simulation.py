import pyvista as pv
import streamlit as st
from stpyvista import stpyvista

st.write("""# Define a simulation - Cantilever beam
## Geometry
Please set the dimensions of the cantilever""")

# add the slider widgets for the geometry
length = st.slider("Length", min_value=1.0, max_value=10.0, value=5.0)
width = st.slider("Width", min_value=0.1, max_value=1.0, value=0.2)
depth = st.slider("Depth", min_value=0.1, max_value=1.0, value=0.2)

## Initialize a plotter object
plotter = pv.Plotter(window_size=[400,400])

## Create a mesh with a cube 
mesh = pv.Cube(center=(0,0,0), x_length=length, y_length=width, z_length=depth)

## Add some scalar field associated to the mesh
# mesh['myscalar'] = mesh.points[:, 2] * mesh.points[:, 0]

## Add mesh to the plotter
#plotter.add_mesh(mesh, scalars='myscalar', cmap='bwr')
plotter.add_mesh(mesh, show_edges=True)
## Final touches
plotter.view_isometric()
plotter.set_background('white')

## Send to streamlit
stpyvista(plotter, panel_kwargs=dict(
        orientation_widget=True,
        interactive_orientation_widget=True)
        )
# TODO: try to isolate this as otherwise pyvista always reloads
st.write("""## Loads
Please define the load at the end of the cantilever:
remark: the x-direction is the length-direction of the beam""")

traction = [0.0]*3
traction[0] = st.number_input("traction in x", value=1.0)
traction[1] = st.number_input("traction in y", value=0.0)
traction[2] = st.number_input("traction in z", value=0.0)
