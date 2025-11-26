# ============================================================
# EDA Inicial - Carregamento, inspeção e visualização dos dados
# ============================================================

import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

# ------------------------------------------------------------
# Configurações de estilo
# ------------------------------------------------------------
sns.set(style="whitegrid")  # estilo dos gráficos
sns.set_context("talk")     # melhora títulos e labels

# ------------------------------------------------------------
# Caminho do CSV (relativo ao script)
# ------------------------------------------------------------
script_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(script_dir, "..", "data", "processed", "vw_gold_orders", "vw_gold_orders.csv")

# ------------------------------------------------------------
# Diretórios de saída
# ------------------------------------------------------------
figures_dir = os.path.join(script_dir, "..", "outputs", "figures")
tables_dir = os.path.join(script_dir, "..", "outputs", "tables")
os.makedirs(figures_dir, exist_ok=True)
os.makedirs(tables_dir, exist_ok=True)

# ------------------------------------------------------------
# Carregar dados
# ------------------------------------------------------------
df = pd.read_csv(csv_path)

# ------------------------------------------------------------
# Inspeção inicial
# ------------------------------------------------------------
print("===== 5 primeiras linhas =====")
print(df.head())

print("\n===== Info geral =====")
print(df.info())

print("\n===== Estatísticas descritivas =====")
print(df.describe())

print("\n===== Valores ausentes =====")
print(df.isna().sum())

# ============================================================
# Criar features de engenharia
# ============================================================

# Converter colunas de data
df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
df['delivery_forecast'] = pd.to_datetime(df['delivery_forecast'], errors='coerce')
df['delivery_date'] = pd.to_datetime(df['delivery_date'], errors='coerce')

# delivery_delay_days: diferença entre entrega real e prevista
if 'delivery_delay_days' not in df.columns:
    df['delivery_delay_days'] = (df['delivery_date'] - df['delivery_forecast']).dt.days

# delivery_lead_time: diferença entre entrega e pedido
if 'delivery_lead_time' not in df.columns:
    df['delivery_lead_time'] = (df['delivery_date'] - df['order_date']).dt.days

# is_late: atraso positivo
if 'is_late' not in df.columns:
    df['is_late'] = (df['delivery_delay_days'] > 0).astype(int)

# is_confirmed: garantir inteiro
df['is_confirmed'] = pd.to_numeric(df['is_confirmed'], errors='coerce').fillna(0).astype(int)

# freight_share: proporção do frete
if 'freight_share' not in df.columns:
    df['freight_share'] = df['freight_price'] / df['total']

# discount_abs: valor absoluto do desconto
if 'discount_abs' not in df.columns:
    df['discount_abs'] = df['subtotal'] - df['total']

# Verificar features criadas
feature_cols = ['delivery_delay_days', 'delivery_lead_time', 'is_late',
                'is_confirmed', 'freight_share', 'discount_abs']
print("\n===== Features criadas =====")
print(df[feature_cols].head())

# ============================================================
# EDA Inicial - Histogramas e Boxplots
# ============================================================

numeric_cols_hist = ['product_price', 'delivery_lead_time', 'discount_abs']

for col in numeric_cols_hist:
    df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Histograma
    plt.figure(figsize=(10, 5))
    sns.histplot(df[col].dropna(), kde=True, bins=30, color='skyblue')
    plt.title(f'Histograma de {col}')
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, f"histograma_{col}.png"))
    plt.close()
    
    # Boxplot
    plt.figure(figsize=(10, 5))
    sns.boxplot(x=df[col].dropna(), color='lightgreen')
    plt.title(f'Boxplot de {col}')
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, f"boxplot_{col}.png"))
    plt.close()

# ============================================================
# EDA Inicial - Séries Temporais
# ============================================================

df['year_month'] = df['order_date'].dt.to_period('M')

monthly_summary = df.groupby('year_month').agg({
    'product_price': 'sum',  # receita
    'freight_price': 'sum',  # frete
    'order_id': 'count'      # número de pedidos
}).rename(columns={'product_price': 'revenue',
                   'freight_price': 'freight',
                   'order_id': 'orders'}).reset_index()

# Converter year_month de Period para datetime
monthly_summary['year_month'] = monthly_summary['year_month'].dt.to_timestamp()

plt.figure(figsize=(15, 6))
sns.lineplot(data=monthly_summary, x='year_month', y='revenue', marker='o', label='Receita')
sns.lineplot(data=monthly_summary, x='year_month', y='freight', marker='o', label='Frete')
sns.lineplot(data=monthly_summary, x='year_month', y='orders', marker='o', label='Pedidos')

plt.title('Séries Temporais Mensais')
plt.xlabel('Mês')
plt.ylabel('Valores')
plt.xticks(rotation=45)
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(figures_dir, "series_temporais_mensais.png"))
plt.close()

# ============================================================
# EDA – Heatmap de Correlação
# ============================================================

