import os
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.stats.diagnostic import acorr_ljungbox
from config.paths import FIGURES_DIR

def test_autocorrelation(series, name, max_lags=24, standardize=True):
    """
    Testa autocorrelação de uma série temporal:
    - Plota ACF (Autocorrelation Function) com escala própria
    - Aplica teste de Ljung-Box
    - Retorna um dicionário com resultados
    
    Parâmetros:
    - series: pd.Series
    - name: nome da série (str)
    - max_lags: número máximo de lags para o ACF
    - standardize: se True, padroniza a série (z-score) para evitar escalas diferentes
    """
    series_clean = series.dropna()
    n_points = len(series_clean)
    
    if n_points < 2:
        print(f"⚠️ Série '{name}' muito curta para análise de autocorrelação.")
        return None

    # Padronização opcional
    if standardize:
        series_clean = (series_clean - series_clean.mean()) / series_clean.std()

    # Define lags
    lags = min(max_lags, n_points - 1)

    # =========================
    # Criar diretório caso não exista
    # =========================
    os.makedirs(FIGURES_DIR, exist_ok=True)

    # =========================
    # Plot ACF
    # =========================
    plt.figure(figsize=(10, 6))
    plot_acf(series_clean, lags=lags, alpha=0.05, zero=False)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.title(f"Autocorrelação de {name}", fontsize=16)
    plt.xlabel("Lag")
    plt.ylabel("Autocorrelação")
    plt.tight_layout()
    acf_path = os.path.join(FIGURES_DIR, f"acf_{name}.png")
    plt.savefig(acf_path)
    plt.close()
    print(f"🖼️ Gráfico ACF de '{name}' salvo em {acf_path}")

    # =========================
    # Teste de Ljung-Box
    # =========================
    ljung_result = acorr_ljungbox(series_clean, lags=[lags], return_df=True)
    p_value = ljung_result['lb_pvalue'].values[0]

    print(f"\nLjung-Box Test para '{name}' ({lags} lags):")
    print(ljung_result)
    if p_value > 0.05:
        print(f"✅ {name}: não há evidência de autocorrelação significativa (aprox. independente).")
    else:
        print(f"⚠️ {name}: há autocorrelação significativa (dependência temporal).")

    return {
        'name': name,
        'p_value': p_value,
        'ljung_box_df': ljung_result,
        'acf_path': acf_path
    }