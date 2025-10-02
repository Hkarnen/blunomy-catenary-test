import pandas as pd

def load_parquet(file_path):
    """Load a LiDAR Parquet file into a Pandas DataFrame."""
    return pd.read_parquet(file_path)