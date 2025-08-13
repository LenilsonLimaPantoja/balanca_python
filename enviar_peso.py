import time
import requests
from hx711 import HX711
import os

# Função para obter o serial do Raspberry Pi
def get_rpi_serial():
    try:
        with open("/proc/cpuinfo", "r") as f:
            for line in f:
                if line.startswith("Serial"):
                    return line.strip().split(":")[1].strip()
    except Exception as e:
        print(f"[ERRO] Não foi possível ler serial do Raspberry: {e}")
    return "000000"  # fallback caso não consiga ler

# Serial do Raspberry
serial_rpi = get_rpi_serial()
print(f"[INFO] Serial do Raspberry Pi: {serial_rpi}")

# Inicializa o HX711 com pinos DOUT=5 e SCK=6
hx = HX711(5, 6)

# Define a unidade de referência (calibração) baseada em peso conhecido
REFERENCE_UNIT = 103.33
hx.set_reference_unit(REFERENCE_UNIT)
print(f"[INFO] Unidade de referência definida: {REFERENCE_UNIT}")

# Reseta o sensor e zera a balança
hx.reset()
print("[INFO] Sensor resetado.")
hx.tare()
print("[INFO] Tare concluído. Peso inicial zerado.")

print("Balança pronta. Coloque o peso!")

while True:
    try:
        # Lê o peso médio de 5 amostras
        peso = hx.get_weight(5)
        peso = max(0, int(peso))
        print(f"[DEBUG] Peso lido: {peso} g")

        # Cria payload para enviar à API
        payload = {
            "peso_atual": peso,
            "identificador_balanca": serial_rpi
        }
        url = "http://api-pesagem.vercel.app/peso-caixa"

        try:
            response = requests.post(url, json=payload)
            print(f"[INFO] Peso enviado: {peso}g | Status: {response.status_code}")
        except requests.RequestException as req_err:
            print(f"[ERRO] Falha ao enviar peso para a API: {req_err}")

        # Reinicia o HX711 para evitar leituras instáveis
        hx.power_down()
        print("[DEBUG] Sensor desligado temporariamente.")
        time.sleep(0.1)
        hx.power_up()
        print("[DEBUG] Sensor ligado novamente.")

        time.sleep(5)

    except (KeyboardInterrupt, SystemExit):
        print("\n[INFO] Programa interrompido pelo usuário.")
        break

    except Exception as e:
        print(f"[ERRO] Problema na leitura ou envio do peso: {e}")
        time.sleep(5)