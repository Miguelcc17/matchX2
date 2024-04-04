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

from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException


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

def detect_language_columns(file_path: str = None) -> dict:
    """
    Detects the language of unique values in each column of a DataFrame loaded from a file.

    Parameters:
    - file_path (str): Path of the file to load.

     Returns:
    - dict: Dictionary with language detection results for each column's unique values.
    """
    if file_path is None or len(file_path) == 0:
        raise ValueError("'file_path' cannot be empty")
    if type(file_path) != str:
        raise TypeError("data type compatible only 'str'")
    
    df = get_df(file_path)  # Assuming get_df function is defined elsewhere to get the DataFrame
    
    unique_values_by_column = df.apply(lambda col: col.astype(str).unique())
    
    def detect_language_list(texts):
        full_text = ' '.join(texts)
        try:
            language = detect(full_text)
            return language
        except LangDetectException:
            return 'Unknown'

    # Convert DataFrame to dictionary
    language_dict = unique_values_by_column.apply(detect_language_list).to_dict()

    return language_dict

def detect_language_file(file_path: str = None) -> str:
    """
    Detects the language of a CSV file given its path.

    Parameters:
    - path (str): The path of the CSV file to process.

    Returns:
    - str: A message indicating the detected language in the CSV file.
    
    Raises:
    - ValueError: If 'path' is None or an empty string.
    - TypeError: If the type of 'path' is not str.

    Example:
    >>> detect_language_file('path/to/file.csv')
    'The detected language in the CSV is: en'
    """
    if file_path is None or len(file_path) == 0:
        raise ValueError("'path' cannot be empty")
    if type(file_path) != str:
        raise TypeError("data type compatible only 'str'")
    
    # Get the DataFrame from the CSV file
    df = get_df(file_path)

    # Combine the text of all rows into a single text
    text_combined = ' '.join(df.apply(lambda row: ' '.join(row.astype(str)), axis=1))

    try:
        # Detect the language of the combined text
        language = detect(text_combined)
        return f"The detected language in the CSV is: {language}"
    except LangDetectException as e:
        print("Error detecting language:", e)