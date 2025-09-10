from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QComboBox, QLabel

class ExemploComboBox(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Exemplo QComboBox")
        self.setGeometry(100, 100, 300, 150)

        layout = QVBoxLayout()

        self.label = QLabel("Escolha uma opção:")
        layout.addWidget(self.label)

        self.combobox = QComboBox()
        self.combobox.addItems(["Opção 1", "Opção 2", "Opção 3"])
        self.combobox.currentTextChanged.connect(self.item_selecionado)
        layout.addWidget(self.combobox)

        self.setLayout(layout)

    def item_selecionado(self, texto):
        self.label.setText(f"Você selecionou: {texto}")

app = QApplication([])
window = ExemploComboBox()
window.show()
app.exec_()
