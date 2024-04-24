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


def find_exact_and_similar_matches(values_alternative, values_origin, threshold=80):
    """
    Encuentra coincidencias exactas y similares entre dos listas de valores.

    Parameters:
        values_alternative (list): Lista de valores de referencia.
        values_origin (list): Lista de valores con los que se compararán los valores de referencia.
        threshold (int): Umbral de similitud para considerar una coincidencia como similar (valor predeterminado: 80).

    Returns:
        tuple: Una tupla que contiene dos listas: coincidencias exactas y coincidencias similares.

    La función itera a través de los valores en 'values_alternative' y busca coincidencias exactas y similares en 'values_origin'.
    Las coincidencias exactas se almacenan en 'exact_matches', mientras que las coincidencias similares se almacenan en 'similar_matches'.
    Si se encuentra una coincidencia exacta, la función se detiene y pasa al siguiente valor en 'values_alternative'.
    Luego, calcula los porcentajes de coincidencias exactas y similares en relación con la longitud de 'values_alternative'.
    Si al menos uno de los porcentajes es mayor o igual al 80%, devuelve ambas listas.

    Notas:
        - Los valores 'NaN', 'nan', '0', y None se excluyen de las comparaciones.

    Ejemplo de uso:
        exact, similar = find_exact_and_similar_matches(lista1, lista2, 85)
    """
    exact_matches = []
    similar_matches = []

    for val_alternative in values_alternative:
        exact_match_found = False
        for val_origin in values_origin:
            # Convierte ambos valores a cadenas de texto (str) para asegurarte de que sean comparables
            val_alternative_str = str(val_alternative)
            val_origin_str = str(val_origin)

            # Excluye ciertos valores de las comparaciones
            if val_origin_str == 'NaN' or val_origin_str is None or val_alternative_str == 'NaN' or val_alternative_str is None or val_origin_str == 'nan' or val_origin_str == '0' or val_alternative_str == 'nan' or val_alternative_str == '0':
                continue

            if val_alternative_str == val_origin_str:
                exact_matches.append((val_alternative, val_origin))
                exact_match_found = True
                break  # Rompe el bucle si se encuentra una coincidencia exacta
            else:
                similarity = fuzz.token_set_ratio(val_alternative_str, val_origin_str)
                if similarity >= threshold:
                    similar_matches.append((val_alternative, val_origin))

        if not exact_match_found:
            # Si no se encontró una coincidencia exacta, puedes hacer algo aquí
            pass

    # Calcula los porcentajes de coincidencias exactas y similares en relación con la longitud de values_alternative
    porcentaje_exactas = (len(exact_matches) / len(values_alternative)) * 100
    porcentaje_similares = (len(similar_matches) / len(values_alternative)) * 100

    # Verifica si al menos uno de los porcentajes es mayor o igual al 80%
    if porcentaje_exactas >= 80 or porcentaje_similares >= 80:
        return exact_matches, similar_matches

def cumple_condiciones_match(column_name_origin, column_name_alternative):
    """
    Verifica si un par de nombres de columnas cumple ciertas condiciones de coincidencia.

    Parameters:
        column_name_origin (str): Nombre de columna de origen a verificar.
        column_name_alternative (str): Nombre de columna alternativa a verificar.

    Returns:
        bool: True si ninguna de las condiciones se cumple, False si al menos una condición se cumple.

    La función verifica si los nombres de las columnas, 'column_name_origin' y 'column_name_alternative', cumplen
    ciertas condiciones de coincidencia en función de una lista de condiciones predefinidas. Si alguna de las condiciones
    se cumple, la función devuelve False; de lo contrario, devuelve True.

    Las condiciones se definen en el archivo 'rules.json'.

    Ejemplo de uso:
        resultado = cumple_condiciones_match('degree_of_alcohol', 'year')
    """
    # Lista de condiciones a verificar
    def find_not_match():
        with open('rules.json', 'r') as file:
            config = json.load(file)

    condiciones = [
        ('degree_of_alcohol', 'year'),
        ('price', 'volume'),
        ('volume', 'price')
    ]
    
    # Verifica si alguna de las condiciones se cumple
    for condicion in condiciones:
        condicion_origin, condicion_alternative = condicion
        if (
            fuzz.partial_ratio(condicion_origin, column_name_origin) >= 80 or
            fuzz.partial_ratio(condicion_alternative, column_name_alternative) >= 80
        ):
            return False
    
    # Si ninguna de las condiciones se cumple, devuelve True
    return True

