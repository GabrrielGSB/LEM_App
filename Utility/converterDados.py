import pandas as pd
import matplotlib.pyplot as plt
import sys
import os

def processar_csv(input_csv, escala):
    """
    Processa CSV com dados de ângulo e deslocamento, gera força e salva CSV transformado.

    Parâmetros:
        input_csv (str): Caminho do arquivo CSV de entrada.
        escala (int): Escala usada na medição (50, 100, 200).
    """

    # Lê nomes das colunas da primeira linha e os dados a partir da segunda
    with open(input_csv, 'r') as f:
        nomes_colunas = f.readline().strip().split(',')

    df = pd.read_csv(input_csv, skiprows=1, names=nomes_colunas)

    # Verificações básicas
    if "kalman_angle_roll" not in df.columns or "time" not in df.columns:
        raise ValueError("CSV precisa conter as colunas 'kalman_angle_roll' e 'time'.")

    if "analogRule" not in df.columns:
        raise ValueError("CSV precisa conter a coluna 'deslocamento'.")

    # --- Conserta os ângulos ---
    df["kalman_angle_ro_ll"] = df["kalman_angle_roll"] - df["kalman_angle_roll"].iloc[1]
    df["kalman_angle_roll"] = df["kalman_angle_roll"].abs()

    # --- Calcula a força (N) ---
    if escala == 50:
        df["Forca (N)"] = ((df["kalman_angle_roll"] * 1.0363) + 0.0414) / 2
    elif escala == 100:
        df["Forca (N)"] = ((df["kalman_angle_roll"] * 1.0363) + 0.0414)
    elif escala == 200:
        df["Forca (N)"] = ((df["kalman_angle_roll"] * 1.0363) + 0.0414) * 2
    else:
        raise ValueError("A escala utilizada é inválida.")

    # --- Aplica constante ao deslocamento ---
    constante_desloc = 0.01
    df["Deslocamento (mm)"] = df["analogRule"] * constante_desloc

    # --- Seleciona colunas relevantes ---
    df_filtrado = df[["time", "Forca (N)", "Deslocamento (mm)"]]

    # --- Salva novo CSV ---
    output_csv = os.path.splitext(input_csv)[0] + "_transformado.csv"
    df_filtrado.to_csv(output_csv, index=False)
    print(f"Arquivo salvo como: {output_csv}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python converterDados.py <arquivo_csv> <escala> [constante_desloc]")
        sys.exit(1)

    arquivo = sys.argv[1]
    escala = int(sys.argv[2])

    processar_csv(arquivo, escala)
