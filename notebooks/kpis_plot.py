import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from config.paths import FIGURES_DIR, TABLES_DIR

sns.set(style="whitegrid")
sns.set_context("talk")


def improve_labels(ax):
    """Ajusta rótulos, títulos e layout para melhor legibilidade."""
    ax.set_xlabel(ax.get_xlabel().capitalize(), fontsize=14)
    ax.set_ylabel(ax.get_ylabel(), fontsize=14)
    ax.set_title(ax.get_title(), fontsize=18, pad=20)
    plt.xticks(rotation=30, ha='right', fontsize=12)
    plt.yticks(fontsize=12)
    plt.tight_layout()


def format_big_number(value):
    """Formata números grandes (K, M, B)."""
    if value >= 1_000_000_000:
        return f'{value/1_000_000_000:.1f}B'
    elif value >= 1_000_000:
        return f'{value/1_000_000:.1f}M'
    elif value >= 1_000:
        return f'{value/1_000:.0f}K'
    return str(value)


def annotate_bars(ax, horizontal):
    """Adiciona rótulos automáticos sem poluir o gráfico."""
    for p in ax.patches:
        value = p.get_width() if horizontal else p.get_height()
        if value == 0:
            continue
        if len(ax.patches) > 20:  # evitar poluição
            continue
        label = format_big_number(value)
        if horizontal:
            ax.annotate(label,
                        (value, p.get_y() + p.get_height()/2),
                        xytext=(8, 0),
                        textcoords="offset points",
                        va='center', fontsize=11)
        else:
            ax.annotate(label,
                        (p.get_x() + p.get_width()/2, value),
                        xytext=(0, 6),
                        textcoords="offset points",
                        ha='center', fontsize=11)


def plot_kpis(paths):
    """
    Gera gráficos de KPIs a partir dos CSVs produzidos por compute_kpis.
    paths: dict {group_col: csv_path}
    """
    for group_col, csv_path in paths.items():
        df = pd.read_csv(csv_path)
        horizontal = len(df[group_col].unique()) > 6

        # ===================== Total Revenue =====================
        plt.figure(figsize=(14,7))
        if horizontal:
            ax = sns.barplot(data=df, y=group_col, x='total_revenue', palette='Blues_r')
        else:
            ax = sns.barplot(data=df, x=group_col, y='total_revenue', palette='Blues_d')

        plt.title(f"Total de Receita por {group_col}", fontsize=20, pad=20)

        # Escala log se muito desbalanceado (mais robusta)
        if df['total_revenue'].max() > df['total_revenue'].median() * 30:
            if horizontal:
                ax.set_xscale("log")
                ax.set_xlabel("Total Revenue (escala log)", fontsize=14)
            else:
                ax.set_yscale("log")
                ax.set_ylabel("Total Revenue (escala log)", fontsize=14)

        annotate_bars(ax, horizontal)
        if not horizontal:
            plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(os.path.join(FIGURES_DIR, f"total_revenue_{group_col}.png"))
        plt.close()

        # ===================== Avg Ticket =====================
        plt.figure(figsize=(14,6))
        if horizontal:
            ax = sns.barplot(data=df, y=group_col, x='avg_ticket', palette='Greens_d')
        else:
            ax = sns.barplot(data=df, x=group_col, y='avg_ticket', palette='Greens_d')

        plt.title(f"Ticket Médio por {group_col}", fontsize=18)
        improve_labels(ax)
        plt.savefig(os.path.join(FIGURES_DIR, f"avg_ticket_{group_col}.png"))
        plt.close()

        # ===================== % Cancelamentos e % Atrasos =====================
        plt.figure(figsize=(14,6))
        melted = df.melt(
            id_vars=[group_col],
            value_vars=['pct_canceled', 'pct_late'],
            var_name='Indicador',
            value_name='Percentual'
        )
        melted['Indicador'] = melted['Indicador'].replace({
            'pct_canceled': 'Cancelamentos (%)',
            'pct_late': 'Atrasos (%)'
        })

        palette = {'Cancelamentos (%)': '#e63946', 'Atrasos (%)': '#1d3557'}

        ax = sns.barplot(data=melted, x=group_col, y='Percentual', hue='Indicador', palette=palette)

        # Formatar eixo Y em %
        ax.yaxis.set_major_formatter(mtick.PercentFormatter())

        # Rótulos das barras
        for container in ax.containers:
            ax.bar_label(container, fmt='%.1f%%', padding=3, fontsize=10)

        plt.xticks(rotation=45, ha='right')
        plt.title(f"Cancelamentos e Atrasos por {group_col}", fontsize=18)
        plt.legend(title="Indicador")
        improve_labels(ax)
        plt.tight_layout()
        plt.savefig(os.path.join(FIGURES_DIR, f"pct_cancel_late_{group_col}.png"))
        plt.close()