numeric_cols_corr = ['subtotal', 'discount', 'total', 'discount_abs', 'freight_price',
                     'delivery_lead_time', 'delivery_delay_days', 'is_late', 
                     'is_confirmed', 'freight_share', 'product_price']

for col in numeric_cols_corr:
    df[col] = pd.to_numeric(df[col], errors='coerce')

numeric_df = df[numeric_cols_corr].replace([float('inf'), -float('inf')], pd.NA).dropna()

corr_matrix = numeric_df.corr()

plt.figure(figsize=(12, 10))
sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap='coolwarm', cbar=True)
plt.title('Heatmap de Correlação entre Variáveis Numéricas')
plt.xticks(rotation=45)
plt.yticks(rotation=0)
plt.tight_layout()
plt.savefig(os.path.join(figures_dir, "heatmap_correlacao.png"))
plt.close()

# ============================================================
# EDA – KPIs agregados por categoria / subcategoria / tipo de serviço
# ============================================================

# Colunas de agrupamento existentes no seu DataFrame
group_cols_list = ['category', 'subcategory', 'delivery_service']

for group_col in group_cols_list:
    if group_col in df.columns:
        kpi_df = df.groupby(group_col).agg(
            total_orders=('order_id', 'count'),
            total_revenue=('product_price', 'sum'),
            avg_ticket=('product_price', 'mean'),
            avg_lead_time=('delivery_lead_time', 'mean'),
            total_discount=('discount_abs', 'sum'),
            avg_freight_share=('freight_share', 'mean'),
            pct_canceled=('is_confirmed', lambda x: 100 * (x == 0).sum() / x.count()),
            pct_late=('is_late', lambda x: 100 * (x == 1).sum() / x.count())
        ).reset_index()
        
        # Ordenar por total_revenue
        kpi_df = kpi_df.sort_values(by='total_revenue', ascending=False)
        
        # Salvar tabela
        output_path = os.path.join(tables_dir, f"kpis_{group_col}.csv")
        kpi_df.to_csv(output_path, index=False)
        
        print(f"✅ KPIs agregados por '{group_col}' salvos em: {output_path}")
    else:
        print(f"⚠️ Coluna '{group_col}' não existe no DataFrame e foi ignorada.")

# ============================================================
# Visualização Gráfica dos KPIs
# ============================================================

import matplotlib.ticker as mtick

for group_col in group_cols_list:
    # Carregar KPIs agregados
    kpi_path = os.path.join(tables_dir, f"kpis_{group_col}.csv")
    kpi_df = pd.read_csv(kpi_path)
    
    # Gráfico 1: Total de Receita
    plt.figure(figsize=(12, 6))
    sns.barplot(data=kpi_df, x=group_col, y='total_revenue', palette='Blues_d')
    plt.title(f'Total de Receita por {group_col}')
    plt.ylabel('Receita')
    plt.xlabel(group_col.capitalize())
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, f"total_revenue_{group_col}.png"))
    plt.close()
    
    # Gráfico 2: Ticket Médio
    plt.figure(figsize=(12, 6))
    sns.barplot(data=kpi_df, x=group_col, y='avg_ticket', palette='Greens_d')
    plt.title(f'Ticket Médio por {group_col}')
    plt.ylabel('Ticket Médio')
    plt.xlabel(group_col.capitalize())
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, f"avg_ticket_{group_col}.png"))
    plt.close()
    
    # Gráfico 3: % Cancelamentos e % Atrasos
    plt.figure(figsize=(12, 6))
    sns.barplot(data=kpi_df.melt(id_vars=[group_col], value_vars=['pct_canceled','pct_late']),
                x=group_col, y='value', hue='variable', palette=['red', 'orange'])
    plt.title(f'Percentual de Cancelamentos e Atrasos por {group_col}')
    plt.ylabel('Percentual (%)')
    plt.xlabel(group_col.capitalize())
    plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter())
    plt.xticks(rotation=45)
    plt.legend(title='')
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, f"pct_cancel_late_{group_col}.png"))
    plt.close()
    
    print(f"✅ Gráficos de KPIs para '{group_col}' salvos em {figures_dir}")

# ============================================================
# Inferência Estatística
# ============================================================

import scipy.stats as stats
import numpy as np

# Função para calcular IC 95%
def confidence_interval(data, confidence=0.95):
    data_clean = data.dropna()
    n = len(data_clean)
    mean = np.mean(data_clean)
    sem = stats.sem(data_clean)  # Erro padrão da média
    h = sem * stats.t.ppf((1 + confidence) / 2., n-1)
    return mean, mean-h, mean+h

# Ticket médio
ticket_mean, ticket_lower, ticket_upper = confidence_interval(df['product_price'])
print(f"Ticket médio: {ticket_mean:.2f} | IC 95%: [{ticket_lower:.2f}, {ticket_upper:.2f}]")

# Atraso médio (lead time)
lead_mean, lead_lower, lead_upper = confidence_interval(df['delivery_lead_time'])
print(f"Atraso médio: {lead_mean:.2f} dias | IC 95%: [{lead_lower:.2f}, {lead_upper:.2f}] dias")

