# Standard Library Dependencies
import os
import sys

def resource_path(file):
    """Used to get the path to a file, even if it is in a windows .exe"""
    if getattr(sys, 'frozen', None):
        basedir = sys._MEIPASS
    else:
        basedir = os.path.dirname(__file__)

    return os.path.join(basedir, file)
