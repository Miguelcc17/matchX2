import matcher

def toolkit_detect_language(file_path: str = None, columns: bool = False)->dict: 
    if file_path is None or len(file_path) == 0:
        raise ValueError("'file_path' cannot be empty")
    if type(file_path) != str:
        raise TypeError("data type compatible only 'str'")
    if type(columns) != bool:
        raise TypeError('Columns must be bool')
    from transformers import pipeline
    pipe = pipeline("text-classification", model="ImranzamanML/GEFS-language-detector")
    max_length = 2187
    def split_text(text, max_length):
        words = text.split()  
        words_selected = []
        currency_length = 0
        for word in words:
            if currency_length + len(word) + sum(map(len, words_selected)) <= max_length:
                words_selected.append(word)
                currency_length += len(word)
            else:
                break       
        return ' '.join(words_selected)
    df = matcher.get_df(file_path)
    if not columns:         
        text_combined = ' '.join(df.apply(lambda row: ', '.join(row.astype(str).unique()), axis=1))
        texto_cortado = split_text(text_combined, max_length)
        return pipe(texto_cortado)[0]['label']  
    # Convert each column to a text series and get unique values
    unique_values_by_column = df.apply(lambda col: col.astype(str).unique())
    # Iterate over the keys of the dictionary of unique values by column
    for column_name, values in unique_values_by_column.items():
        # Join the unique values into a single string
        complete_text = ' '.join(values)       
        # Split the text into segments
        divided_text = split_text(complete_text, max_length) 
        unique_values_by_column[column_name] = pipe(divided_text)[0]['label']
    return unique_values_by_column