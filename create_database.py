# -*- coding: utf-8 -*-
# Programa que genera una base de datos SQLite a partir de
# ficheros de datos.
# Autor: César Husillos (versión 2, 11 Mayo 2020) 

import argparse
from datetime import datetime
import os
import glob
import re
from datetime import datetime

# import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.dates as mdates

import sqlite3

def db_creation(db_file, overwrite=False):
    """Crea la base de datos SQLite en la ruta dada por 'db_file'.
    La base de datos puede generarse de nuevo si el parámetro 
    'overwrite' es True.
    
    Args:
        db_file (str): ruta al fichero que contendrá la base de
            datos SQLite.
        overwrite (bool): si es True, se borra y se genera de 
            nuevo la base de datos con la tabla 'measurement'.
    
    Returns: 
        (int): 0, si la creación de la base de datos fue exitosa.
    """
    create = False

    if os.path.exists(db_file): # database exists
        if overwrite:
            create = True
        else: 
            print("INFO: Database exists previously. Nothing done!")
    else:
        create = True
    
    if create:
        conn = sqlite3.connect(db_file)
        c = conn.cursor()

        print(f"INFO: Creating '{db_file}' SQLite database.")
        # Create table measurement
        c.execute('''CREATE TABLE measurement
                    ([datetime_obs] INTEGER, 
                    [is_moon] INTEGER, 
                    [photo_night] REAL, 
                    [sky_bright] REAL, 
                    [position] INTEGER, 
                    [filter_name] TEXT)''')
        conn.commit()

    return 0

def fix_file(file_path):
    """Procesa el fichero de entrada 'file_path'.
    
    Si hay líneas que no verifican el patrón esperado
        01/05/2020 03:02:05      0      0.819527      20.402396
    se ignoran. En ese caso se genera un fichero con las líneas
    válidas y el orginal se copia un fichero con el mismo
    nombre que el original pero con sufijo '.ori'.
    
    Args:
        file_path (str): Ruta al fichero de datos.
        
    Returns:
        (int): 0, si el procesado se realizó con éxito.
               1, si la ruta al fichero de datos no es correcta.
    """
    if not os.path.isfile(file_path):
        return 1

    lines = [l for l in open(file_path).read().split('\n') if len(l) > 0]
    good_lines = []
    bad_lines = False
    # good line example: 
    # 01/05/2020 03:02:05      0      0.819527      20.402396
    for l in lines:
        value = re.findall(r'(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2}\s+\d\s+\d.\d+\s+\d+.\d+)', l)
        if len(value):
            good_lines.append(value[0])
        else:
            bad_lines = True
            print(f"\tWARNING: Bad line '{l}'")
    if bad_lines:
        new_name = file_path.replace('.dat', '.dat.ori')
        os.rename(file_path, new_name)
        with open(file_path, 'w') as fout:
            fout.write('\n'.join(good_lines))

    return 0

def proc_file(file_path):
    """Lee el fichero "file_path" y procesa sólo las líneas que
    verfican el patrón de campos válido. Agrega al pandas.dataframe
    de salida los campos "position" y "filter", necesarios para
    el análisis de la información.
    
    Args:
        file_path (str): ruta al fichero de datos.
        
    Returns:
        (pandas.dataframe): con los campos 
            ['date', 'time', 'is_moon', 'photo_night', 'sky_bright',
            'position', 'filter', 'datetime']
            siendo este último la combinación de los dos primeros.

            Devuelve None si la ruta al fichero de datos no es correcta.
    """
    # file_path example pattern: abr2020pos2_V.dat
    values = re.findall(r'/(\w{3})(\d{4})pos(\d{1})_(\w{1}).dat', file_path)
    if not len(values):
        print(f"WARNING: Non valid file data '{file_path}'")
        return None
    # Fixed field with format file
    data = pd.read_fwf(file_path, header=None, \
        names=['date', 'time', 'is_moon', 'photo_night', 'sky_bright'], \
        index_col=False)
    # combining two columns
    try:
        dt = data['date'] + ' ' + data['time']
    except TypeError:
        print(data.info())
        print(data.head())
        return None

    dt_size = len(dt.index)
    
    # Additional info
    data['position'] = [int(values[0][2])] * dt_size
    data['filter'] = [values[0][3]] * dt_size


    # Changing str to datetime type
    data['datetime'] = pd.to_datetime(dt, dayfirst=True)

    return data

