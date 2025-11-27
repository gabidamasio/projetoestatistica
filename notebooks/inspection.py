def inspect_dataset(df):
    print("===== 5 primeiras linhas =====")
    print(df.head())

    print("\n===== Info geral =====")
    print(df.info())

    print("\n===== Estatísticas descritivas =====")
    print(df.describe())

    print("\n===== Valores ausentes =====")
    print(df.isna().sum())
