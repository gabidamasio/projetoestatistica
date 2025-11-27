import pandas as pd
from config.paths import PROCESSED_DIR
import os

def load_csv(path="vw_gold_orders/vw_gold_orders.csv"):
    """
    Carrega um CSV da pasta processada com pandas.
    """
    csv_path = os.path.join(PROCESSED_DIR, path)
    
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Arquivo não encontrado: {csv_path}")
    
    return pd.read_csv(csv_path)
