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


def get_df(file_path: str = None) -> pd.DataFrame:
    """
    Load data from a file (CSV, Excel, or JSON) and return a DataFrame.

    Parameters:
    - file_path (str): Path of the file to load.

    Returns:
    - DataFrame: pandas DataFrame object.
    """
    # Get the file extension
    if file_path is None or len(file_path) == 0:
        raise ValueError("'file_path' cannot be empty")
    if type(file_path) != str:
        raise TypeError("data type compatible only 'str'")

    extension = file_path.split('.')[-1].lower()

    if extension == 'csv':
        # Detect the encoding and delimiter of the CSV file
        with open(file_path, 'rb') as f:
            result = chardet.detect(f.read())
            encoding = result['encoding']

        # Try different delimiters until finding a valid one
        possible_delimiters = [',', ';', '\t', '|']
        for delimiter in possible_delimiters:
            try:
                # Read the CSV and convert to DataFrame
                df = pd.read_csv(file_path, encoding=encoding, delimiter=delimiter)
                break  # If read successfully, exit the loop
            except pd.errors.ParserError:
                pass  # Try the next delimiter if reading fails

    elif extension == 'xlsx' or extension == 'xls':
        # Read the Excel file and convert to DataFrame
        df = pd.read_excel(file_path)

    elif extension == 'json':
        # Read the JSON file and convert to DataFrame
        # with open(file_path, 'r') as f:
        #     data = json.load(f)
        df = pd.read_json(file_path, encoding='utf-8')

    else:
        raise ValueError("Unsupported file extension. Use 'csv', 'xlsx', 'xls', or 'json'.")

    # Convert headers to lowercase
    df.columns = map(str.lower, df.columns)

    return df