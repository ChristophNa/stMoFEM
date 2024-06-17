import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
from scipy import optimize
import time
import os
import os.path
import zipfile
import pandas as pd
from scipy.optimize import curve_fit, least_squares
import sys
import gmsh
import math

import matplotlib.image as mpimg
import re

import pyvista as pv
import ipywidgets as widgets
pv.set_plot_theme("document")

plt.rcParams['figure.figsize'] = [12, 9]
plt.rcParams['figure.dpi'] = 300
plt.rcParams['font.family'] = "Serif"
plt.rcParams['font.size'] = 15

from pyvirtualdisplay import Display
display = Display(backend="xvfb", visible=False, size=(1024, 768))
display.start()
    
user_name=!whoami # get user name
user_name=user_name[0]
um_view = "$HOME/um_view"

# new executables
mixed_exe = um_view + "/*eshelbian_*/ep"
standard_exe = um_view + "/tutorials/vec-2/nonlinear_elastic"

class AttrDict(dict):
    def __getattr__(self, attr):
        if attr in self:
            return self[attr]
        raise AttributeError(f"'AttrDict' object has no attribute '{attr}'")

# generation of a config file - what attributes should the blocksets have
def generate_config(params):
    # Open the file for writing
    with open(params.config_file, 'w') as f:
        # FIX_ALL boundary condition (do not change)
        data = ['[SET_ATTR_FIX_ALL]', 'number_of_attributes=3', 'user1=0', 'user2=0', 'user3=0']
        # Use a for loop to write each line of data to the file
        for line in data:
            f.write(line + '\n')
            # print the data as it is written to the file
            print(line)
        # FORCE_1 boundary condition (change in params bellow)
        data = ['[SET_ATTR_FORCE_1]', 'number_of_attributes=3', 'user1='+str(params.force_x), 
                'user2='+str(params.force_y), 'user3='+str(params.force_z)]
        # Use a for loop to write each line of data to the file
        for line in data:
            f.write(line + '\n')
            # print the data as it is written to the file
            print(line)

# gmsh creation of a 3D beam + visualisation of it
def generate_mesh_box(params):
    if (params.length_x+params.length_y+params.length_z)/params.element_size > 600:
        raise Exception("Not more than 200 elements per side should be used in this tutorial")
    
    # Initialize gmsh
    gmsh.initialize()
    gmsh.option.setNumber("General.Verbosity", 3)

    box1 = gmsh.model.occ.add_box(0, 0, 0, params.length_x, params.length_y, params.length_z)

    # Create the relevant Gmsh data structures from Gmsh model.
    gmsh.model.occ.synchronize()

    # ensuring a structured mesh with required element size 
    for n in [0,2,4,6]:
        N = int(params.length_z / params.element_size) + 1
        gmsh.model.mesh.setTransfiniteCurve(n+1, N,'Progression', 1.0)
    for n in [1,3,5,7]:
        N = int(params.length_y / params.element_size) + 1
        gmsh.model.mesh.setTransfiniteCurve(n+1, N,'Progression', 1.0)
    for n in [8,9,10,11]:
        N = int(params.length_x / params.element_size) + 1
        gmsh.model.mesh.setTransfiniteCurve(n+1, N,'Progression', 1.0)

    for n in range(len(gmsh.model.getEntities(2))):
        gmsh.model.mesh.setTransfiniteSurface(n+1)

    gmsh.model.mesh.setTransfiniteVolume(1)

    # gmsh.model.addPhysicalGroup(dimention, [number of element], name="name")
    gmsh.model.addPhysicalGroup(3, [box1], name="DOMAIN")
    gmsh.model.addPhysicalGroup(2, [1], name="FIX_ALL")
    gmsh.model.addPhysicalGroup(2, [2], name="FORCE_1")

    # generate a 3D mesh
    gmsh.model.mesh.generate(3)
    
    # save as a .med file
    med_file = params.mesh_file + ".med"
    gmsh.write(med_file)
    
    # close gmsh
    gmsh.finalize()
    
    # translate .med file to a format readable by MoFEM and assign values to physical groups
    h5m_file=params.mesh_file + ".h5m"    
    !read_med -med_file {med_file} -output_file {h5m_file} -meshsets_config {params.config_file} -log_sl error
    
    # visualise the mesh
    if params.show_mesh:
        vtk_file=params.mesh_file + ".vtk"
        !mbconvert {h5m_file} {vtk_file}

        mesh = pv.read(vtk_file)
        mesh = mesh.shrink(0.98)

        p = pv.Plotter(notebook=True)
        p.add_mesh(mesh, smooth_shading=False)

        p.camera_position = "xy"
        p.show(jupyter_backend='ipygany')
    
    return

