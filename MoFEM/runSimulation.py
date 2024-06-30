import shutil
import pysondb as db
from pathlib import Path
import subprocess
import gmsh
from convert import convert
from time import sleep
import logging
import sys
sys.path.append("um_view/bin")

logging.basicConfig(filename='logSimulation.txt', level=logging.DEBUG)

# generation of a config file - what attributes should the blocksets have
def generate_config(params, path):
    try:
        # Open the file for writing
        with open(Path(path)/"config.cfg", 'w') as f:
            # FIX_ALL boundary condition (do not change)
            data = ['[SET_ATTR_FIX_ALL]', 'number_of_attributes=3', 'user1=0', 'user2=0', 'user3=0']
            # Use a for loop to write each line of data to the file
            for line in data:
                f.write(line + '\n')
                # logging.debug the data as it is written to the file
                logging.debug(line)
            # FORCE_1 boundary condition (change in params bellow)
            data = ['[SET_ATTR_FORCE_1]', 'number_of_attributes=3', 'user1='+str(params["force_x"]), 
                    'user2='+str(params["force_y"]), 'user3='+str(params["force_z"])]
            # Use a for loop to write each line of data to the file
            for line in data:
                f.write(line + '\n')
                # logging.debug the data as it is written to the file
                logging.debug(line)
        return True
    except:
        return False


# gmsh creation of a 3D beam + visualisation of it
def generate_mesh_box(params, path):
    try:
        binPath = Path("um_view/bin/")
        if (params["length_x"]+params["length_y"]+params["length_z"])/params["element_size"] > 600:
            raise Exception("Not more than 200 elements per side should be used in this tutorial")
        
        # Initialize gmsh
        gmsh.initialize()
        gmsh.option.setNumber("General.Verbosity", 3)

        box1 = gmsh.model.occ.add_box(0, 0, 0, params["length_x"], params["length_y"], params["length_z"])

        # Create the relevant Gmsh data structures from Gmsh model.
        gmsh.model.occ.synchronize()

        # ensuring a structured mesh with required element size 
        for n in [0,2,4,6]:
            N = int(params["length_z"] / params["element_size"]) + 1
            gmsh.model.mesh.setTransfiniteCurve(n+1, N,'Progression', 1.0)
        for n in [1,3,5,7]:
            N = int(params["length_y"] / params["element_size"]) + 1
            gmsh.model.mesh.setTransfiniteCurve(n+1, N,'Progression', 1.0)
        for n in [8,9,10,11]:
            N = int(params["length_x"] / params["element_size"]) + 1
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
        gmsh.write(str((Path(path)/"mesh.med").resolve()))
        
        # close gmsh
        gmsh.finalize()
        
        # translate .med file to a format readable by MoFEM and assign values to physical groups
        h5m_file=Path(path)/"mesh.h5m"
        subprocess.run([binPath/"read_med", "-med_file", Path(path)/"mesh.med", "-output_file", Path(path)/"mesh.h5m", 
                    "-meshsets_config", Path(path)/"config.cfg", "-log_sl", "error"])
        vtk_file= Path(path)/"mesh.vtk"
        subprocess.run([binPath/"mbconvert", h5m_file, vtk_file])
        return True
    except Exception as e:
        logging.debug(e)
        return False
    # TODO: visualise the mesh
    # if params.show_mesh:
    #     vtk_file=file_name + ".vtk"
    #     subprocess.run(["mbconvert", h5m_file, vtk_file])

    #     mesh = pv.read(vtk_file)
    #     mesh = mesh.shrink(0.98)

    #     p = pv.Plotter(notebook=True)
    #     p.add_mesh(mesh, smooth_shading=False)

    #     p.camera_position = "xy"
    #     p.show(jupyter_backend='ipygany')
    # return

def parse_log_file(log_file):
    res = {}
    with open(log_file, "r") as lf:
        for line in lf:
            line = line.strip()
            if "nb global dofs" in line:
                res["elem_num"] = int(line.split()[13])
            if "norm_u: " in line:
                res["norm_u"] = float(line.split()[4])
            if "norm_piola: " in line:
                res["norm_piola"] = float(line.split()[4])
            if "norm_u_h1: " in line:
                res["norm_u_h1"] = float(line.split()[4])
            if "norm_error_u_l2: " in line:
                res["norm_error_u_l2"] = float(line.split()[4])
    return res

