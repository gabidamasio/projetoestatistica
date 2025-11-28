
# E-commerce Analysis

Este projeto realiza uma **análise exploratória e estatística** de dados de um e-commerce brasileiro, com foco em KPIs como receita, frete, ticket médio, atraso de entregas e comportamento do cliente. O objetivo é gerar insights acionáveis para o negócio, utilizando **Python, Pandas, Seaborn, Matplotlib e SQL**.

---

## 1. Requisitos e instalação

Para garantir a **reprodutibilidade**, todas as dependências estão listadas em `requirements.txt`.

Instale as dependências utilizando:

```bash
pip install -r requirements.txt
````

---

## 2. Estrutura do Projeto `ecommerce_analysis`

```text
ecommerce_analysis/
├── config/                     # Configurações gerais, como paths, constantes, etc.
├── data/                       # Módulos para manipulação e transformação de dados
│   ├── __init__.py
│   ├── feature_engineering.py  # Funções para criar features derivadas
│   ├── load_data.py            # Função para carregar CSVs ou outras fontes
│   ├── processed/              # Armazena dados processados pelo pipeline
│   ├── raw/                    # Dados brutos originais
│   └── __pycache__/            # Cache do Python
├── notebooks/                  # Funções de análise exploratória e gráficos
├── outputs/                    # Resultados do pipeline
│   ├── figures/                # Gráficos gerados pelo pipeline
│   └── tables/                 # Tabelas geradas pelo pipeline
├── sql/                        # Scripts SQL ou consultas
├── stats/                      # Funções estatísticas
│   ├── inference.py            # Cálculo de IC, médias e proporções
│   ├── normality.py            # Testes e gráficos de normalidade
│   └── independence_tests.py   # Testes de autocorrelação, independência, etc.
├── venv/                       # Ambiente virtual Python
├── .gitignore                   # Arquivos e pastas ignoradas pelo Git
├── main.py                      # Script principal do pipeline
├── README.md                    # Documentação do projeto
└── requirements.txt             # Dependências do projeto
```

---

## 3. Como usar

1. Coloque os arquivos CSV originais em `data/raw/e-commerce_projeto_est/`.
2. Execute os notebooks em `notebooks/` para:

   * Limpeza e preparação dos dados
   * Engenharia de features
   * Análise exploratória (EDA)
   * Inferência estatística
3. Resultados (gráficos, tabelas) serão salvos automaticamente em `outputs/`.

---

## 4. KPIs analisados

* Receita, subtotal, frete, desconto médio (%), ticket médio
* Take-rate de frete (P_Service/Total)
* Prazo de entrega, atraso
* Conversão de pagamento por tipo de pagamento
* Performance logística por tipo de serviço (Standard, Same-Day, Scheduled)
* Mix por Category/Subcategory e elasticidade vs desconto
* Sazonalidade por mês, UF e região

---

## 5. Observações

* Todas as análises são replicáveis através do notebook Python e das queries SQL.
* Pastas `outputs/` e `processed/` não devem ser versionadas no Git se forem muito grandes, use `.gitignore`.
