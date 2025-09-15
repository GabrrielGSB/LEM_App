import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def aplicar_filtros_csv(nome_arquivo, colunas_alvo, janela=100, metodo_csv='ponderada_gaussiana', salvar_arquivo='dados_KMm.csv', plotar=True):
    """
    Aplica filtros de média móvel (simples e ponderadas) em colunas de um arquivo CSV.
    
    Parâmetros:
        nome_arquivo (str): Caminho para o arquivo CSV de entrada.
        colunas_alvo (list): Lista de nomes das colunas a serem filtradas.
        janela (int): Tamanho da janela da média móvel.
        metodo_csv (str): Método de filtro para salvar no CSV. Pode ser 'simples' ou:
                          'ponderada_linear', 'ponderada_invertida', 'ponderada_exponencial',
                          'ponderada_central', 'ponderada_gaussiana'.
        salvar_arquivo (str): Caminho para o arquivo CSV de saída.
        plotar (bool): Se True, exibe gráficos com os filtros aplicados.
    """

    # Carrega dados
    df = pd.read_csv(nome_arquivo)

    # ---------- Operação extra para angle_roll ----------
    if "angle_roll" in df.columns:
        df["angle_roll"] = (df["angle_roll"] - df["angle_roll"].iloc[1]).abs()

    # Funções de pesos
    def gerar_pesos(janela, tipo):
        if tipo == 'linear':
            return np.arange(1, janela + 1)
        elif tipo == 'invertida':
            return np.arange(janela, 0, -1)
        elif tipo == 'exponencial':
            return np.exp(np.linspace(0, 2, janela))
        elif tipo == 'central':
            centro = (janela - 1) / 2
            return 1 / (1 + np.abs(np.arange(janela) - centro))
        elif tipo == 'gaussiana':
            x = np.linspace(-1, 1, janela)
            sigma = 0.4
            return np.exp(-0.5 * (x / sigma)**2)
        else:
            raise ValueError("Tipo de peso inválido")

    def weighted_moving_average(dados, pesos):
        return np.dot(dados, pesos) / pesos.sum()

    tipos_pesos = {'linear':      'ponderada_linear',
                   'invertida':   'ponderada_invertida',
                   'exponencial': 'ponderada_exponencial',
                   'central':     'ponderada_central',
                   'gaussiana':   'ponderada_gaussiana'}

    for coluna in colunas_alvo:
        if coluna not in df.columns:
            print(f"[AVISO] Coluna '{coluna}' não encontrada no arquivo.")
            continue

        if plotar:
            plt.figure(figsize=(12, 6))
            plt.plot(df['time'], df[coluna], label='Original', linewidth=1, alpha=0.6)

        col_simples = f'{coluna}_media_simples'
        df[col_simples] = df[coluna].rolling(window=janela, center=True).mean()
        if plotar:
            plt.plot(df['time'], df[col_simples], label='Média Móvel Simples', linewidth=1.2)

        for tipo, nome_sufixo in tipos_pesos.items():
            pesos = gerar_pesos(janela, tipo)
            col_nome = f'{coluna}_media_{nome_sufixo}'
            df[col_nome] = df[coluna].rolling(window=janela, center=True)\
                            .apply(lambda x: weighted_moving_average(x, pesos), raw=True)
            if plotar:
                plt.plot(df['time'], df[col_nome], label=f'Média {tipo.capitalize()}', linestyle='--', linewidth=1.5)

        if plotar:
            plt.title(f'Filtro - {coluna}')
            plt.xlabel('Tempo')
            plt.ylabel('Valor')
            plt.legend()
            plt.grid(True)
            plt.tight_layout()
            plt.show()

    # Seleção para salvar no CSV
    colunas_para_salvar = ['time']
    for col in colunas_alvo:
        colunas_para_salvar.append(col)
        if metodo_csv == 'simples':
            colunas_para_salvar.append(f'{col}_media_simples')
        else:
            colunas_para_salvar.append(f'{col}_media_{metodo_csv}')

    df_filtrado = df[colunas_para_salvar]
    df_filtrado.to_csv(salvar_arquivo, index=False)
    print(f"[✓] CSV salvo como '{salvar_arquivo}' usando método '{metodo_csv}' com janela={janela}.")
