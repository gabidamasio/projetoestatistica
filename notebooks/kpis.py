import os
import pandas as pd
from config.paths import TABLES_DIR

def compute_kpis(df):

    group_cols = ['category','subcategory','delivery_service']

    result_paths = {}

    for col in group_cols:
        if col not in df.columns:
            print(f"⚠️ Coluna {col} ausente")
            continue

        kpi = df.groupby(col).agg(
            total_orders=('order_id','count'),
            total_revenue=('product_price','sum'),
            avg_ticket=('product_price','mean'),
            avg_lead_time=('delivery_lead_time','mean'),
            total_discount=('discount_abs','sum'),
            avg_freight_share=('freight_share','mean'),
            pct_canceled=('is_confirmed', lambda x: 100*(x==0).mean()),
            pct_late=('is_late', lambda x: 100*(x==1).mean())
        ).reset_index()

        path = os.path.join(TABLES_DIR, f"kpis_{col}.csv")
        kpi.to_csv(path, index=False)
        result_paths[col] = path

    return result_paths