def find_columns_match(df_origin, df_alternative):
    """
    Encuentra columnas en dos DataFrames que cumplen con ciertas condiciones y tienen coincidencias de valores.

    Parameters:
        df_origin (pd.DataFrame): DataFrame de origen.
        df_alternative (pd.DataFrame): DataFrame alternativo.

    Returns:
        list: Una lista de nombres de columnas en el formato "columna_origen,columna_alternativa"
        que cumplen con las condiciones y tienen coincidencias de valores.

    La función busca coincidencias de columnas entre dos DataFrames ('df_origin' y 'df_alternative') en ambos sentidos.
    Para cada par de columnas que cumple con ciertas condiciones definidas en las funciones auxiliares, busca coincidencias
    de valores utilizando 'fuzzywuzzy'. Si encuentra coincidencias, las agrega a la lista 'columns_match'.

    Las condiciones se definen en las funciones auxiliares 'cumple_condiciones' y 'cumple_condiciones_match'.

    Ejemplo de uso:
        coincidencias = find_columns_match(dataframe_origen, dataframe_alternativo)
    """
    def find_exact_and_similar_matches(values_alternative, values_origin, threshold=80):
        exact_matches = []
        similar_matches = []

        for val_alternative in values_alternative:
            exact_match_found = False
            for val_origin in values_origin:
            # Convierte ambos valores a cadenas de texto (str) para asegurarte de que sean comparables
                val_alternative_str = str(val_alternative)
                val_origin_str = str(val_origin)
                # if fuzz.token_set_ratio(val_alternative_str, 'nan') == 100 or fuzz.token_set_ratio(val_origin_str, 'nan') == 100 or fuzz.token_set_ratio(val_alternative_str, '0') == 100 or fuzz.token_set_ratio(val_origin_str, '0') == 100 :
                #     continue
                if val_origin_str ==  'NaN' or val_origin_str is None  or val_alternative_str ==  'NaN' or val_alternative_str is None or val_origin_str ==  'nan' or val_origin_str == '0'  or val_alternative_str ==  'nan' or val_alternative_str == '0':
                    continue
                
                # print(val_origin_str, val_alternative_str)
                if val_alternative_str == val_origin_str:
                    exact_matches.append((val_alternative, val_origin))
                    exact_match_found = True
                    break  # Rompe el bucle si se encuentra una coincidencia exacta
                else:
                    similarity = fuzz.token_set_ratio(val_alternative_str, val_origin_str)
                    if similarity >= threshold:
                        similar_matches.append((val_alternative, val_origin))
        
            if not exact_match_found:
                # Si no se encontró una coincidencia exacta, puedes hacer algo aquí
                pass
    
        # Calcula los porcentajes de coincidencias exactas y similares en relación con la longitud de df_alternative
        porcentaje_exactas = (len(exact_matches) / len(values_alternative)) * 100
        porcentaje_similares = (len(similar_matches) / len(values_alternative)) * 100

        # Verifica si al menos uno de los porcentajes es mayor o igual al 80%
        if porcentaje_exactas >= 80 or porcentaje_similares >= 80:
            return exact_matches, similar_matches

    def cumple_condiciones(column_values):
        # Código de verificación de condiciones para las columnas, igual que en la versión original
        column_name = column_values.name.lower()
        if fuzz.partial_ratio('id origin', column_name) >= 80:  # Ajusta el umbral de similitud según tus necesidades
            return False
        return ( not column_values.isna().all()) or (column_values.eq(0).all()) or (column_values.eq('0').all())

    # Suponiendo que ya tienes definidos df_origin y df_alternative
    columns_origin = set(df_origin.columns)
    columns_alternative = set(df_alternative.columns)

    columns_match = []

    # Buscar coincidencias en ambos sentidos con fuzzywuzzy
    for column_origin in columns_origin:
        column_values_origin = df_origin[column_origin]

        # Verificar si la columna de origen cumple con las condiciones
        if not cumple_condiciones(column_values_origin):
            continue
        
        for column_alternative in columns_alternative:
            column_values_alternative = df_alternative[column_alternative]

            # Verificar si la columna alternativa cumple con las condiciones
            if (
                cumple_condiciones_match(column_origin, column_alternative) and
                cumple_condiciones(column_values_alternative)
            ):
                result = find_exact_and_similar_matches(column_values_alternative, column_values_origin)

                # Verificar si la función devolvió un resultado válido antes de desempaquetar
                if result is not None:
                    columns_match.append(f'{column_origin},{column_alternative}')
    return columns_match