# running MoFEM executable
def run_mofem(params, path):

    # define name of the mesh file
    part_file = Path(path)/("mesh" + f'_{params["nproc"]}p.h5m')
    log_file = Path(path)/"MoFEM.log"
    binPath = Path("um_view/bin/")
    
    # partition the mesh
    subprocess.run([binPath/"mofem_part", "-my_file", Path(path)/"mesh.h5m", "-my_nparts", str(params["nproc"]), "-output_file", part_file])
    
    # choose MoFEM executable
    um_view = "/mofem_install/um_view"
    exes = {"Mixed": um_view + "/eshelbian_plasticty/ep", "Standard": um_view + "/tutorials/vec-2/nonlinear_elastic"}
    # copy petsc parameter file to current directory
    # shutil.copyfile(Path(exes[params["formulation"]]).parent/"param_file.petsc", Path(path)/"param_file.petsc")
    shutil.copyfile(Path("app/MoFEM")/"param_file.petsc", Path(path)/"param_file.petsc")
    with open(Path(path)/"start.sh", "w") as f:
        f.write("#!/bin/bash\n")
        f.write("export OMPI_MCA_btl_vader_single_copy_mechanism=none\n")
        
        # f.write(" ".join(["nice", "-n", "10", "mpirun", "--oversubscribe", "--allow-run-as-root",
        #             "-np", str(params["nproc"]), exes[params["formulation"]],
        #             "-file_name", str(part_file.resolve()), "-my_file", str(part_file.resolve()),
        #             "-order", str(params["order"]),
        #             "-space_order", str(params["order"] + 1),
        #             "-hencky_young_modulus", str(params["young_modulus"]),
        #             "-hencky_poisson_ratio", str(params["poisson_ratio"]),
        #             "-rotations", str(params["rotations"]),
        #             "-stretches", str(params["stretches"]),
        #             "2>&1", "|", "tee", str(log_file.resolve())]))
        f.write("cd " + str(Path(path).resolve()) + "\n")
        f.write(" ".join(["nice", "-n", "10", "mpirun", "--oversubscribe", "--allow-run-as-root",
                    "-np", str(params["nproc"]), exes[params["formulation"]],
                    "-file_name", "mesh" + f'_{params["nproc"]}p.h5m', "-my_file", "mesh" + f'_{params["nproc"]}p.h5m',
                    "-order", str(params["order"]),
                    "-space_order", str(params["order"] + 1),
                    "-hencky_young_modulus", str(params["young_modulus"]),
                    "-hencky_poisson_ratio", str(params["poisson_ratio"]),
                    "-rotations", str(params["rotations"]),
                    "-stretches", str(params["stretches"]),
                    "2>&1", "|", "tee", "MoFEM.log"]))
    subprocess.run(["chmod", "+x", Path(path)/"start.sh"])
    subprocess.run([Path(path)/"start.sh"])
    # subprocess.run(["export", "OMPI_MCA_btl_vader_single_copy_mechanism=none", "&&",
    #                 "nice", "-n", "10", "mpirun", "--oversubscribe", "--allow-run-as-root",
    #                 "-np", str(params["nproc"]), exes[params["formulation"]],
    #                 "-file_name", part_file, "-my_file", part_file,
    #                 "-order", str(params["order"]),
    #                 "-space_order", str(params["order"] + 1),
    #                 "-hencky_young_modulus", str(params["young_modulus"]),
    #                 "-hencky_poisson_ratio", str(params["poisson_ratio"]),
    #                 "-rotations", str(params["rotations"]),
    #                 "-stretches", str(params["stretches"]),
    #                 "2>&1", "|", "tee", log_file])


    # return results found by parse_log_file
    return parse_log_file(log_file)

# The workflow
if __name__=="__main__":
    # set the base path
    basePath = Path("simulations")
    basePath.mkdir(parents=True, exist_ok=True)

    
    while True:
        users = [item for item in basePath.iterdir() if item.is_dir()]
        logging.debug(users)
        for user in users:
            database = db.getDb((f"{user}/database.json"))
            for data in database.getAll():
                workDir = Path(user)/str(data["id"])
                if data["status"] == "started":
                    try:
                        workDir.mkdir(parents=True, exist_ok=True)
                        database.updateById(data["id"],{"status":"Created workDir"})
                        data = database.getById(data["id"])
                        logging.debug("created workdir")
                    except Exception as e:
                        logging.debug(e)
                        data["status"] == "Failed"
                        database.updateById(data["id"],{"status":"Failed"})
                        data = database.getById(data["id"])
                if data["status"] == "Created workDir":
                    if generate_config(data["params"], workDir):
                        database.updateById(data["id"],{"status":"Generated config"})
                        data = database.getById(data["id"])
                        logging.debug("Generated config")
                    else:
                        logging.debug("Failed generating config")
                        database.updateById(data["id"],{"status":"Failed"})
                        data = database.getById(data["id"])
                if data["status"] == "Generated config":
                    if generate_mesh_box(data["params"], str(workDir.resolve())):
                        database.updateById(data["id"],{"status":"Generated mesh"})
                        data = database.getById(data["id"])
                        logging.debug("Generated mesh")
                    else:
                        data["status"] == "Failed"
                        database.updateById(data["id"],{"status":"Failed"})
                        data = database.getById(data["id"])
                if data["status"] == "Generated mesh":
                    try:
                        run_mofem(data["params"], workDir)
                        database.updateById(data["id"],{"status":"Simulated"})
                        data = database.getById(data["id"])
                        logging.debug("Simulated")
                    except Exception as e:
                        logging.debug(e)
                        data["status"] == "Failed"
                        database.updateById(data["id"],{"status":"Failed"})
                        data = database.getById(data["id"])
                if data["status"] == "Simulated":
                    # convert results to vtk
                    try:
                        convert(files=list(workDir.glob('out*')), np=data["params"]["nproc"], log_file=Path(workDir)/"convert.log")
                        logging.debug("Finished")
                        database.updateById(data["id"],{"status":"Finished"})
                        data = database.getById(data["id"])
                    except Exception as e:
                        logging.debug(e)
                        database.updateById(data["id"],{"status":"Failed"})
                        data = database.getById(data["id"])
        logging.debug("waiting for 10 s")
        sleep(10)