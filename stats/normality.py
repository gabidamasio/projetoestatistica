import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import shapiro, norm
import os
# Assumindo que 'config.paths' existe e contém FIGURES_DIR
from config.paths import FIGURES_DIR 

sns.set(style="whitegrid")
sns.set_context("talk")

# =========================
# Teste de Normalidade (Shapiro-Wilk)
# =========================
def normality_test(series):
    """
    Teste de normalidade Shapiro-Wilk.
    Retorna: (estatística, p-value)
    """
    series_clean = series.dropna()
    # Verifica tamanho da amostra (Shapiro-Wilk é ideal para N <= 5000)
    if len(series_clean) < 3:
        return np.nan, np.nan
    
    # Limita N para testes grandes, onde p-value tende a ser zero
    if len(series_clean) > 5000:
        series_clean = series_clean.sample(5000, random_state=42)
        
    stat, p = shapiro(series_clean)
    return stat, p


def check_normality(df):
    """
    Aplica Shapiro-Wilk aos indicadores do dataset e imprime resultados.
    """
    print("\n===== Testes de Normalidade (Shapiro-Wilk) =====")
    indicators = {
        'Ticket Médio': 'product_price',
        'Lead Time': 'delivery_lead_time'
    }

    for name, col in indicators.items():
        if col not in df.columns:
            print(f"{name}: coluna '{col}' não encontrada.")
            continue

        stat, p = normality_test(df[col])
        if np.isnan(stat):
            print(f"⚠️ {name}: Dados insuficientes para o teste.")
            continue

        print(f"{name}: stat={stat:.4f}, p={p:.4f}")
        if p > 0.05:
            print(f"✅ {name}: dados seguem distribuição normal (p > 0.05)")
        else:
            print(f"⚠️ {name}: rejeita hipótese de normalidade (p ≤ 0.05)")
        print("-" * 10)


# =========================
# Plot Distribuição + Curva Normal
# =========================
def plot_distribution(series, name, color='skyblue', filename=''):
    """
    Plota histograma com curva normal teórica sobreposta e salva o arquivo.
    """
    series_clean = series.dropna()
    mu, sigma = series_clean.mean(), series_clean.std()
    
    plt.figure(figsize=(10,6))
    sns.histplot(series_clean, bins=30, kde=False, color=color, stat='density', label='Dados')
    
    # Curva normal teórica
    x = np.linspace(series_clean.min(), series_clean.max(), 100)
    plt.plot(x, norm.pdf(x, mu, sigma), color='red', lw=2, label='Curva Normal')
    
    plt.title(f'Distribuição de {name}', fontsize=18)
    plt.xlabel(name, fontsize=14)
    plt.ylabel('Densidade', fontsize=14)
    plt.legend()
    plt.tight_layout()
    
    # Salva arquivo se filename fornecido
    if filename:
        plt.savefig(os.path.join(FIGURES_DIR, filename))
        print(f"🖼️ Gráfico de distribuição '{name}' salvo em {FIGURES_DIR}")
    
    plt.close()  # Evita exibição em pipeline automatizado


def check_and_plot_normality(df):
    """
    Combina teste de normalidade e plot de distribuição.
    """
    # Executa todos os testes e imprime resultados
    check_normality(df)
    
    # Plota os gráficos individualmente
    indicators = {
        'Ticket Médio': ('product_price', 'skyblue', "distribuicao_ticket_normal.png"),
        'Lead Time': ('delivery_lead_time', 'lightgreen', "distribuicao_leadtime_normal.png")
    }

    print("\n===== Visualização de Distribuição e Curva Normal =====")
    for name, (col, color, filename) in indicators.items():
        if col in df.columns:
            plot_distribution(df[col], name, color, filename)
        else:
            print(f"⚠️ {name}: coluna '{col}' não encontrada para plotagem.")