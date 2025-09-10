from All_imports import *
from Utility.classesAux import *
import serial.tools.list_ports


"""
Essa TAB tem a função de servir como interface inicial, buscando:
    1) Permitir a escolha da máquina na qual os dados vão ser coletados;
    2) Permite a escolha da porta em que vão ser escolhidos os dados;
    3) Ativar a coleta de dados, a fim de preencher o CSV.
"""

class tab1(QWidget):
    def __init__(self, imagemFundo):
        super().__init__()

   
        # Definição das caracteristicas do plano de fundo----------------
        self.background = definirPlanoDeFundo(imagemFundo)
        self.background.setGeometry(0, 0, self.width(), self.height())
        #----------------------------------------------------------------

        # Criação de um LAYOUT para todos os WIDGETs dessa TAB
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.background)
        # ----------------------------------------------------

        # Criação do retângulo estiloso atrás dos widgets principais---------------------
        self.caixaControle = QFrame(self.background)
        self.caixaControle.setGeometry(40, 20, 420, 340)
        self.caixaControle.setStyleSheet("""QFrame {background-color: rgba(0, 0, 0, 150);
                                            border-radius: 15px;
                                            border: 2px solid white;}""")
        self.caixaControle.lower()  
        #--------------------------------------------------------------------------------

        # Definição da caixa de seleção da fonte dos dados---------------------------
        self.Selecao = QComboBox()
        self.Selecao.setParent(self.background)
        self.Selecao.setStyleSheet("""QComboBox {border: 2px solid black;
                                                 border-radius: 10px;
                                                 padding: 5px;
                                                 background-color: lightblue;
                                                 color: darkblue;}
                                      QComboBox QAbstractItemView {border: 1px solid gray;
                                                                   selection-background-color: lightgray;
                                                                   background: white;}""")
        self.Selecao.move(50, 50)
        self.Selecao.setFixedSize(380, 30)
        self.Selecao.currentTextChanged.connect(self.mostrarImagemComboBox)

        # Definição do texto de seleção de dados
        self.SelectionLabel = QLabel("Selecione a fonte dos dados", self.background)
        self.SelectionLabel.move(50, 25)
        self.SelectionLabel.setFont(QFont("Arial", 14, QFont.Bold))
        self.SelectionLabel.setStyleSheet("color: white;")
        self.SelectionLabel.show()
        #----------------------------------------------------------------------------

        # Definição da imagem atrelada à seleção da fonte de dados
        self.imagemMaquina = QLabel(self.background)
        self.imagemMaquina.move(650, 50)

        self.mostrarImagemComboBox(self.Selecao.currentText())
        #---------------------------------------------------------

        # Definição da ComboBox para seleção da porta serial------------------------
        self.serialPort = QComboBox(self.background)
        self.serialPort.move(50, 125)
        self.serialPort.setFixedSize(380, 30)
        self.serialPort.setStyleSheet("""QComboBox {border: 2px solid black;
                                                 border-radius: 10px;
                                                 padding: 5px;
                                                 background-color: lightblue;
                                                 color: darkblue;}
                                   
                                      QComboBox QAbstractItemView {border: 1px solid gray;
                                                                   selection-background-color: lightgray;
                                                                   background: white;}""")
        
        # Definição do texto de seleção de SerialPort
        self.serialPortLabel = QLabel("Selecione a porta da ESP32", self.background)
        self.serialPortLabel.move(50, 100)
        self.serialPortLabel.setFont(QFont("Arial", 14, QFont.Bold))
        self.serialPortLabel.setStyleSheet("color: white;")

        # Carrega as portas disponíveis
        self.serialPort.currentIndexChanged.connect(self.salvarPortaSerial)
        self.choosenSerialPort = None 

        self.atualizarPortasSeriais()
        self.salvarPortaSerial() 
        #---------------------------------------------------------------------------

        # Definição do botão de inicialização utilizado--------------------------
        self.botao = QPushButton("Inicializar Coleta de Dados", self.background)
        self.botao.setParent(self.background)
        self.botao.setStyleSheet("""QPushButton {background-color: blue; 
                                                           color: white; 
                                                           font-size: 14px;
                                                           font-weight: bold; 
                                                           border-radius: 10px;}
                                    QPushButton:hover {background-color: lightblue;}""")
        self.botao.move(50, 300)
        self.botao.setFixedSize(200, 40)
        self.botao.clicked.connect(self.iniciarColeta)
        #------------------------------------------------------------------------
        self.errOnScript = False # Para saber se houve erro no script
      

    def mostrarImagemComboBox(self, texto):
        caminho_imagem = f"Imagens/{texto}.png"  # Supondo que as imagens tenham o mesmo nome das máquinas

        # definida uma imagem padrão caso o a imagem escolhida nn existir
        if not os.path.exists(caminho_imagem): caminho_imagem = "Imagens/im.jpg" 

        imageComboBox = QPixmap(caminho_imagem)

        self.imagemMaquina.setPixmap(imageComboBox.scaled(300, 300))


    def iniciarColeta(self):
        # Cria janela de status--------------------------------------------------
        self.janela_status = QWidget()
        self.janela_status.setWindowTitle("Coleta em Andamento")
        self.janela_status.setFixedSize(400, 150)

        layout = QVBoxLayout()
        label = QLabel("Coletando dados...\nClique para interromper a coleta.")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        botao_parar = QPushButton("Parar Coleta")
        botao_parar.clicked.connect(self.pararColeta)
        layout.addWidget(botao_parar)

        self.janela_status.setLayout(layout)
        self.janela_status.show()
        #-------------------------------------------------------------------------

        # Executa o script de coleta com argumento do CSV
        self.executarScript("/home/GGSB/Códigos/LEM_App/Utility/iniciarColetaDados.py")
        


    def executarScript(self, scriptPath):
        self.errOnScript = False

        if not self.choosenSerialPort:
            QMessageBox.warning(self, "Aviso", "Nenhuma porta serial foi selecionada.")
            return
        print(self.choosenSerialPort)
        self.processo = QProcess(self)
        self.processo.start("python3", [scriptPath, self.choosenSerialPort])

        self.processo.readyReadStandardOutput.connect(self.ler_saida)
        self.processo.readyReadStandardError.connect(self.ler_erro)
        self.processo.finished.connect(self.processo_terminou)


    def pararColeta(self):
        if hasattr(self, "processo") and self.processo.state() == QProcess.Running:
            self.processo.terminate()

    def ler_saida(self):
        saida = self.processo.readAllStandardOutput().data().decode()
        print("Saída do Script:", saida)

    def ler_erro(self):
        self.errOnScript = True

        erro = self.processo.readAllStandardError().data().decode()
        print("Erro no Script:", erro)


    def processo_terminou(self):
        if hasattr(self, "janela_status"):
            self.janela_status.close()

        if self.errOnScript:
            QMessageBox.critical(self, "Erro", "Ocorreu um erro durante a coleta de dados.")
        else:
            QMessageBox.information(self, "Coleta Finalizada", 
                f"Coleta finalizada com sucesso!\n Arquivo salvo em (Dados)")

    def atualizarPortasSeriais(self):
        """Lista todas as portas seriais disponíveis no sistema."""

        self.serialPort.clear()
        portas = serial.tools.list_ports.comports()

        for porta in portas:
            # Exibe nome amigável da porta
            descricao = f"{porta.device} - {porta.description}"
            self.serialPort.addItem(descricao, porta.device)  

        self.salvarPortaSerial()

    def salvarPortaSerial(self):
        self.choosenSerialPort = self.serialPort.currentData()







