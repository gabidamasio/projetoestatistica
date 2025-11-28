import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from config.paths import FIGURES_DIR

sns.set(style="whitegrid")
sns.set_context("talk")

def plot_histograms_and_boxplots(df):
    """
    Plota histogramas e boxplots para colunas numéricas específicas.
    Colunas: product_price, delivery_lead_time, discount_abs
    Além disso, adiciona:
    - Boxenplot para discount_abs
    - Elasticidade de discount_abs x product_price
    """
    numeric_cols = ['product_price', 'delivery_lead_time', 'discount_abs']
    colors = {
        'product_price': 'skyblue',
        'delivery_lead_time': 'lightgreen',
        'discount_abs': 'orange'
    }

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

        # Histograma com KDE
        plt.figure(figsize=(10, 5))
        sns.histplot(df[col].dropna(), kde=True, bins=30, color=colors.get(col, 'skyblue'))
        plt.title(f"Histograma de {col}")
        plt.tight_layout()
        plt.savefig(os.path.join(FIGURES_DIR, f"histograma_{col}.png"))
        plt.close()

        # Boxplot
        plt.figure(figsize=(10, 5))
        sns.boxplot(x=df[col].dropna(), color=colors.get(col, 'lightgreen'))
        plt.title(f"Boxplot de {col}")
        plt.tight_layout()
        plt.savefig(os.path.join(FIGURES_DIR, f"boxplot_{col}.png"))
        plt.close()

    # =========================
    # Boxenplot de discount_abs
    # =========================
    plt.figure(figsize=(12, 6))
    sns.boxenplot(x='discount_abs', data=df, color='orange')
    plt.title("Boxenplot de discount_abs")
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "boxenplot_discount_abs.png"))
    plt.close()

    # =========================
    # Elasticidade discount_abs x product_price
    # =========================
    plt.figure(figsize=(12, 6))
    sns.scatterplot(x='discount_abs', y='product_price', data=df, alpha=0.6)
    sns.regplot(x='discount_abs', y='product_price', data=df, scatter=False, color='red', line_kws={'lw':2})
    plt.title("Elasticidade: discount_abs x product_price")
    plt.xlabel("Discount Absoluto")
    plt.ylabel("Ticket Médio")
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "elasticidade_discount_ticket.png"))
    plt.close()