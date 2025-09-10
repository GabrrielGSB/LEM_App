from All_imports import *
csv = None
def sen(x): return np.sin(x)

dadosX, dadosY = [],[]

# Função que simula um processo demorado
class LeitorCSV:
    def __init__(self, caminhoArquivo):
        self.caminhoArquivo = caminhoArquivo
        # self.oldCount = None

    def ler(self):
        global csv
        count = 0
        with open(self.caminhoArquivo, mode='r') as csv:
            # colunas = csv.readline().strip().split(',')
            linha = csv.readline()
            count += len(linha)+1
            csv.seek(count,0)

            while True:
                linha = csv.readline()
                print(linha.strip())
                count += 2*len(linha)+1
                csv.seek(count,0)

                # print(linha)
                # if linha[0] == "": 
                #     print("Todo arquivo lido")
                #     break
                # print(linha)
                # dadosX.append(float(linha[0]))
                # dadosY.append(float(linha[1]))
                t.sleep(1)


       

if __name__ == "__main__":
    leitor = LeitorCSV("Dados/dados.csv")
    leitor.ler()

  


