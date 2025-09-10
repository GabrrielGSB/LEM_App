import csv
import matplotlib.pyplot as plt
import os
import time as t

# Função para carregar os dados do CSV
def carregarCSV(file_path):
    times = []
    angle_rolls = []
    angle_pitchs = []

    with open(file_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                times       .append(float(row['Tempo']))
                angle_rolls .append(float(row['angle_roll']))
                angle_pitchs.append(float(row['angle_pitch']))
            except ValueError:
                continue

    return times, angle_rolls, angle_pitchs

def monitorar_csv(file_path):
    # Inicializa as listas para armazenar os dados
    dadosX, dadoY = [], []

    # Posiciona o ponteiro do arquivo no final
    with open(file_path, mode='r') as file:
        file.seek(0, 0)  # Move o ponteiro para o final do arquivo (modo 'r')
        
        while True:
            current_position = file.tell()  # Pega a posição atual do ponteiro
            
            with open(file_path, mode='r') as file_read:
                file_read.seek(current_position)  # Começa a leitura a partir da posição anterior
                
                reader = csv.DictReader(file_read)
                for row in reader:
                    try:
                        # Processa os novos dados
                        dadosX.append(float(row['Tempo']))
                        dadoY.append(float(row['angle_roll']))
                    except ValueError:
                        continue

            # Pausa para evitar loop contínuo
            t.sleep(1)  # Aguarda 1 segundo antes de verificar novamente o arquivo

def carregarCSVteste(caminhoArquivo):
    dadosX, dadosY = [], []

    with open(caminhoArquivo, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                dadosX.append(float(row['Pontos_no_Eixo X']))
                dadosY.append(float(row['Pontos_no_Eixo Y']))
                # print(float(row['Pontos_no_Eixo X']), float(row['Pontos_no_Eixo Y']))
            except ValueError:
                continue
    return dadosX, dadosY
    
# Função para plotar os dados
def plotarDadosCSV(times, angle_rolls, angle_pitchs):
    print("\n--- Configurações de Plotagem ---")
    print("1. Plotar tudo")
    print("2. Plotar apenas uma parte dos dados")
    print("3. Mudar título, legendas e salvar o gráfico")
    option = int(input("Escolha uma opção: "))

    # Configuração padrão
    start_index = 0
    end_index = len(times)
    title = "Gráfico"
    x_label = "Time (s)"
    y_label = "Values"
    show_legend = True

    # Opção 2: Plotar uma parte dos dados
    if option == 2:
        start_index = int(input(f"Início do intervalo (0 a {len(times)-1}): "))
        end_index = int(input(f"Fim do intervalo (1 a {len(times)}): "))

    # Opção 3: Personalizar
    if option == 3:
        title = input("Digite o título do gráfico: ")
        x_label = input("Digite o rótulo do eixo X: ")
        y_label = input("Digite o rótulo do eixo Y: ")
        show_legend = input("Exibir legendas? (s/n): ").strip().lower() == 's'

    # Plotagem
    plt.figure(figsize=(10, 6))
    plt.plot(times[start_index:end_index], angle_rolls[start_index:end_index], label="Angle Roll", color='blue')
    plt.plot(times[start_index:end_index], angle_pitchs[start_index:end_index], label="Angle Pitch", color='green')

    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)

    if show_legend:
        plt.legend()
    plt.grid(True)

    # Opção de salvar como PNG
    save_option = input("Deseja salvar o gráfico como PNG? (s/n): ").strip().lower()
    if save_option == 's':
        output_path = input("Digite o nome do arquivo (sem extensão): ") + ".png"
        plt.savefig(output_path, format='png')
        print(f"Gráfico salvo como {os.path.abspath(output_path)}")

    plt.show()

# def plotarDadosCSVteste():

# # Caminho do arquivo CSV
# csv_file = input("Digite o caminho do arquivo CSV: ")

# # Verificar se o arquivo existe
# if os.path.exists(csv_file):
#     times, angle_rolls, angle_pitchs = carregarCSV(csv_file)
#     plot_data(times, angle_rolls, angle_pitchs)
# else:
#     print(f"Arquivo {csv_file} não encontrado!")