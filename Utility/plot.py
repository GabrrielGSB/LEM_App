import sys
import pandas as pd
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QVBoxLayout, QWidget, QLabel


class CSVGraphApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CSV Plotter")
        self.setGeometry(300, 300, 400, 200)
        self.initUI()

    def initUI(self):
        # Layout principal
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Label de instrução
        self.label = QLabel("Clique no botão para selecionar um arquivo CSV.")
        self.layout.addWidget(self.label)

        # Botão para abrir o seletor de arquivos
        self.button = QPushButton("Selecionar Arquivo CSV")
        self.button.clicked.connect(self.select_csv)
        self.layout.addWidget(self.button)

    def select_csv(self):
        # Abrir o diálogo para selecionar arquivos
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Selecione um Arquivo CSV", "", "CSV Files (*.csv);;All Files (*)", options=options
        )

        if file_path:
            try:
                # Ler o arquivo CSV
                data = pd.read_csv(file_path)
                if data.shape[1] < 2:
                    self.label.setText("O arquivo precisa ter pelo menos 2 colunas.")
                    return

                # Plotar os dados
                plt.figure(figsize=(8, 6))
                plt.plot(data.iloc[:, 2], data.iloc[:, 0], label="Y vs X")
                plt.xlabel("X")
                plt.ylabel("Y")
                plt.title("Gráfico dos Dados")
                plt.legend()
                plt.grid()
                plt.show()

                self.label.setText("Gráfico plotado com sucesso!")
            except Exception as e:
                self.label.setText(f"Erro ao processar o arquivo: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CSVGraphApp()
    window.show()
    sys.exit(app.exec_())