# looking through the output for norms and other phrases 
def parse_log_file(params):
    res = AttrDict()
    with open(params.log_file, "r") as log_file:
        for line in log_file:
            line = line.strip()
            if "nb global dofs" in line:
                res.elem_num = int(line.split()[13])
            if "norm_u: " in line:
                res.norm_u = float(line.split()[4])
            if "norm_piola: " in line:
                res.norm_piola = float(line.split()[4])
            if "norm_u_h1: " in line:
                res.norm_u_h1 = float(line.split()[4])
            if "norm_error_u_l2: " in line:
                res.norm_error_u_l2 = float(line.split()[4])
    return res

# running MoFEM executable
def run_mofem(exe, params):
    if params.order > 5:
        raise Exception("Approximation order greater than 5 should not be used in this tutorial")
    if params.nproc > 4:
        raise Exception("Not more than 4 processors should be used in this tutorial")
    
    # define name of the mesh file
    params.part_file = params.mesh_file + "_" + str(params.nproc) + "p.h5m"
    
    # partition the mesh
    !{um_view}/bin/mofem_part \
    -my_file {params.mesh_file}.h5m \
    -my_nparts {params.nproc} -output_file {params.part_file} 
    
    # run the chosen MoFEM executable
    !export OMPI_MCA_btl_vader_single_copy_mechanism=none && \
    nice -n 10 mpirun --oversubscribe --allow-run-as-root \
    -np {params.nproc} {exe} \
    -file_name {params.part_file} \
    -my_file {params.part_file} \
    -order {params.order} \
    -space_order {params.order + 1} \
    -hencky_young_modulus {params.young_modulus} \
    -hencky_poisson_ratio {params.poisson_ratio} \
    -rotations {params.rotations} \
    -stretches {params.stretches} \
    2>&1 | tee {params.log_file}
    
    # convert results to vtk if desired
    if params.convert_result:
        !convert.py -np {params.nproc} out*
    
    # return results found by parse_log_file
    return parse_log_file(params)

# showing results of vtks
def show_results(params):
    out_to_vtk = !ls -c1 {params.show_file}*vtk
    last_file=out_to_vtk[0]

    mesh = pv.read(last_file[:-3] + "vtk")
    if params.warp_field:
        mesh = mesh.warp_by_vector(vectors=params.warp_field, factor=params.warp_factor)

    if params.show_edges:
        mesh=mesh.shrink(0.95)
    
    jupyter_backend='ipygany'
    cmap = "turbo"

    p = pv.Plotter(notebook=True)
    p.add_mesh(mesh, scalars=params.show_field, component=None, smooth_shading=True, cmap=cmap)
    p.camera_position = "xy"
    
    p.enable_parallel_projection()
    p.enable_image_style()
    
    p.show(jupyter_backend=jupyter_backend)


params = AttrDict() # Attribute dictionary for storing the parameters

# Pre-processing parameters
params.mesh_file = "beam_box"
params.length_x = 10
params.length_y = 1
params.length_z = 1
params.element_size = 0.3 # element size in the regular mesh
params.show_mesh = True

# boundary condition configuration
params.config_file = "bc.cfg"
params.force_x = 0.
params.force_y = -1.
params.force_z = 0.

# material parameters
params.young_modulus = 100.
params.poisson_ratio = 0.

# solution parameters
params.log_file = "log" # log file name 
params.nproc = 2
params.order = 2 # approximation order for displacements

# post-processing defaults
params.warp_field = ""
params.warp_factor = 1

# parameters for mixed formulation
params.rotations = "small" # choose from: small, medium, large
params.stretches = "linear" # choose from: linear, log

params.show_mesh = True
generate_config(params)
generate_mesh_box(params)

!rm -rf out*                      # remove previous analysis output files
params.convert_result = True      # convert the results to vtk for visualisation
params.order = 2                  # set approximation order
run_mofem(standard_exe, params)   # run analysis

params.order = 1
run_mofem(mixed_exe, params)