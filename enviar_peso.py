import time
import requests
from hx711 import HX711
import subprocess

# Função para obter o serial único do Raspberry Pi
def get_raspberry_serial():
    try:
        serial = subprocess.check_output(
            "cat /proc/cpuinfo | grep Serial | cut -d ' ' -f 2",
            shell=True
        )
        return serial.decode("utf-8").strip()
    except Exception as e:
        print(f"[ERRO] Não foi possível obter o serial: {e}")
        return "serial_desconhecido"

IDENTIFICADOR_BALANCA = get_raspberry_serial()
print(f"[INFO] Identificador da balança: {IDENTIFICADOR_BALANCA}")

# Inicializa HX711
hx = HX711(5, 6)
hx.set_reference_unit(103.33)
hx.reset()
hx.power_up()
print("[INFO] Unidade de referência definida e sensor pronto!")

print("[INFO] Iniciando leituras. Não será feita tara automática.")

while True:
    try:
        # Lê peso médio de 20 amostras, float para precisão
        peso = max(0, hx.get_weight(20))
        print(f"[DEBUG] Peso lido: {peso:.2f} g")

        payload = {
            "peso_atual": round(peso, 2),
            "identificador_balanca": IDENTIFICADOR_BALANCA
        }

        url = "http://api-pesagem.vercel.app/peso-caixa"
        try:
            response = requests.post(url, json=payload)
            print(f"[INFO] Peso enviado: {peso:.2f} g | Status: {response.status_code}")
        except requests.RequestException as req_err:
            print(f"[ERRO] Falha no envio: {req_err}")

        # Reinicia sensor para leituras estáveis
        hx.power_down()
        hx.power_up()

        # Aguarda um dia entre leituras (86400 segundos)
        time.sleep(86400)

    except (KeyboardInterrupt, SystemExit):
        print("\n[INFO] Programa interrompido pelo usuário.")
        break

    except Exception as e:
        print(f"[ERRO] Falha geral: {e}")
        time.sleep(5)