# Importación de módulos necesarios.
# ProjectEchoSyncMatcher <-----------------------------------------------------------------------------------------------------------------------
# Importa el módulo 'pandas' y lo alias como 'pd' para su uso posterior en el código.
import pandas as pd

# Importa el módulo 'numpy' y lo alias como 'np' para su uso posterior en el código.
import numpy as np

# Importa la función 'fuzz' desde el módulo 'fuzzywuzzy' para su uso posterior en el código.
from fuzzywuzzy import fuzz
import chardet

# Importa los módulos estándar 'os', 'json', 'csv' y 're' para su uso en el código.
import os
import json
import csv
import re


def get_df(archivo):
    """
    Carga datos desde un archivo (CSV, Excel o JSON) y devuelve un DataFrame.

    Parámetros:
    - archivo (str): Ruta del archivo a cargar.

    Retorna:
    - DataFrame: Objeto DataFrame de pandas.
    """
    # Obtener la extensión del archivo
    extension = archivo.split('.')[-1].lower()

    if extension == 'csv':
        # Detectar el encoding y el separador del archivo CSV
        with open(archivo, 'rb') as f:
            result = chardet.detect(f.read())
            encoding = result['encoding']

        #Intentar diferentes delimitadores hasta encontrar uno válido
        posibles_delimitadores = [',', ';', '\t', '|']
        for delimitador in posibles_delimitadores:
            try:
                # Leer el CSV y convertir a DataFrame
                df = pd.read_csv(archivo, encoding=encoding, delimiter=delimitador)
                break  # Si se lee correctamente, salir del bucle
            except pd.errors.ParserError:
                pass  # Intentar con el siguiente delimitador si falla la lectura

    elif extension == 'xlsx' or extension == 'xls':
        # Leer el archivo Excel y convertir a DataFrame
        df = pd.read_excel(archivo)

    elif extension == 'json':
        # Leer el archivo JSON y convertir a DataFrame
        # with open(archivo, 'r') as f:
        #     data = json.load(f)
        df = pd.read_json(archivo, encoding='utf-8')

    else:
        raise ValueError("Extensión de archivo no compatible. Use 'csv', 'xlsx', 'xls' o 'json'.")

    # Convertir los encabezados a minúsculas
    df.columns = map(str.lower, df.columns)


    return df
