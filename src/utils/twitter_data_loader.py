import pandas as pd
import os

def validate_file_path(file_path):
    """
    Validasi keberadaan file pada path yang diberikan.

    Parameters:
    - file_path (str): Path ke file CSV.

    Raises:
    - FileNotFoundError: Jika file tidak ditemukan.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

def validate_required_columns(df, required_columns):
    """
    Validasi keberadaan kolom yang diperlukan dalam DataFrame.

    Parameters:
    - df (pd.DataFrame): DataFrame yang akan divalidasi.
    - required_columns (list): Daftar kolom yang wajib ada.

    Raises:
    - ValueError: Jika ada kolom yang hilang.
    """
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Kolom berikut tidak ditemukan dalam file: {missing_columns}")

def read_csv_file(file_path):
    """
    Membaca file CSV dan mengembalikan DataFrame.

    Parameters:
    - file_path (str): Path ke file CSV.

    Returns:
    - pd.DataFrame: DataFrame hasil pembacaan file.

    Raises:
    - ValueError: Jika terjadi kesalahan saat parsing file.
    """
    try:
        df = pd.read_csv(file_path)
        print(f"Successfully loaded file with {len(df)} rows.")
        return df
    except pd.errors.ParserError as e:
        raise ValueError(f"Error parsing file: {e}")

def rename_columns(df, column_mapping):
    """
    Mengganti nama kolom pada DataFrame sesuai dengan mapping yang diberikan.

    Parameters:
    - df (pd.DataFrame): DataFrame yang kolomnya akan diubah.
    - column_mapping (dict): Dictionary mapping nama kolom lama ke nama kolom baru.

    Returns:
    - pd.DataFrame: DataFrame dengan kolom yang sudah diganti namanya.
    """
    return df.rename(columns=column_mapping, inplace=False)

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

    # Validasi file path
    validate_file_path(normalized_path)

    # Baca file CSV
    df = read_csv_file(normalized_path)

    # Validasi keberadaan kolom yang diperlukan
    validate_required_columns(df, required_columns)

    # Pilih hanya kolom yang diperlukan
    selected_df = df[required_columns]

    # Ubah nama kolom
    column_mapping = {
        'Datetime': 'Date', 
        'Username': 'User', 
        'Tweet Text': 'Tweet'
    }
    processed_df = rename_columns(selected_df, column_mapping)

    print(f"Returning DataFrame with columns: {list(processed_df.columns)}")
    return processed_df
