import os
import seaborn as sns
import matplotlib.pyplot as plt
from config.paths import FIGURES_DIR

def plot_correlation(df):

    cols = [
        'subtotal','discount','total','discount_abs','freight_price',
        'delivery_lead_time','delivery_delay_days','is_late',
        'is_confirmed','freight_share','product_price'
    ]

    df_corr = df[cols].apply(lambda x: x.astype(float)).dropna()

    corr = df_corr.corr()

    plt.figure(figsize=(12,10))
    sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f")
    plt.title("Heatmap de Correlação")
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "heatmap_correlacao.png"))
    plt.close()
