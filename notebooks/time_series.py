import os
import matplotlib.pyplot as plt
import seaborn as sns
from config.paths import FIGURES_DIR

sns.set(style="whitegrid")
sns.set_context("talk")

def analyze_time_series(df):
    """
    Agrupa os dados por 'year_month', plota séries temporais normalizadas de revenue, freight e orders,
    e imprime a correlação mensal.
    Retorna o DataFrame mensal agregado.
    """
    df['year_month'] = df['order_date'].dt.to_period('M')
    
    # Agrupamento mensal
    monthly_summary = df.groupby('year_month').agg(
        revenue=('product_price', 'sum'),
        freight=('freight_price', 'sum'),
        orders=('order_id', 'count')
    ).reset_index()
    
    # Converter year_month de Period -> datetime
    monthly_summary['year_month'] = monthly_summary['year_month'].dt.to_timestamp()
    
    # ==== Correlação mensal ====
    corr_cols = ['revenue', 'orders', 'freight']
    print("\n===== Correlação entre receita, pedidos e frete (mensal) =====")
    print(monthly_summary[corr_cols].corr())
    
    # ==== Normalização para plot visual comparável ====
    monthly_norm = monthly_summary.copy()
    for col in corr_cols:
        monthly_norm[col] = (monthly_summary[col] - monthly_summary[col].mean()) / monthly_summary[col].std()
    
    # ==== Plot das séries normalizadas ====
    plt.figure(figsize=(15, 6))
    sns.lineplot(data=monthly_norm, x='year_month', y='revenue', marker='o', label='Receita (normalizada)')
    sns.lineplot(data=monthly_norm, x='year_month', y='freight', marker='o', label='Frete (normalizado)')
    sns.lineplot(data=monthly_norm, x='year_month', y='orders', marker='o', label='Pedidos (normalizados)')
    
    plt.title('Séries Temporais Mensais (Normalizadas)')
    plt.xlabel('Mês')
    plt.ylabel('Valores Normalizados')
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    
    # Salva o gráfico
    os.makedirs(FIGURES_DIR, exist_ok=True)
    plt.savefig(os.path.join(FIGURES_DIR, "series_temporais_mensais_normalizadas.png"))
    plt.close()
    
    return monthly_summary