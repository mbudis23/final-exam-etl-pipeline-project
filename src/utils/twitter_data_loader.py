import pandas as pd
import os

def load_twitter_data(file_path, required_columns=None):
    """
    Membaca file CSV data Twitter, memvalidasi keberadaan kolom yang diperlukan,
    dan mengembalikan DataFrame dengan kolom yang diubah namanya.

    Parameters:
    - file_path (str): Path ke file CSV.
    - required_columns (list, optional): Kolom yang wajib ada dalam file. Default adalah:
      ['Datetime', 'Username', 'Tweet Text'].

    Returns:
    - pd.DataFrame: DataFrame yang hanya berisi kolom yang diperlukan, dengan nama kolom diubah.
    """
    # Default required columns jika tidak diberikan
    if required_columns is None:
        required_columns = ['Datetime', 'Username', 'Tweet Text']

    # Normalisasi path
    normalized_path = os.path.realpath(file_path)
    print(f"Loading data from: {normalized_path}")

    # Pastikan file ada
    if not os.path.exists(normalized_path):
        raise FileNotFoundError(f"File not found: {normalized_path}")

    # Load CSV
    try:
        df = pd.read_csv(normalized_path)
        print(f"Successfully loaded file with {len(df)} rows.")
    except pd.errors.ParserError as e:
        raise ValueError(f"Error parsing file: {e}")

    # Validasi keberadaan kolom yang diperlukan
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Kolom berikut tidak ditemukan dalam file: {missing_columns}")

    # Pilih hanya kolom yang diperlukan
    load_df = df[required_columns]

    # Ubah nama kolom
    column_mapping = {
        'Datetime': 'Date', 
        'Username': 'User', 
        'Tweet Text': 'Tweet'
    }
    load_df.rename(columns=column_mapping, inplace=True)

    print(f"Returning DataFrame with columns: {list(load_df.columns)}")
    return load_df
