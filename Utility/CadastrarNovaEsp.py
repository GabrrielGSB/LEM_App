
from All_imports import *

class CadastroESPDialog(QDialog):
    # Crie um sinal para notificar que uma nova máquina foi cadastrada
    nova_mquina_cadastrada = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cadastrar Nova Máquina")
        self.setFixedSize(300, 200)

        layout = QFormLayout()

        self.nome_input = QLineEdit()
        self.ip_input = QLineEdit()
        self.porta_input = QLineEdit()

        layout.addRow("Nome da Máquina:", self.nome_input)
        layout.addRow("Endereço IP:", self.ip_input)
        layout.addRow("Porta:", self.porta_input)

        self.botao_cadastrar = QPushButton("Cadastrar")
        self.botao_cadastrar.clicked.connect(self.cadastrar)
        layout.addRow(self.botao_cadastrar)

        self.setLayout(layout)

    def cadastrar(self):
        nome = self.nome_input.text()
        ip = self.ip_input.text()
        porta = self.porta_input.text()

        if nome and ip and porta:
            # Salva os dados da máquina em um arquivo de texto
            with open("Dados/maquinas.txt", "a") as arquivo:
                arquivo.write(f"{nome},{ip},{porta}\n")

            QMessageBox.information(self, "Sucesso", "Máquina cadastrada com sucesso!")
            self.nova_mquina_cadastrada.emit()  # Emite o sinal após o cadastro
            self.close()
        else:
            QMessageBox.warning(self, "Erro", "Preencha todos os campos!")