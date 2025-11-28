import os
import matplotlib.pyplot as plt
import seaborn as sns
from config.paths import FIGURES_DIR

sns.set(style="whitegrid")
sns.set_context("talk")

def analyze_time_series(df):
    """
    Agrupa os dados por 'year_month', plota diversas séries temporais de revenue, freight e orders.
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
    
    os.makedirs(FIGURES_DIR, exist_ok=True)
    
    # ==== 1. Séries temporais absolutas ====
    plt.figure(figsize=(15, 6))
    sns.lineplot(data=monthly_summary, x='year_month', y='revenue', marker='o', label='Receita')
    sns.lineplot(data=monthly_summary, x='year_month', y='freight', marker='o', label='Frete')
    sns.lineplot(data=monthly_summary, x='year_month', y='orders', marker='o', label='Pedidos')
    plt.title('Séries Temporais Absolutas')
    plt.xlabel('Mês')
    plt.ylabel('Valores Absolutos')
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "series_temporais_absolutos.png"))
    plt.close()
    
    # ==== 2. Séries temporais normalizadas ====
    monthly_norm = monthly_summary.copy()
    for col in corr_cols:
        monthly_norm[col] = (monthly_summary[col] - monthly_summary[col].mean()) / monthly_summary[col].std()
    
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
    plt.savefig(os.path.join(FIGURES_DIR, "series_temporais_normalizados.png"))
    plt.close()
    
    # ==== 3. Séries mensais com IC (usando erro padrão como proxy) ====
    monthly_ci = monthly_summary.copy()
    monthly_ci['revenue_lower'] = monthly_ci['revenue'] - monthly_ci['revenue'].std() / (len(df)**0.5)
    monthly_ci['revenue_upper'] = monthly_ci['revenue'] + monthly_ci['revenue'].std() / (len(df)**0.5)
    
    plt.figure(figsize=(15, 6))
    plt.plot(monthly_ci['year_month'], monthly_ci['revenue'], marker='o', label='Receita')
    plt.fill_between(monthly_ci['year_month'], monthly_ci['revenue_lower'], monthly_ci['revenue_upper'], color='blue', alpha=0.2, label='IC aproximado')
    plt.title('Séries Temporais Mensais com IC')
    plt.xlabel('Mês')
    plt.ylabel('Receita')
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "series_temporais_mensais_ic.png"))
    plt.close()
    
    # ==== 4. Séries mensais simples ====
    plt.figure(figsize=(15, 6))
    sns.lineplot(data=monthly_summary, x='year_month', y='revenue', marker='o', label='Receita')
    sns.lineplot(data=monthly_summary, x='year_month', y='freight', marker='o', label='Frete')
    sns.lineplot(data=monthly_summary, x='year_month', y='orders', marker='o', label='Pedidos')
    plt.title('Séries Temporais Mensais')
    plt.xlabel('Mês')
    plt.ylabel('Valores Absolutos')
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "series_temporais_mensais.png"))
    plt.close()
    
    # ==== 5. Variação percentual mensal ====
    monthly_pct = monthly_summary.copy()
    monthly_pct[corr_cols] = monthly_pct[corr_cols].pct_change() * 100
    plt.figure(figsize=(15, 6))
    for col in corr_cols:
        sns.lineplot(data=monthly_pct, x='year_month', y=col, marker='o', label=f'{col} (%)')
    plt.title('Variação Percentual Mensal')
    plt.xlabel('Mês')
    plt.ylabel('Variação (%)')
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "series_temporais_variacao_percentual.png"))
    plt.close()
    
    return monthly_summary