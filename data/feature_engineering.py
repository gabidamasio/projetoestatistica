import pandas as pd

def apply_feature_engineering(df):
    """
    Cria features derivadas do dataset de pedidos:
    - delivery_delay_days, delivery_lead_time, is_late, is_confirmed,
      freight_share, discount_abs
    - Converte datas para datetime
    """
    # -------- Conversões de data --------
    for col in ['order_date', 'delivery_forecast', 'delivery_date']:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

    # -------- Features principais --------
    if 'delivery_delay_days' not in df.columns:
        df['delivery_delay_days'] = (df['delivery_date'] - df['delivery_forecast']).dt.days

    if 'delivery_lead_time' not in df.columns:
        df['delivery_lead_time'] = (df['delivery_date'] - df['order_date']).dt.days

    if 'is_late' not in df.columns:
        df['is_late'] = (df['delivery_delay_days'] > 0).astype(int)

    # Garantir inteiro em is_confirmed (mesmo se já existir)
    if 'is_confirmed' in df.columns:
        df['is_confirmed'] = pd.to_numeric(df['is_confirmed'], errors='coerce').fillna(0).astype(int)

    if 'freight_share' not in df.columns:
        df['freight_share'] = df['freight_price'] / df['total'].replace(0, pd.NA)

    if 'discount_abs' not in df.columns:
        df['discount_abs'] = df['subtotal'] - df['total']

    return df