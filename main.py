import os
from data.load_data import load_csv
from data.feature_engineering import apply_feature_engineering

from notebooks.histograms_boxplots import plot_histograms_and_boxplots
from notebooks.correlations import plot_correlation
from notebooks.time_series import analyze_time_series
from notebooks.kpis import compute_kpis
from notebooks.kpis_plot import plot_kpis

# Estatística e gráficos
from stats.inference import compute_indicators_ci
from stats.normality import check_and_plot_normality
from stats.independence_tests import test_autocorrelation


def main():

    # 1. Carregar dados
    df = load_csv()

    # 2. Feature Engineering
    df = apply_feature_engineering(df)

    # 3. EDA
    plot_histograms_and_boxplots(df)
    plot_correlation(df)

    # 4. Séries temporais
    monthly_summary = analyze_time_series(df)

    # 5. Indicadores com IC
    compute_indicators_ci(df)

    # 6. Teste de normalidade e plot de distribuição
    check_and_plot_normality(df)

    # 7. Teste de autocorrelação para séries mensais
    print("\n===== Teste de Autocorrelação =====")
    for col in ['revenue', 'orders', 'freight']:
        test_autocorrelation(monthly_summary[col], col)

    # 8. KPIs
    kpis = compute_kpis(df)
    plot_kpis(kpis)

    print("\nPipeline concluído.")


if __name__ == "__main__":
    main()