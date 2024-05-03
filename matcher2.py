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


# # Abre el archivo JSON 'rules.json' en modo de lectura ('r') y lo carga en la variable 'config'.
# with open('rules/rules.json', 'r') as file:
#     config = json.load(file)

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
            print(encoding)

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
        with open(archivo, 'r', encoding='utf-8') as f:
            data = json.load(f)
        df = pd.DataFrame(data)

    else:
        raise ValueError("Extensión de archivo no compatible. Use 'csv', 'xlsx', 'xls' o 'json'.")

    # Convertir los encabezados a minúsculas
    df.columns = map(str.lower, df.columns)


    return df



# functions matchers


def harmony_datum_matcher(pathFiles: str = None, query: list = None, strict: int = 0, precision: int = 80, with_out_duplicates: int = 0):
    """
    Performs data matching based on a query within a specified folder.

    Parameters:
    - pathFiles (str): Path to the folder containing data files.
    - query (list): List containing the query for matching.
    - strict (int): Strict matching indicator. If 1, returns unique matches.
    - precision (int): Matching precision threshold (between 0 and 100).
    - with_out_duplicates (int): Duplicates handling indicator. If 1, handles duplicates; otherwise, does not.

    Exceptions:
    - ValueError: Raised when invalid arguments are provided.

    Returns:
    - None: The result is stored in files within the specified folder.
    """
    # Input validations
    if pathFiles is None or type(pathFiles) != str:
        raise ValueError('A valid value for "pathFiles" is required.')
    if not os.path.exists(pathFiles) or not os.path.isdir(pathFiles):
        raise ValueError(f'The folder at path "{pathFiles}" does not exist or is not a valid folder.')
    
    if query is None or type(query) != list:
        raise ValueError('A valid value for "query" is required.')
    if len(query) < 2:
        if len(query) == 1:
            if len(query[0]) < 2:
                raise ValueError(f"The query {query[0]} does not have two elements.")
            else:
                formatted_columns = []
                for column in query[0]:
                    formatted_columns.append(column)
                query = formatted_columns
        else:
            raise ValueError(f"The query {query} does not have two elements.")
    else:
        for i, pair in enumerate(query):
            if type(pair) != list:
                query = query
                if len(query) < 2:
                    raise ValueError(f"The query {query} does not have two elements.")
            else:
                if len(pair) != 2:
                    raise ValueError(f"The query {query[i]} does not have two elements.")

    if type(precision) != int:
        raise ValueError('A valid value for "precision" is required.') 
    if not 0 <= precision <= 100:
        raise ValueError(f'The value {precision} is outside the range of 0 to 100.')
    
    if not with_out_duplicates in [0, 1] or type(with_out_duplicates) != int:
        raise ValueError('A valid value for "with_out_duplicates" is required.')
    
    def exists_file(folder_path: str = None, file_name: str = None):
        """
        Checks if a file exists in the specified folder path with various possible extensions.

        Parameters:
        - folder_path (str): The path to the folder where the file is expected to be.
        - file_name (str): The name of the file without extension.

        Returns:
        - str: The full path of the existing file with the first found extension (.json, .csv, .xlsx, .xls).

        Raises:
        - ValueError: If folder_path is None or not a valid string, or if file_name is None or not a valid string.
        - FileNotFoundError: If the file with any of the supported extensions is not found.
        """
        # Validate input parameters
        if folder_path is None or type(folder_path) != str:
            raise ValueError('A valid value for "folder_path" is required.')

        if file_name is None or type(file_name) != str:
            raise ValueError('A valid value for "file_name" is required.')

        # Combine folder_path and file_name to form the original file path
        file_path = os.path.join(folder_path, file_name)

        # Flag to track whether the file with any extension exists
        not_exist = 0

        # Check for the existence of the file with different extensions
        for extension in ['.json', '.csv', '.xlsx', '.xls']:
            if os.path.exists(file_path + extension):
                not_exist = 1
                return file_path + extension

        # Raise FileNotFoundError if none of the extensions were found
        if not_exist == 0:
            raise FileNotFoundError(f'File does not exist: {file_name}')
    
    def harmonize_series(data_frame: pd.DataFrame = None, target_field: str = None):
        """
        Harmonizes a specific column in a DataFrame by converting it to a string.

        Parameters:
        - data_frame (pd.DataFrame): The DataFrame containing the target field.
        - target_field (str): The name of the field to be harmonized.

        Returns:
        - pd.Series: A new Series representing the harmonized field as strings.

        Raises:
        - ValueError: If data_frame is None or not a valid pandas DataFrame,
                    or if target_field is None or not a valid string.
        """

        # Validate input parameters
        if data_frame is None or type(data_frame) != pd.DataFrame:
            raise ValueError('A valid value for "data_frame" is required.')

        if target_field is None or type(target_field) != str:
            raise ValueError('A valid value for "target_field" is required.')

        # Harmonize the specified field by converting it to a string
        harmonized_series = data_frame[target_field.lower()].astype('str')

        return harmonized_series

    def harmonize_index_match(df_origin: pd.DataFrame = None, df_alternative: pd.DataFrame = None, query: list = None, strict: int = None, precision: int = precision):
        """
        Harmonizes indices between two DataFrames based on a specified query.

        Parameters:
        - df_origin (pd.DataFrame): Original DataFrame.
        - df_alternative (pd.DataFrame): Alternative DataFrame.
        - query (list): List containing two column names for harmonization.
        - strict (int): Flag for strict matching. If 1, returns unique matches.
        - precision (int): Matching precision threshold (0 to 100).

        Returns:
        - np.ndarray or list: Matched indices between the two DataFrames.
        """

        # Validate input parameters
        if df_origin is None or type(df_origin) != pd.DataFrame:
            raise ValueError('A valid value for "df_origin" is required.')
        if df_alternative is None or type(df_alternative) != pd.DataFrame:
            raise ValueError('A valid value for "df_alternative" is required.')
        # if not 0 <= precision <= 100:
        #     raise ValueError(f'The value {precision} is out of the range 0 to 100.')

        # Obtain series from specified columns in the original and alternative DataFrames
        series_origin = harmonize_series(df_origin, query[0])
        series_alternative = harmonize_series(df_alternative, query[1])

        # Initialize a list to store matched indices
        index_data_match = []

        # Iterate over indices and check for matches based on fuzzy matching
        for index_row_origin in series_origin.index:
            for index_row_alternative in series_alternative.index:
                if fuzz.ratio(series_origin[index_row_origin], series_alternative[index_row_alternative]) >= precision or fuzz.token_set_ratio(series_origin[index_row_origin], series_alternative[index_row_alternative]) >= precision or fuzz.partial_token_set_ratio(series_origin[index_row_origin], series_alternative[index_row_alternative]) == 100:
                    index_data_match.append([index_row_origin,index_row_alternative])

        # Return either unique matches (if strict is 1) or the list of matches
        if strict == 1:
            return np.unique(index_data_match, axis=0)
        else:
            return index_data_match

    def arr_to_dic(arr: list = None):
        """
        Converts an array to a dictionary.

        Parameters:
        - arr (list): List of arrays.

        Returns:
        - dict: Dictionary with keys "A0", "A1", ..., "An" and corresponding NumPy arrays.
        """
        # Validate input parameters
        if arr is None or type(arr) != list:
            raise ValueError('A valid value for "arr" is required.')
        
        variables = {}
        for i in range(len(arr)):
            variables["A" + str(i)] = np.array(arr[i])

        return variables
    
    def matcher_pair_columns(variables: dict = None):
        """
        Matches pairs of columns in the provided dictionary.

        Parameters:
        - variables (dict): Dictionary with keys "A0", "A1", ..., "An" and corresponding NumPy arrays.

        Returns:
        - np.ndarray: Matched data from the second column ("A1").
        """

        # Validate input parameter
        if variables is None or type(variables) != dict:
            raise ValueError('A valid value for "variables" is required.')

        # Initialize a list to store matched data
        data_match = []

        # Iterate through pairs of data in the first column ("A0")
        for data_0_x, data_0_y in variables["A0"]:

            # Find rows in the second column ("A1") where the first element matches data_0_x
            resultado_booleano_xx = np.where(variables["A1"][:, 0] == data_0_x)
            filas_coincidentes = variables["A1"][resultado_booleano_xx]

            # Find rows in the result where the second element matches data_0_y
            resultado_booleano_xy = np.where(filas_coincidentes[:, 1] == data_0_y)
            filas_coincidentes = filas_coincidentes[resultado_booleano_xy]

            # If there is exactly one matching row, append it to the list
            if len(filas_coincidentes) == 1:
                data_match.append(np.ravel(filas_coincidentes))

        # Convert the list to a NumPy array and return the second column
        data_match = np.array(data_match)
        
        # return data_match[:, 1]
        return data_match

    # Load DataFrames from files
    df_origin = get_df(exists_file(pathFiles, 'origin'))
    df_alternative = get_df(exists_file(pathFiles, 'alternative'))

    # Perform data matching based on the query
    if np.ndim(query) == 1:
        # Single query case
        
        # Harmonize indices and get matched data
        data_match = harmonize_index_match(df_origin, df_alternative, query)
        print(data_match)
        # Create a DataFrame for the matched data
        df_alternative_result = pd.DataFrame(columns=df_alternative.columns)
        df_origin_result = pd.DataFrame(columns=df_origin.columns)

        for row in data_match:
            # print(df_alternative.iloc[row[1]])
            # df_origin_result.loc[len(df_origin_result.index)] = df_origin.iloc[row[0]]

            df_alternative_result.loc[len(df_alternative_result.index)] = df_alternative.iloc[row[1]]

            # df_alternative_result.loc[len(df_alternative_result.index)] = df_alternative.iloc[row[1]]
        # Save the result to JSON with or without duplicates
            
        # df_alternative_result = df_alternative_result.merge(df_origin_result,how='cross')
        if with_out_duplicates == 0:
            df_alternative_result.to_csv(f'{pathFiles}/result_withDuplicates_simple.csv')
            # df_origin_result.to_json(f'{pathFiles}/Oresult_withDuplicates_simple.json')
        else:
            df_alternative_result.drop_duplicates().to_json(f'{pathFiles}/result_withOutDuplicates_simple.json')
            # df_origin_result.drop_duplicates().to_json(f'{pathFiles}/Oresult_withOutDuplicates_simple.json')
    else:
        # Multiple queries case
        
        if len(query) >= 2:
            # Harmonize indices for each query and store the results in a matrix
            matriz_data_match = []
            for query_x in query:
                matriz_data_match.append(harmonize_index_match(df_origin, df_alternative, query_x, precision=70))
            # Convert the matrix to a dictionary
            variables = arr_to_dic(matriz_data_match)
            
            # Perform matching on pairs of columns
            result = matcher_pair_columns(variables)
            # Save the result to JSON with or without duplicates
            if with_out_duplicates == 0:
                df_agregar = df_origin.iloc[result[:, 0]]

                df_result = df_alternative.iloc[result[:,1]].reset_index(drop=True)
                # print(df_result)
                df_result['url_origin'] = df_agregar['product_url'].reset_index(drop=True)

                df_result.to_csv(f'{pathFiles}/result_withDuplicates_multi.csv')
            else:
                df_alternative.iloc[result].drop_duplicates().to_csv(f'{pathFiles}/result_withOutDuplicates_multi.csv')