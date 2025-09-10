from All_imports import *
def sen(x): return np.sin(x)


class definirPlanoDeFundo(QWidget):
    """
    Define a imagem que vai ser posta no plano de fundo de alguma TAB, 
    o tamanho da imagem vai se auto ajustar a janela, que deve ser de tamanho fixo!
    """
    def __init__(self, path):
        super().__init__()

        self.backgroundImage = QPixmap(path) # objeto para mostrar imagens dentro de WIDGETS

    def paintEvent(self, event):
        """
        Essa função sobrescreve o método de pintura de um WIDGET Qt para desenhar 
        uma imagem de fundo (background) que é carregada de um PATH armazenado em 'self.path'. 
        A imagem é escalada para preencher todo o WIDGET, independentemente do seu tamanho.
        """
        painter = QPainter(self) # objeto usado para qualquer tipo de desenho (texto, imagens etc.)
        
        # Desenha a imagem em 'backgroundImage' no WIDGET pai
        painter.drawPixmap(0, 0, self.width(), self.height(), self.backgroundImage)

class JanelaGrafico(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gráfico Externo")
        self.setGeometry(100, 100, 800, 600)

        # Criação do gráfico usando Matplotlib
        self.grafico = Grafico(self)
        self.setCentralWidget(self.grafico)

class Grafico(FigureCanvas):
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(8, 6), dpi=100)
        super().__init__(self.fig)

        self.ponteiroLinha = 26

        self.graficoMostrado = self.fig.add_subplot(111)

        #Cria o timer que vai controlar a taxa de atualização do gráfico e a função atrelada
        self.timer = QTimer()
        self.timer.timeout.connect(self.atualizarGrafico)

        self.graficoMostrado.set_title("Gráfico", fontsize=16)
        self.graficoMostrado.set_xlabel("Eixo X", fontsize=12)
        self.graficoMostrado.set_ylabel("Eixo Y", fontsize=12)
        self.graficoMostrado.grid()
        self.line, = self.graficoMostrado.plot([], [], label="Dados", color="blue", linewidth=1)
        self.graficoMostrado.legend()
        self.stop = False
        self.arquivoAtual = None
       
    def iniciarAtualizacao(self):
        self.dadosX = []
        self.dadosY = []
        self.arquivo = None
        self.procurarCSV()
        self.timer.start(10)  

    def pararAtualizacao(self):
        self.timer.stop()

    def procurarCSV(self):
        pasta = "Dados"
        arquivos = [os.path.join(pasta, f) for f in os.listdir(pasta) if f.endswith('.csv')]
        
        if not arquivos:
            return  # Se não houver arquivos, nada será feito

        arquivoMaisRecente = max(arquivos, key=os.path.getmtime)
        
        # Abrir um novo arquivo caso o mais recente tenha mudado
        if self.arquivoAtual != arquivoMaisRecente:
            self.arquivoAtual = arquivoMaisRecente
    
    def atualizarGrafico(self):
        with open(self.arquivoAtual, mode='r') as self.arquivo:
            self.nomeColunas = self.arquivo.readline().strip().split(',')
            self.arquivo.seek(self.ponteiroLinha, 0)
        
            linha = self.arquivo.readline()
            self.ponteiroLinha += len(linha)+1

            linha = linha.strip().split(',')

            if (linha[0] != ''):
                self.stop == True
                self.dadosX.append(int(linha[2]))
                self.dadosY.append(float(linha[0]))

                if (len(self.dadosX) >= 300):
                    self.dadosX.pop(0)
                    self.dadosY.pop(0)

                self.line.set_data(self.dadosX, self.dadosY)

                self.graficoMostrado.set_xlim(self.dadosX[0], self.dadosX[-1]+100)
                self.graficoMostrado.set_ylim(-90, 90)

                self.draw()

            # elif self.stop == True:
            #     print("todos os dados foram lidos")
            #     self.timer.stop()

    def atualizarTitulo(self, novoTitulo):
        self.graficoMostrado.set_title(novoTitulo, fontsize=16)
        self.draw()

    def atualizarXlabel(self, novoTexto):
        self.graficoMostrado.set_xlabel(novoTexto, fontsize=12)
        self.draw()

    def atualizarYlabel(self, novoTexto):
        self.graficoMostrado.set_ylabel(novoTexto, fontsize=12)
        self.draw()