# Proporção de cancelamentos
pct_cancel = df['is_confirmed'].eq(0).mean() * 100
# IC para proporção usando distribuição normal
n = len(df)
se_cancel = np.sqrt(pct_cancel/100 * (1 - pct_cancel/100) / n)
z = stats.norm.ppf(0.975)
pct_cancel_lower = pct_cancel - z*se_cancel*100
pct_cancel_upper = pct_cancel + z*se_cancel*100
print(f"Proporção de cancelamentos: {pct_cancel:.2f}% | IC 95%: [{pct_cancel_lower:.2f}%, {pct_cancel_upper:.2f}%]")

# Proporção de atrasos
pct_late = df['is_late'].mean() * 100
se_late = np.sqrt(pct_late/100 * (1 - pct_late/100) / n)
pct_late_lower = pct_late - z*se_late*100
pct_late_upper = pct_late + z*se_late*100
print(f"Proporção de atrasos: {pct_late:.2f}% | IC 95%: [{pct_late_lower:.2f}%, {pct_late_upper:.2f}%]")

# ============================================================
# Testes de normalidade (Shapiro-Wilk)
# ============================================================

# Ticket
stat_ticket, p_ticket = stats.shapiro(df['product_price'].dropna())
print(f"Shapiro-Wilk Ticket: stat={stat_ticket:.4f}, p={p_ticket:.4f}")

# Atraso
stat_lead, p_lead = stats.shapiro(df['delivery_lead_time'].dropna())
print(f"Shapiro-Wilk Lead Time: stat={stat_lead:.4f}, p={p_lead:.4f}")

# Interpretação:
# p > 0.05 -> dados seguem distribuição normal
# p <= 0.05 -> rejeita hipótese de normalidade

# ============================================================
# Visualização das distribuições com curva normal
# ============================================================
# -> Cole o código que te passei aquiimport matplotlib.pyplot as plt 
import seaborn as sns
import numpy as np
from scipy.stats import norm

# Configurações de estilo
sns.set(style="whitegrid")
sns.set_context("talk")

# ============================================================
# Ticket médio
# ============================================================
ticket_data = df['product_price'].dropna()
ticket_mean = ticket_data.mean()
ticket_std = ticket_data.std()

plt.figure(figsize=(10, 6))
sns.histplot(ticket_data, bins=30, kde=False, color='skyblue', stat='density', label='Dados')
# Curva normal teórica
x = np.linspace(ticket_data.min(), ticket_data.max(), 100)
plt.plot(x, norm.pdf(x, ticket_mean, ticket_std), color='red', lw=2, label='Curva Normal')
plt.title('Distribuição do Ticket Médio')
plt.xlabel('Ticket')
plt.ylabel('Densidade')
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(figures_dir, "distribuicao_ticket_normal.png"))
plt.close()

# ============================================================
# Lead time (atraso médio)
# ============================================================
lead_data = df['delivery_lead_time'].dropna()
lead_mean = lead_data.mean()
lead_std = lead_data.std()

plt.figure(figsize=(10, 6))
sns.histplot(lead_data, bins=30, kde=False, color='lightgreen', stat='density', label='Dados')
# Curva normal teórica
x = np.linspace(lead_data.min(), lead_data.max(), 100)
plt.plot(x, norm.pdf(x, lead_mean, lead_std), color='red', lw=2, label='Curva Normal')
plt.title('Distribuição do Lead Time')
plt.xlabel('Lead Time (dias)')
plt.ylabel('Densidade')
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(figures_dir, "distribuicao_leadtime_normal.png"))
plt.close()

# ============================================================
# Testes de Independência - Séries Temporais
# ============================================================

from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.stats.diagnostic import acorr_ljungbox

time_series_cols = ['revenue', 'orders', 'freight']

for col in time_series_cols:
    series = monthly_summary[col]
    n_points = len(series)
    
    # Definir lags menor que o tamanho da série
    lags = min(12, n_points - 1)
    
    if lags < 1:
        print(f"⚠️ Série {col} muito curta para teste de autocorrelação.")
        continue
    
    # --- Autocorrelação ---
    plt.figure(figsize=(10,6))
    plot_acf(series, lags=lags, alpha=0.05)
    plt.title(f"Autocorrelação de {col.capitalize()} Mensal")
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, f"acf_{col}.png"))
    plt.close()
    
    # --- Teste de Ljung-Box ---
    ljung_result = acorr_ljungbox(series, lags=[lags], return_df=True)
    print(f"\nLjung-Box Test para {col.capitalize()} ({lags} lags):")
    print(ljung_result)
    
    # Interpretação automática
    p_value = ljung_result['lb_pvalue'].values[0]
    if p_value > 0.05:
        print(f"✅ {col.capitalize()}: não há evidência de autocorrelação (aprox. independente).")
    else:
        print(f"⚠️ {col.capitalize()}: há autocorrelação significativa (dependência temporal).")
