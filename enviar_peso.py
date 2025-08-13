import time
import requests
from hx711 import HX711
import subprocess

# Função para obter o serial único do Raspberry Pi
def get_raspberry_serial():
    try:
        # Comando para pegar o número de série da CPU
        serial = subprocess.check_output("cat /proc/cpuinfo | grep Serial | cut -d ' ' -f 2", shell=True)
        return serial.decode("utf-8").strip()
    except Exception as e:
        print(f"[ERRO] Não foi possível obter o serial do Raspberry Pi: {e}")
        return "serial_desconhecido"

# Obtém o identificador único do Raspberry
IDENTIFICADOR_BALANCA = get_raspberry_serial()
print(f"[INFO] Identificador da balança: {IDENTIFICADOR_BALANCA}")

# Inicializa o HX711 nos pinos DOUT=5 e SCK=6
hx = HX711(5, 6)

# Define o fator de calibração
hx.set_reference_unit(103.33)  # Valor calibrado manualmente
print("[INFO] Unidade de referência definida: 103.33")

# Reseta e faz tara
hx.reset()
print("[DEBUG] Sensor resetado.")
hx.tare()
print("[DEBUG] Tara concluída.")

print("[INFO] Balança pronta. Coloque o peso!")

# Loop principal de leitura e envio
while True:
    try:
        # Lê peso médio de 5 amostras e garante que não seja negativo
        peso = max(0, int(hx.get_weight(5)))
        print(f"[DEBUG] Peso lido: {peso}g")

        # Monta payload com o peso e o identificador do Raspberry
        payload = {
            "peso_atual": peso,
            "identificador_balanca": IDENTIFICADOR_BALANCA
        }

        # URL da API
        url = "http://api-pesagem.vercel.app/peso-caixa"

        try:
            # Envia dados para API
            response = requests.post(url, json=payload)
            print(f"[INFO] Peso enviado: {peso}g | Status: {response.status_code} | Resposta: {response.text}")
        except requests.RequestException as req_err:
            print(f"[ERRO] Falha no envio para API: {req_err}")

        # Reinicia o sensor para evitar leituras instáveis
        hx.power_down()
        hx.power_up()

        # Aguarda antes da próxima leitura
        time.sleep(5)

    except (KeyboardInterrupt, SystemExit):
        print("\n[INFO] Programa interrompido pelo usuário.")
        break

    except Exception as e:
        print(f"[ERRO] Falha geral: {e}")
        time.sleep(5)