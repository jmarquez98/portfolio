import pandas as pd



import sys
import pathlib
path = str(pathlib.Path(__file__).parent.absolute())


sys.path.insert(1, path+"/../bonds")
import funciones.download_functions as df


sys.path.insert(1, path+"/../database")
from db_connection import db
import load_info as li
import store_info as sidb
