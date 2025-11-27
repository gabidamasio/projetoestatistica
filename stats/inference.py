import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

def confidence_interval(series, confidence=0.95):
    """
    Calcula IC para uma série numérica (média + t-Student).
    Retorna: (média, limite_inferior, limite_superior)
    """
    series_clean = series.dropna()
    n = len(series_clean)
    if n <= 1:
        return np.nan, np.nan, np.nan
    mean = series_clean.mean()
    sem = stats.sem(series_clean)
    h = sem * stats.t.ppf((1 + confidence) / 2., n-1)
    return mean, mean - h, mean + h

def compute_indicators_ci(df):
    mean_cols = ['product_price', 'delivery_lead_time']
    
    print("Intervalos de Confiança (95%):\n")
    
    # Médias
    print("--- IC para Médias (T-Student) ---")
    means, lowers, uppers, names = [], [], [], []
    
    for col in mean_cols:
        if col not in df.columns:
            print(f"⚠️ Coluna '{col}' não encontrada.")
            continue

        mean, lower, upper = confidence_interval(df[col])
        name = 'Ticket médio' if col == 'product_price' else 'Atraso médio'
        units = ' dias' if col == 'delivery_lead_time' else ''
        print(f"{name}: {mean:.2f}{units} | IC 95%: [{lower:.2f}{units}, {upper:.2f}{units}]")
        
        means.append(mean)
        lowers.append(lower)
        uppers.append(upper)
        names.append(name)
    
    # Gráfico de médias
    plt.figure(figsize=(8,5))
    plt.bar(names, means, 
            yerr=[np.array(means)-np.array(lowers), np.array(uppers)-np.array(means)],
            capsize=5, color='skyblue')
    for i, val in enumerate(means):
        plt.text(i, val + 0.02*val, f"{val:.2f}", ha='center', va='bottom')
    plt.title("Médias com Intervalo de Confiança 95%")
    plt.ylabel("Valor")
    plt.ylim(0, max(uppers)*1.1)
    plt.tight_layout()
    plt.close()
    
    # Proporções
    print("\n--- IC para Proporções (Aprox. Normal) ---")
    n = len(df)
    z = stats.norm.ppf(0.975)
    
    pct_cancel = df['is_confirmed'].eq(0).mean()
    se_cancel = np.sqrt(pct_cancel * (1 - pct_cancel) / n)
    lower_cancel = max(0, (pct_cancel - z * se_cancel) * 100)
    upper_cancel = min(100, (pct_cancel + z * se_cancel) * 100)
    print(f"Proporção de cancelamentos: {pct_cancel*100:.2f}% | IC 95%: [{lower_cancel:.2f}%, {upper_cancel:.2f}%]")

    pct_late = df['is_late'].mean()
    se_late = np.sqrt(pct_late * (1 - pct_late) / n)
    lower_late = max(0, (pct_late - z * se_late) * 100)
    upper_late = min(100, (pct_late + z * se_late) * 100)
    print(f"Proporção de atrasos: {pct_late*100:.2f}% | IC 95%: [{lower_late:.2f}%, {upper_late:.2f}%]")

    prop_names = ['Cancelamentos', 'Atrasos']
    prop_means = [pct_cancel*100, pct_late*100]
    prop_lowers = [lower_cancel, lower_late]
    prop_uppers = [upper_cancel, upper_late]

    # Gráfico de proporções
    plt.figure(figsize=(8,5))
    plt.bar(prop_names, prop_means,
            yerr=[np.array(prop_means)-np.array(prop_lowers), np.array(prop_uppers)-np.array(prop_means)],
            capsize=5, color='lightcoral')
    for i, val in enumerate(prop_means):
        plt.text(i, val + 0.5, f"{val:.2f}%", ha='center', va='bottom')  # deslocamento acima das barras
    plt.title("Proporções com Intervalo de Confiança 95%")
    plt.ylabel("Percentual (%)")
    plt.ylim(0, max(prop_uppers)*1.1)
    plt.tight_layout()
    plt.close()