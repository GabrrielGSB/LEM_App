from Utility.CadastrarNovaEsp import CadastroESPDialog
from All_imports import *
from Tabs.tab1 import *
from Tabs.tab2 import *

caminhoLinuxImagemFundo    = "Imagens/im1.png"
caminhoWindownsImagemFundo = "Imagens\im1.png"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Define caracteristicas básicas do APP
        self.setWindowTitle("RAITec - LEM")
        self.setFixedSize(1000, 500)  
        #--------------------------------------

        # Cria um widget central e layout para organizar a imagem e as abas
        mainWidget = QWidget()
        layout     = QVBoxLayout()
        self.setCentralWidget(mainWidget)
        mainWidget.setLayout(layout)
        #------------------------------------------------------------------

        # Cria as TABs de navegação----------------------------------
        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.North)
        tabs.setMovable(False)

        # Adiciona as Classes que implementam cada TAB de navegação
        tabs.addTab(tab1(caminhoLinuxImagemFundo), 
                         "Receber Dados em Tempo Real")
        tabs.addTab(tab2(caminhoLinuxImagemFundo), 
                         "Plotar Gráficos")
        layout.addWidget(tabs) 
        #-----------------------------------------------------------

app    = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()