def data2db(data, db_file):
    """
    Inserta el contenido "data" en la base de datos SQLite "db_file".
    
    Args:
        data (pandas.dataframe): dataframe con información a insertar.
        db_file (str): ruta al fichero SQLite que contiene la base de datos.
    
    Return:
        (int): 0 si la operación resultó exitosa.
    """
    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    # Create table measurement (one sentence each time)
    c.execute("BEGIN TRANSACTION;")
    sql = """INSERT INTO 
    'measurement' ('datetime_obs', 'is_moon', 'photo_night', 'sky_bright', 'position', 'filter_name') 
    VALUES
    """
    values = []
    for index, row in data.iterrows():
        str_val = f"(strftime ('%s', '{row['datetime']}'), {row['is_moon']}, {row['photo_night']}, {row['sky_bright']}, {row['position']}, '{row['filter']}')"
        values.append(str_val)
        # if index ==  2: # for testing purposes
        #     break
    sql = f"{sql} {','.join(values)};" 
    # print(sql) # Testing
    c.execute(sql)
    c.execute('COMMIT;')
    # conn.commit()

    return 0



def main():
    parser = argparse.ArgumentParser(prog='create_database.py',
                                     conflict_handler='resolve',
                                     description='''This program reads input directory files
                                     and create an sqlite database for querying info later. ''',
                                     epilog='''''')
    parser.add_argument('--version', action='version', version='%(prog)s 0.1')
    parser.add_argument("data_dir", help="Directory where data files are.")
    parser.add_argument("--output_dir",
                        action="store",
                        dest="output_dir",
                        default="./",
                        help="""Output directory where mysqlite database will 
                        be created [default: %(default)s]""")
    parser.add_argument("--overwrite",
                        action="store",
                        dest="overwrite",
                        type=bool,
                        default=False,
                        help="""It True, database is dropped, dreated and 
                        filled again [default: %(default)s]""")
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help="Show running and progress information [default: %(default)s].")
    args = parser.parse_args()

    if not os.path.isdir(args.output_dir):
        try:
            os.makedirs(args.output_dir)
        except IOError:
            print(f"ERROR: Couldn't create outpur directory '{args.output_dir}'")
            return 1
    
    ficheros_con_datos = glob.glob(os.path.join(args.data_dir, '*.dat'))
    ficheros_con_datos.sort()

    if not len(ficheros_con_datos):
        print(f"WARNING: No data files availables in '{ficheros_con_datos}'")
        return 2

    print(f"INFO: {len(ficheros_con_datos)} data files found.")
    
    # Database file
    db_file = os.path.join(args.output_dir, 'astmonDB.db')

    if args.overwrite and os.path.exists(db_file):
        # deleting previous database file
        try:
            os.remove(db_file)
        except IOError:
            print(f"ERROR: Problems deleting database file '{db_file}'")
            return 3
    
    # Database creation
    db_creation(db_file)

    # return 1

    for file_data in ficheros_con_datos:
        if fix_file(file_data):
            print(f"WARNING: Bad format for some line in file '{file_data}'.")
        # insert data file in database
        print(f"INFO: Working on data file '{file_data}'")
        dt = proc_file(file_data)
            
        if dt is not None:
            if len(dt.index) == 0:
                print(f"WARNING: Couldn't insert info from file '{file_data}' in database.")
            else:
                # insert file in database
                data2db(dt, db_file)
        # break

    return 0

if __name__ == '__main__':

    # Posibles consultas...
    # SELECT 
    #   datetime(datetime_obs, 'unixepoch'), 
    #   'is_moon', 
    #   'photo_night', 
    #   'sky_bright', 
    #   'position', 
    #   'filter_name' 
    # FROM 
    #   measurement where datetime_obs BETWEEN strftime('%s', '2020-04-04') and strftime('%s', '2020-04-06 12:00:00')

    # 
    print(main())