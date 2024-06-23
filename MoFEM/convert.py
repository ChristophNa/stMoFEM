import logging
import sys
import platform
import argparse
import subprocess
from os import path
from itertools import filterfalse

import multiprocessing as mp

def print_progress(iteration, total, decimals=1, bar_length=50):
    str_format = "{0:." + str(decimals) + "f}"
    percents = str_format.format(100 * (iteration / float(total)))
    filled_length = int(round(bar_length * iteration / float(total)))
    bar = '█' * filled_length + '-' * (bar_length - filled_length)

    sys.stdout.write('\r |%s| %s%s (%s of %s)' %
                     (bar, percents, '%', str(iteration), str(total)))
    sys.stdout.flush()

def is_not_h5m(file):
    return not file.endswith('h5m')

def is_older_than_vtk(file):
    file_vtk = path.splitext(file)[0] + ".vtk"
    if path.exists(file_vtk):
        return path.getmtime(file) < path.getmtime(file_vtk)
    return False

def mb_convert(file):
    file = path.splitext(file)[0]
    p = subprocess.Popen(["mbconvert", file + ".h5m", file + ".vtk"],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (out, err) = p.communicate()
    lock.acquire()
    if p.returncode:
        logging.info('\n' + err.decode())

def init(l):
    global lock
    lock = l

def convert(files, np, log_file):
    logging.basicConfig(filename=log_file, level=logging.INFO)
    # get all files 
    file_list = list(filterfalse(is_not_h5m, files))
    if not len(file_list):
        logging.warning("No h5m files were found with the given name/mask")
        return

    file_list = list(filterfalse(is_older_than_vtk, files))
    if not len(file_list):
        logging.info("All found h5m files are older than corresponding vtk files")
        return

    l = mp.Lock()
    pool = mp.Pool(processes=np, initializer=init, initargs=(l,))

    pool.map(mb_convert, file_list)
    pool.close()
    pool.join()

    return