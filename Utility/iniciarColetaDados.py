# Utility/iniciarColetaDados.py

from datetime import datetime
import csv
import serial
import sys

def iniciarColetaDados(CSV_name, porta_serial):
    try:
        data = serial.Serial(porta_serial, 115200)
    except serial.SerialException as e:
        print(f"Erro ao abrir a porta serial {porta_serial}: {e}")
        return

    try:
        while data.is_open:
            line = data.readline().decode('utf-8').split(',')

            try:
                angleRoll        = line[0]
                kalmanAngleRoll  = line[1]
                anglePitch       = line[2]
                kalmanAnglePitch = line[3]
                analogRule       = line[4]
                tempo            = line[5].strip()

                with open(CSV_name, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([angleRoll, kalmanAngleRoll,
                                     anglePitch, kalmanAnglePitch,
                                     analogRule, tempo])
                    file.flush()
            except Exception as e:
                print("Erro ao processar linha:", e)

    except KeyboardInterrupt:
        print("Finalizando...")
    finally:
        data.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python iniciarColetaDados.py <porta_serial>")
        sys.exit(1)

    porta_serial = sys.argv[1]

    dadosTempo = datetime.now().strftime("%Y_%m_%d__%H_%M_%S")
    CSV_name = f"/home/GGSB/Códigos/LEM_App/Dados/dados_{dadosTempo}.csv"

    with open(CSV_name, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['angle_roll', 'kalman_angle_roll',
                         'angle_pitch', 'kalman_angle_pitch',
                         'analogRule', 'time'])

    iniciarColetaDados(CSV_name, porta_serial)
