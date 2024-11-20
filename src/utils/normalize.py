import pandas as pd
import numpy as np

def convert_column_to_integer(df, column_name):
    """
    Convert a column with values like '14K', '3.1K', '2M', or NaN to integers.

    Parameters:
    - df (pd.DataFrame): DataFrame containing the column to process.
    - column_name (str): Name of the column to convert.

    Returns:
    - pd.DataFrame: The updated DataFrame with the column converted to integers.
    """
    def convert_to_int(value):
        """Helper function to convert a single value to integer."""
        if pd.isna(value):  # Handle NaN values
            return 0
        if isinstance(value, str):
            if value.endswith('K'):  # Handle 'K' suffix (thousands)
                return int(float(value[:-1]) * 1000)
            elif value.endswith('M'):  # Handle 'M' suffix (millions)
                return int(float(value[:-1]) * 1000000)
            elif value.replace('.', '', 1).isdigit():  # Handle pure numeric strings
                return int(float(value))
        elif isinstance(value, (int, float)):  # Handle numeric types
            return int(value)
        return 0  # Default fallback for unexpected values

    try:
        # Ensure the column exists
        if column_name not in df.columns:
            raise KeyError(f"Column '{column_name}' does not exist in the DataFrame.")
        
        # Apply conversion
        df[column_name] = df[column_name].apply(convert_to_int)
        print(f"Successfully converted '{column_name}' to integers.")
    except KeyError as ke:
        print(f"KeyError: {ke}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    
    return df


def convert_column_to_string(df, column_name):
    """
    Convert a column to string type in a DataFrame.

    Parameters:
    - df (pd.DataFrame): The DataFrame containing the column to convert.
    - column_name (str): The name of the column to convert.

    Returns:
    - pd.DataFrame: The updated DataFrame with the column converted to string type.
    """
    try:
        # Ensure the column exists
        if column_name not in df.columns:
            raise KeyError(f"Column '{column_name}' does not exist in the DataFrame.")
        
        # Convert the column to string
        df[column_name] = df[column_name].astype(str)
        print(f"Successfully converted '{column_name}' to string.")
    except KeyError as ke:
        print(f"KeyError: {ke}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return df