def ordenar_columnas(columnas = None, dataType = None):
    """
    Ordena una lista de pares de nombres de columnas en función de ciertas condiciones de prioridad.

    Parameters:
        columnas (list): Una lista de pares de nombres de columnas en el formato "columna_origen,columna_alternativa".

    Returns:
        list: Una lista ordenada de pares de nombres de columnas en función de la prioridad de coincidencia.

    Esta función toma una lista de pares de nombres de columnas y los ordena en función de ciertas condiciones de prioridad
    definidas en el archivo de configuración 'rules.json'. Las condiciones de prioridad se determinan mediante la similitud
    de nombres y otras reglas definidas.

    Ejemplo de uso:
        columnas_ordenadas = ordenar_columnas(lista_de_columnas)
    """

    if dataType == None:
        print('No ingresaste el tipo de data')
        return
    order = []

    for columna in columnas:
        columna_origin, columna_alternative = columna.split(',')
        max_priority = 0  # Para mantener un seguimiento de la máxima prioridad encontrada
        
        for field in config[dataType]:
            priority = 0 
            # Lógica para determinar la prioridad en función de la similitud de nombres y otras reglas definidas

            if fuzz.token_set_ratio(field['name'], columna_origin) >= 80 or fuzz.token_set_ratio(field['name'], columna_alternative) >= 80:

                if (columna_origin.lower() == columna_alternative.lower() or fuzz.token_set_ratio(columna_origin, columna_alternative) >= 80):
                    if (field['priority'] == 2): 
                        priority = 3
                    elif(field['priority'] == 1):
                        priority = 2
                    else:
                        priority = 1
                else:
                    if field['name'] == columna_origin or fuzz.token_set_ratio(field['name'], columna_origin) >= 80:
                        if (field['priority'] == 2): 
                            priority = 3
                        elif(field['priority'] == 1):
                            priority = 2
                        
                        for name_alternative in config[dataType]:
                            if name_alternative['name'] == columna_alternative or fuzz.token_set_ratio(name_alternative['name'], columna_alternative) >= 80:
                                if field['priority'] == 2 and name_alternative['priority'] == 2:
                                    priority = 3
                                elif field['priority'] == 2 and name_alternative['priority'] == 1 or field['priority'] == 1 and name_alternative['priority'] == 2:
                                    priority = 2
                                elif field['priority'] == 2 and name_alternative['priority'] == 0 or field['priority'] == 0 and name_alternative['priority'] == 2:
                                    priority = 1
                                elif field['priority'] == 1 and name_alternative['priority'] == 0 or field['priority'] == 0 and name_alternative['priority'] == 1:
                                    priority = 1
                                
                            else:
                                for sinonimos in name_alternative['sinonimos']:
                                    if  sinonimos == columna_alternative or fuzz.token_set_ratio(sinonimos, columna_alternative) >= 80:
                                        if field['priority'] == 2 and name_alternative['priority'] == 2:
                                            priority = 3
                                        elif field['priority'] == 2 and name_alternative['priority'] == 1 or field['priority'] == 1 and name_alternative['priority'] == 2:
                                            priority = 2
                                        elif field['priority'] == 2 and name_alternative['priority'] == 0 or field['priority'] == 0 and name_alternative['priority'] == 2:
                                            priority = 1
                                        elif field['priority'] == 1 and name_alternative['priority'] == 0 or field['priority'] == 0 and name_alternative['priority'] == 1:
                                            priority = 1
                        
                    elif field['name'] == columna_alternative or fuzz.token_set_ratio(field['name'], columna_alternative) >= 80:
                        if (field['priority'] == 2): 
                            priority = 3
                        elif(field['priority'] == 1):
                            priority = 2
                        else:
                            priority = 1
                        for name_origin in config[dataType]:
                            if name_origin['name'] == columna_origin or fuzz.token_set_ratio(name_origin['name'], columna_origin) >= 80:
                                if field['priority'] == 2 and name_origin['priority'] == 2:
                                    priority = 3
                                elif field['priority'] == 2 and name_origin['priority'] == 1 or field['priority'] == 1 and name_origin['priority'] == 2:
                                    priority = 2
                                elif field['priority'] == 2 and name_origin['priority'] == 0 or field['priority'] == 0 and name_origin['priority'] == 2:
                                    priority = 1
                                elif field['priority'] == 1 and name_origin['priority'] == 0 or field['priority'] == 0 and name_origin['priority'] == 1:
                                    priority = 1
                                continue
                            else:
                                for sinonimos in name_origin['sinonimos']:
                                    if  sinonimos == columna_origin or fuzz.token_set_ratio(sinonimos, columna_origin) >= 80:
                                        if field['priority'] == 2 and name_origin['priority'] == 2:
                                            priority = 3
                                        elif field['priority'] == 2 and name_origin['priority'] == 1 or field['priority'] == 1 and name_origin['priority'] == 2:
                                            priority = 2
                                        elif field['priority'] == 2 and name_origin['priority'] == 0 or field['priority'] == 0 and name_origin['priority'] == 2:
                                            priority = 1
                                        elif field['priority'] == 1 and name_origin['priority'] == 0 or field['priority'] == 0 and name_origin['priority'] == 1:
                                            priority = 1 
            else:
                for sinonimos in field['sinonimos']:
                    if sinonimos == columna_origin or fuzz.token_set_ratio(sinonimos, columna_origin) >= 80:
                        if (field['priority'] == 2): 
                            priority = 3
                        elif(field['priority'] == 1):
                            priority = 2
                        
                        for name_alternative in config[dataType]:
                            if name_alternative['name'] == columna_alternative or fuzz.token_set_ratio(name_alternative['name'], columna_alternative) >= 80:
                                if field['priority'] == 2 and name_alternative['priority'] == 2:
                                    priority = 3
                                elif field['priority'] == 2 and name_alternative['priority'] == 1 or field['priority'] == 1 and name_alternative['priority'] == 2:
                                    priority = 2
                                elif field['priority'] == 2 and name_alternative['priority'] == 0 or field['priority'] == 0 and name_alternative['priority'] == 2:
                                    priority = 1
                                elif field['priority'] == 1 and name_alternative['priority'] == 0 or field['priority'] == 0 and name_alternative['priority'] == 1:
                                    priority = 1
                                
                            else:
                                for sinonimos in name_alternative['sinonimos']:
                                    if  sinonimos == columna_alternative or fuzz.token_set_ratio(sinonimos, columna_alternative) >= 80:
                                        if field['priority'] == 2 and name_alternative['priority'] == 2:
                                            priority = 3
                                        elif field['priority'] == 2 and name_alternative['priority'] == 1 or field['priority'] == 1 and name_alternative['priority'] == 2:
                                            priority = 2
                                        elif field['priority'] == 2 and name_alternative['priority'] == 0 or field['priority'] == 0 and name_alternative['priority'] == 2:
                                            priority = 1
                                        elif field['priority'] == 1 and name_alternative['priority'] == 0 or field['priority'] == 0 and name_alternative['priority'] == 1:
                                            priority = 1
                    if sinonimos == columna_alternative or fuzz.token_set_ratio(sinonimos, columna_alternative) >= 80:
                        for name_origin in config[dataType]:
                            if name_origin['name'] == columna_origin or fuzz.token_set_ratio(name_origin['name'], columna_origin) >= 80:
                                if field['priority'] == 2 and name_origin['priority'] == 2:
                                    priority = 3
                                elif field['priority'] == 2 and name_origin['priority'] == 1 or field['priority'] == 1 and name_origin['priority'] == 2:
                                    priority = 2
                                elif field['priority'] == 2 and name_origin['priority'] == 0 or field['priority'] == 0 and name_origin['priority'] == 2:
                                    priority = 1
                                elif field['priority'] == 1 and name_origin['priority'] == 0 or field['priority'] == 0 and name_origin['priority'] == 1:
                                    priority = 1
                                continue
                            else:
                                for sinonimos in name_origin['sinonimos']:
                                    if  sinonimos == columna_origin or fuzz.token_set_ratio(sinonimos, columna_origin) >= 80:
                                        if field['priority'] == 2 and name_origin['priority'] == 2:
                                            priority = 3
                                        elif field['priority'] == 2 and name_origin['priority'] == 1 or field['priority'] == 1 and name_origin['priority'] == 2:
                                            priority = 2
                                        elif field['priority'] == 2 and name_origin['priority'] == 0 or field['priority'] == 0 and name_origin['priority'] == 2:
                                            priority = 1
                                        elif field['priority'] == 1 and name_origin['priority'] == 0 or field['priority'] == 0 and name_origin['priority'] == 1:
                                            priority = 1
                
            if priority > max_priority:
                max_priority = priority

        # Añade a la lista de orden solo si la prioridad máxima es mayor que 0
        if max_priority >= 0:
            order.append((max_priority, columna_origin, columna_alternative))

    # Ordena la lista por prioridad en orden descendente
    order.sort(reverse=True)

    return order




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
        return data_match[:, 1]

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
            df_alternative_result.to_json(f'{pathFiles}/result_withDuplicates_simple.json')
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
            print(matriz_data_match)
            # Convert the matrix to a dictionary
            variables = arr_to_dic(matriz_data_match)
            
            # Perform matching on pairs of columns
            result = matcher_pair_columns(variables)
            
            # Save the result to JSON with or without duplicates
            if with_out_duplicates == 0:
                df_result = df_alternative.iloc[result].reset_index(drop=True)
                # print(df_result)
                df_result.to_json(f'{pathFiles}/result_withDuplicates_multi.json')
            else:
                df_alternative.iloc[result].drop_duplicates().to_json(f'{pathFiles}/result_withOutDuplicates_multi.json')