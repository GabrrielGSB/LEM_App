from All_imports import *
from Utility.classesAux import *
import pandas as pd
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QFileDialog, QMessageBox

salvarLinuxArquivoDados    = "Dados/dados_filtrados.csv"
salvarWindownsArquivoDados = "Dados\dados_filtrados.csv"

caminhoLinuxConverterDados = "Utility/converterDados.py"
caminhoWindownsConverterDados = "Utility\converterDados.py"

def aplicar_filtros_csv(nome_arquivo, colunas_alvo, janela=100, metodo_csv='ponderada_gaussiana', salvar_arquivo=salvarLinuxArquivoDados):
    """
    Aplica um filtro de média móvel (simples ou ponderada) em colunas de um arquivo CSV.

    Parâmetros:
        nome_arquivo (str): Caminho para o arquivo CSV de entrada.
        colunas_alvo (list): Lista de nomes das colunas a serem filtradas.
        janela (int): Tamanho da janela da média móvel.
        metodo_csv (str): Método de filtro a aplicar. Pode ser 'simples' ou:
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

    # Função para gerar pesos
    def gerar_pesos(janela, tipo):
        if   tipo == 'linear':      return np.arange(1, janela + 1)
        elif tipo == 'invertida':   return np.arange(janela, 0, -1)
        elif tipo == 'exponencial': return np.exp(np.linspace(0, 2, janela))
        elif tipo == 'central':     return 1 / (1 + np.abs(np.arange(janela) - (janela - 1) / 2))
        elif tipo == 'gaussiana':
            x = np.linspace(-1, 1, janela)
            sigma = 0.4
            return np.exp(-0.5 * (x / sigma)**2)
        else:
            raise ValueError("Tipo de peso inválido")

    # Função para média ponderada
    def weighted_moving_average(dados, pesos):
        return np.dot(dados, pesos) / pesos.sum()

    # Dicionário para mapear os tipos válidos
    tipos_pesos = {
        'ponderada_linear': 'linear',
        'ponderada_invertida': 'invertida',
        'ponderada_exponencial': 'exponencial',
        'ponderada_central': 'central',
        'ponderada_gaussiana': 'gaussiana'
    }

    for coluna in colunas_alvo:
        if coluna not in df.columns:
            continue

        # Nome da nova coluna com o filtro aplicado
        col_filtrada = f'{coluna}_filtrada'

        if metodo_csv == 'simples':
            # Média móvel simples
            df[col_filtrada] = df[coluna].rolling(window=janela, center=True).mean()
        elif metodo_csv in tipos_pesos:
            tipo_peso = tipos_pesos[metodo_csv]
            pesos = gerar_pesos(janela, tipo_peso)
            df[col_filtrada] = df[coluna].rolling(window=janela, center=True)\
                                         .apply(lambda x: weighted_moving_average(x, pesos), raw=True)
        else:
            raise ValueError(f"Método de filtro inválido: {metodo_csv}")

    # Seleção das colunas para salvar
    colunas_para_salvar = ['time']
    for col in colunas_alvo:
        if col in df.columns:
            colunas_para_salvar.append(col)
            colunas_para_salvar.append(f'{col}_filtrada')

    # Salvar CSV
    df_filtrado = df[colunas_para_salvar]
    df_filtrado.to_csv(salvar_arquivo, index=False)


filterMethod = None

class tab2(QWidget):
    def __init__(self, imagemFundo):
        super().__init__()

       ### MODIFICADO: Bloco de Calibração para Múltiplas Escalas ###
        # Agora armazenamos os dados de calibração em um dicionário,
        # onde a chave é a escala (50, 100, 200).
        # ---------------------------------------------------------------------
        # PASSO 1: Insira seus dados de calibração para CADA ESCALA aqui.
        # A unidade da força aqui é Toneladas, para corresponder ao seu gráfico.
        self.dados_calibracao = {
            50: {
                'angulos': np.array([1.1, 3.39, 8.2, 12.9]),
                'forcas':  np.array([1, 2, 4, 6])  # Força em Toneladas
            },
            100: {
                'angulos': np.array([0.9, 1.8, 3.6, 5.45]),
                'forcas':  np.array([1, 2, 4, 6])  # Força em Toneladas
            },
            200: {
                # ATENÇÃO: Adicione aqui os dados reais para a escala 200
                'angulos': np.array([0.5, 1.0, 2.0, 3.0]),
                'forcas':  np.array([1, 2, 4, 6])  # Força em Toneladas (DADOS DE EXEMPLO)
            }
        }
        # A função de conversão será criada dinamicamente, então a removemos daqui.
        # ---------------------------------------------------------------------

        ### NOVO: Bloco de Calibração 2: ANALOGRULE para DESLOCAMENTO ###
        # Este sistema é independente da escala de força.
        # ---------------------------------------------------------------------
        # PASSO 1B: Insira seus dados de calibração para o sensor analógico.
        # Ex: valores lidos do sensor e o deslocamento real correspondente em mm.
        self.calibracao_analog_rule = {
            'valores_raw':     np.array([250, 745, 1700, 4094]),  # Valores brutos lidos (ex: 0-1023)
            'deslocamento_mm': np.array([50, 100, 200, 400])      # Deslocamento real em mm
        }

        # PASSO 2B: Cria o modelo de conversão para o deslocamento.
        # Um polinômio de grau 1 (reta) geralmente é suficiente para sensores analógicos.
        try:
            dados_analog = self.calibracao_analog_rule
            # Usamos grau 1 para uma conversão linear. Mude para 2 se não for linear.
            coef_analog = np.polyfit(dados_analog['valores_raw'], dados_analog['deslocamento_mm'], 2)
            self.funcao_conversao_deslocamento = np.poly1d(coef_analog)
            print(">>> Função de calibração AnalogRule->Deslocamento criada com sucesso.")
            print(f">>> Equação: Deslocamento = {self.funcao_conversao_deslocamento}")
        except Exception as e:
            print(f"[ERRO] Falha ao criar a função de calibração de deslocamento: {e}")
            self.funcao_conversao_deslocamento = None
        # ---------------------------------------------------------------------


        self.dataPath = None

        # Plano de fundo---------------------------------------------------
        self.planoDeFundo = definirPlanoDeFundo(imagemFundo)
        self.planoDeFundo.setGeometry(0, 0, self.width(), self.height())

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.planoDeFundo)
        #------------------------------------------------------------------

        # Botão para selecionar CSV--------------------------------------------------
        self.selectCSVbutton = QPushButton("Selecionar Arquivo", self.planoDeFundo)
        self.selectCSVbutton.move(300, 50)
        self.selectCSVbutton.setFixedSize(400, 50)
        self.selectCSVbutton.setStyleSheet("""QPushButton {background-color: blue; 
                                                           color: white; 
                                                           font-size: 14px;
                                                           font-weight: bold; 
                                                           border-radius: 10px;}
                                            QPushButton:hover {background-color: lightblue;}""")
        self.selectCSVbutton.clicked.connect(self.openCSV)

        # Layout horizontal
        self.layout_h = QHBoxLayout()
        self.layout_h.addStretch()
        self.layout_h.addWidget(self.selectCSVbutton)
        self.layout_h.addStretch()
        self.layout_h.setParent(self.layout)
        self.layout.addLayout(self.layout_h)
        #----------------------------------------------------------------------------

        # Botão para abrir nova janela-------------------------------------------
        self.configButton = QPushButton("Aplicar Filtro", self.planoDeFundo)
        self.configButton.move(300, 130)
        self.configButton.setFixedSize(400, 50)
        self.configButton.setStyleSheet("""QPushButton {background-color: blue; 
                                                        color: white; font-size: 14px;
                                                        font-weight: bold; 
                                                        border-radius: 10px;}
                                            QPushButton:hover {background-color: lightblue;}""")
        self.configButton.clicked.connect(self.openConfigWindown)
        #------------------------------------------------------------------------

        # Botão para plotar o gráfico dados--------------------------------------
        self.botao_plotar = QPushButton("Plotar Gráfico Dados Brutos", self.planoDeFundo)
        self.botao_plotar.move(225, 350)
        self.botao_plotar.setFixedSize(250, 50)
        self.botao_plotar.setStyleSheet("""QPushButton {background-color: blue; 
                                                        color: white; font-size: 14px;
                                                        font-weight: bold; 
                                                        border-radius: 10px;}
                                            QPushButton:hover {background-color: lightgreen;}""")
        self.botao_plotar.clicked.connect(self.plotarGraficoDadosBrutos)
        #------------------------------------------------------------------------

        # Botão para plotar o gráfico tensão deformação--------------------------
        self.botao_plotar = QPushButton("Plotar Gráfico Tensão Deformação", self.planoDeFundo)
        self.botao_plotar.move(525, 350)
        self.botao_plotar.setFixedSize(250, 50)
        self.botao_plotar.setStyleSheet("""QPushButton {background-color: blue; 
                                                        color: white; font-size: 14px;
                                                        font-weight: bold; 
                                                        border-radius: 10px;}
                                            QPushButton:hover {background-color: lightgreen;}""")
        self.botao_plotar.clicked.connect(self.modificarEscala)
        # self.botao_plotar.clicked.connect(lambda: self.plotarGraficoTensaoDef())
        #------------------------------------------------------------------------

        # Label para mostrar nome do arquivo
        self.label = QLabel("")

        ### NOVO: Dropdown para selecionar a Escala ###
        self.label_escala = QLabel("Selecionar Escala:", self.planoDeFundo)
        self.label_escala.move(440, 230)
        self.label_escala.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")

        self.dropdown_escala = QComboBox(self.planoDeFundo)
        self.dropdown_escala.setGeometry(420, 250, 180, 30)
        # Adicionamos o texto visível e o dado numérico (50, 100, 200)
        self.dropdown_escala.addItem("Escala 50 Ton", 50)
        self.dropdown_escala.addItem("Escala 100 Ton", 100)
        self.dropdown_escala.addItem("Escala 200 Ton", 200)
        self.dropdown_escala.setStyleSheet("""QComboBox {background-color: #F0E68C; 
                                                border: 2px solid #DAA520;
                                                border-radius: 10px;
                                                padding: 5px; font-size: 14px; color: #8B4513;}""")

        
        # Dropdowns de seleção de eixo X e Y
        self.dropdown_x = QComboBox(self.planoDeFundo)
        self.dropdown_x.setGeometry(200, 310, 180, 30)

        if hasattr(self.dropdown_x, "setPlaceholderText"):
         self.dropdown_x.setPlaceholderText("Selecionar eixo X")
        else:
            # fallback: torna editável e usa lineEdit placeholder (readOnly pra evitar digitação)
            self.dropdown_x.setEditable(True)
            self.dropdown_x.lineEdit().setReadOnly(True)
            self.dropdown_x.lineEdit().setPlaceholderText("Selecionar eixo X")

        self.dropdown_x.setStyleSheet("""QComboBox {background-color: #ADD8E6;  
                                                    border: 2px solid #1E90FF;  
                                                    border-radius:    10px;
                                                    padding:          5px;
                                                    font-size:        14px;
                                                    color:            #000080;}
                                                                            
                                         QComboBox:hover {background-color: #BFEFFF;}
                                                                            
                                         QComboBox::drop-down {bself.botao_plotar.clicked.connect(self.plotarGrafico)order:     none;
                                                               background: transparent;
                                                               width:      25px;}
                                                                            
                                         QComboBox QAbstractItemView {border:                     1px solid #87CEFA;
                                                                      selection-background-color: #B0E0E6;
                                                                      background-color:           white;
                                                                      font-size:                  14px;}""")

        self.dropdown_y = QComboBox(self.planoDeFundo)
        self.dropdown_y.setGeometry(420, 310, 180, 30)

        if hasattr(self.dropdown_y, "setPlaceholderText"):
         self.dropdown_y.setPlaceholderText("Selecionar eixo Y")
        else:
            self.dropdown_y.setEditable(True)
            self.dropdown_y.lineEdit().setReadOnly(True)
            self.dropdown_y.lineEdit().setPlaceholderText("Selecionar eixo Y")

        self.dropdown_y.setStyleSheet("""QComboBox {background-color: #ADD8E6;  
                                                    border: 2px solid #1E90FF;  
                                                    border-radius:    10px;
                                                    padding:          5px;
                                                    font-size:        14px;
                                                    color:            #000080;}
                                                                            
                                         QComboBox:hover {background-color: #BFEFFF;}
                                                                            
                                         QComboBox::drop-down {border:     none;
                                                               background: transparent;
                                                               width:      25px;}
                                                                            
                                         QComboBox QAbstractItemView {border:                     1px solid #87CEFA;
                                                                      selection-background-color: #B0E0E6;
                                                                      background-color:           white;
                                                                      font-size:                  14px;}""")
        
                        # Dropdown para segundo eixo Y
        
        self.dropdown_y2 = QComboBox(self.planoDeFundo)
        self.dropdown_y2.setGeometry(640, 310, 180, 30)
        if hasattr(self.dropdown_y2, "setPlaceholderText"):
         self.dropdown_y2.setPlaceholderText("Selecionar 2° eixo Y")
        else:
            self.dropdown_y2.setEditable(True)
            self.dropdown_y2.lineEdit().setReadOnly(True)
            self.dropdown_y2.lineEdit().setPlaceholderText("Selecionar 2° eixo Y")

        self.dropdown_y2.setStyleSheet("""QComboBox {background-color: #ADD8E6;  
                                                    border: 2px solid #1E90FF;  
                                                    border-radius:    10px;
                                                    padding:          5px;
                                                    font-size:        14px;
                                                    color:            #000080;}
                                                                            
                                         QComboBox:hover {background-color: #BFEFFF;}
                                                                            
                                         QComboBox::drop-down {border:     none;
                                                               background: transparent;
                                                               width:      25px;}
                                                                            
                                         QComboBox QAbstractItemView {border:                     1px solid #87CEFA;
                                                                      selection-background-color: #B0E0E6;
                                                                      background-color:           white;
                                                                      font-size:                  14px;}""")

        # Inicialmente desabilita até o CSV ser carregado
        self.dropdown_x.setEnabled(False)
        self.dropdown_y.setEnabled(False)
        self.dropdown_y2.setEnabled(False)


    def openCSV(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Selecionar arquivo CSV", "", "Arquivos CSV (*.csv);;Todos os arquivos (*)")

        if file_name:
            self.dataPath = file_name
            base_name = os.path.basename(file_name)
            self.label.setText(f"Arquivo selecionado: {base_name}")
            self.label.move(300,100)
            self.label.setStyleSheet("color: white; font-size: 18px;")
            self.label.adjustSize()

            for i in reversed(range(self.layout_h.count())):
                widget_item = self.layout_h.itemAt(i)
                if widget_item.widget():
                    self.layout_h.removeWidget(widget_item.widget())

            self.layout_h.addWidget(self.selectCSVbutton)
            self.layout_h.addWidget(self.label)

            # Carregar colunas do arquivo filtrado, se existir
            caminho_filtrado = salvarLinuxArquivoDados
            if os.path.exists(caminho_filtrado):
                try:
                    df_filtrado = pd.read_csv(caminho_filtrado)
                    colunas = list(df_filtrado.columns)

                    self.dropdown_x.clear()
                    self.dropdown_y.clear()
                    self.dropdown_y2.clear()

                    self.dropdown_x.addItems(colunas)
                    self.dropdown_y.addItems(colunas)

                    self.dropdown_y2.addItem("")  # opção vazia
                    self.dropdown_y2.addItems(colunas)

                    self.dropdown_x.setEnabled(True)
                    self.dropdown_y.setEnabled(True)
                    self.dropdown_y2.setEnabled(True)



                except Exception as e:
                    QMessageBox.warning(self, "Erro", f"Erro ao carregar colunas do arquivo filtrado:\n{e}")


    def openConfigWindown(self):
        if not self.dataPath:
            QMessageBox.warning(self, "Nenhum arquivo", "Selecione primeiro um CSV.")
            return
        # Colunas para serem filtradas
        cols = ['angle_roll','analogRule']        
        janela = 100 # numero de dados que vão ser usados para a definição de um único dado filtrado                             
        self.janela_secundaria = configWindown(dataPath    = self.dataPath,
                                               colunas_alvo = cols,
                                               janela       = janela)
        self.janela_secundaria.show()


    def modificarEscala(self):
        if not self.dataPath:# self.botao_plotar.clicked.connect(self.modificarEscala)
            QMessageBox.warning(self, "Nenhum arquivo", "Selecione primeiro um CSV.")
            return
        
        escala = "100"

        scriptPath = "Utility/converterDados.py"

        # Saída esperada
        print(self.dataPath)
        caminho_transformado = os.path.splitext(self.dataPath)[0] + "_tensãoDeformação.csv"

        # Cria processo
        self.processo = QProcess(self)
        self.processo.start("python3", [scriptPath, self.dataPath, escala])

        # Conecta sinais
        self.processo.readyReadStandardOutput.connect(self.ler_saida)
        self.processo.readyReadStandardError.connect(self.ler_erro)
        self.processo.finished.connect(lambda: self.plotarGraficoTensaoDef(caminho_transformado))


    def ler_saida(self):
        saida = self.processo.readAllStandardOutput().data().decode("cp1252")
        print("STDOUT:", saida)

    def ler_erro(self):
        erro = self.processo.readAllStandardError().data().decode()
        print("STDERR:", erro)

    def plotarGraficoTensaoDef(self, caminho=None):
        # Se não foi passado caminho, tenta usar o CSV transformado padrão
        if caminho is None:
            caminho = os.path.splitext(self.dataPath)[0] + "_tensãoDeformação.csv"

        # if not os.path.exists(caminho):
        #     QMessageBox.warning(self, "Arquivo não encontrado", f"O arquivo '{caminho}' não existe.")
        #     return

        try:
            df = pd.read_csv(caminho)

            # Colunas fixas
            eixo_x  = 'Deslocamento (mm)'
            eixo_y1 = 'Forca (N)'
           

            # Converte para numpy para blindar contra erros
            x_vals  = df[eixo_x].to_numpy()
            y1_vals = df[eixo_y1].to_numpy()
    
            # Plotagem
            plt.figure(figsize=(10, 6))
            plt.plot(x_vals, y1_vals, label=eixo_y1, linewidth=2)


            plt.xlabel(eixo_x)
            plt.ylabel("Força")
            plt.title("Gráfico Tensão Deformação")
            plt.legend()
            plt.grid(True)
            plt.tight_layout()
            plt.show()

        except Exception as e:
            QMessageBox.critical(self, "Erro ao plotar", str(e))
    
    def plotarGraficoDadosBrutos(self):
        caminho_filtrado = salvarLinuxArquivoDados
        if not os.path.exists(caminho_filtrado):
            QMessageBox.warning(self, "Arquivo não encontrado", "O arquivo 'dados_filtrados.csv' ainda não foi gerado.")
            return

        eixo_x  = self.dropdown_x.currentText()
        eixo_y1 = self.dropdown_y.currentText()
        eixo_y2 = self.dropdown_y2.currentText()
        escala_selecionada = self.dropdown_escala.currentData()
        
        if not all([eixo_x, eixo_y1, escala_selecionada]):
            QMessageBox.warning(self, "Seleção inválida", "Selecione a Escala e pelo menos os eixos X e Y1.")
            return

        # --- Criação dinâmica das funções de conversão ---
        try:
            # Função de conversão 1: Força (dependente da escala)
            dados_calib_forca = self.dados_calibracao[escala_selecionada]
            coef_forca = np.polyfit(dados_calib_forca['angulos'], dados_calib_forca['forcas'], 2)
            funcao_conversao_forca = np.poly1d(coef_forca)
            print(f">>> Usando calibração de FORÇA para Escala {escala_selecionada} Ton.")

            # Função de conversão 2: Deslocamento (pega do self)
            funcao_conversao_deslocamento = self.funcao_conversao_deslocamento
            if not funcao_conversao_deslocamento:
                 raise ValueError("Função de calibração de deslocamento não foi criada.")

        except Exception as e:
            QMessageBox.critical(self, "Erro de Calibração", f"Não foi possível criar os modelos de conversão.\nErro: {e}")
            return
        
        # --- Leitura e Conversão dos Dados ---
        try:
            df = pd.read_csv(caminho_filtrado)
            
            # Inicializa valores e rótulos
            x_vals  = df[eixo_x].to_numpy(copy=True) # Usamos copy=True para garantir que não estamos modificando o dataframe
            y1_vals = df[eixo_y1].to_numpy(copy=True)
            y2_vals = df[eixo_y2].to_numpy(copy=True) if eixo_y2 else None

            label_eixo_x = eixo_x
            label_y1_final = eixo_y1
            label_y2_final = eixo_y2 if eixo_y2 else ""

            # Converte EIXO X se necessário
            if eixo_x == 'analogRule_filtrada':
                x_vals = funcao_conversao_deslocamento(x_vals)
                label_eixo_x = 'Deslocamento (mm)'
            
            # Converte EIXO Y1 se necessário
            if eixo_y1 == 'angle_roll_filtrada':
                y1_vals = funcao_conversao_forca(y1_vals)
                label_y1_final = f'Força ({escala_selecionada} Ton)'
            elif eixo_y1 == 'analogRule_filtrada':
                y1_vals = funcao_conversao_deslocamento(y1_vals)
                label_y1_final = 'Deslocamento (mm)'
            
            # Converte EIXO Y2 se necessário
            if eixo_y2:
                if eixo_y2 == 'angle_roll_filtrada':
                    y2_vals = funcao_conversao_forca(y2_vals)
                    label_y2_final = f'Força ({escala_selecionada} Ton)'
                elif eixo_y2 == 'analogRule_filtrada':
                    y2_vals = funcao_conversao_deslocamento(y2_vals)
                    label_y2_final = 'Deslocamento (mm)'

            # --- Plotagem ---
            plt.figure(figsize=(10, 6))
            ax1 = plt.gca() # Get current axes

            # Plota a primeira linha
            color1 = 'tab:blue'
            ax1.plot(x_vals, y1_vals, label=label_y1_final, linewidth=2, color=color1)
            ax1.set_xlabel(label_eixo_x)
            ax1.set_ylabel(label_y1_final, color=color1)
            ax1.tick_params(axis='y', labelcolor=color1)

            # Plota a segunda linha (se existir) usando um segundo eixo Y para clareza
            if y2_vals is not None:
                ax2 = ax1.twinx()  # Cria um segundo eixo Y que compartilha o mesmo eixo X
                color2 = 'tab:red'
                ax2.plot(x_vals, y2_vals, label=label_y2_final, linewidth=2, linestyle='--', color=color2)
                ax2.set_ylabel(label_y2_final, color=color2)
                ax2.tick_params(axis='y', labelcolor=color2)
                
            plt.title(f"Gráfico de Dados (Escala {escala_selecionada} Toneladas)")
            # Coleta os "handles" e "labels" de ambos os eixos para uma legenda unificada
            handles1, labels1 = ax1.get_legend_handles_labels()
            if 'ax2' in locals():
                handles2, labels2 = ax2.get_legend_handles_labels()
                ax1.legend(handles1 + handles2, labels1 + labels2, loc='best')
            else:
                ax1.legend(handles1, labels1, loc='best')

            ax1.grid(True)
            plt.tight_layout()
            plt.show()

        except Exception as e:
            QMessageBox.critical(self, "Erro ao plotar", str(e))

        except Exception as e:
            QMessageBox.critical(self, "Erro ao plotar", str(e))



class configWindown(QWidget):
    def __init__(self, dataPath, colunas_alvo, janela=100):
        super().__init__()
        self.setWindowTitle("Configurações de Filtragem")
        self.setFixedSize(350, 200)

        self.dataPath    = dataPath
        self.colunas_alvo = colunas_alvo
        self.janela       = janela

        
        vLayout = QVBoxLayout(self)

        # Label
        vLayout.addWidget(QLabel("Escolha o método de filtragem:"))

        # ComboBox com opções
        self.filterOptions = QComboBox()
        opções = [('Ponderada Gaussiana', 'ponderada_gaussiana'),
                  ('Ponderada Linear', 'ponderada_linear'),
                  ('Ponderada Invertida', 'ponderada_invertida'),
                  ('Ponderada Exponencial', 'ponderada_exponencial'),
                  ('Ponderada Central', 'ponderada_central'),
                  ('Média Simples', 'simples'),]
        
        for texto, key in opções:
            self.filterOptions.addItem(texto, key)
        vLayout.addWidget(self.filterOptions)

        # Botão aplicar
        applyButton = QPushButton("Aplicar")
        applyButton.clicked.connect(self.on_apply)

        # centraliza botão
        hLayout = QHBoxLayout()
        hLayout.addStretch()
        hLayout.addWidget(applyButton)
        hLayout.addStretch()
        vLayout.addLayout(hLayout)

    def on_apply(self):
        filterMethod = self.filterOptions.currentData()
        
        try:
            # chama sua função de filtragem
            aplicar_filtros_csv(nome_arquivo   = self.dataPath,
                                colunas_alvo   = self.colunas_alvo,
                                janela         = self.janela,
                                metodo_csv     = filterMethod,
                                salvar_arquivo = salvarLinuxArquivoDados)
            
            QMessageBox.information(self, "Sucesso", f"Arquivo filtrado salvo como/n'dados_filtrados.csv'")
            self.close()

        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))