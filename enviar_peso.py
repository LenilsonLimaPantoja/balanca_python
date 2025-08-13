import time
import requests
import subprocess
from hx711 import HX711

# Obtém serial do Raspberry
def get_rpi_serial():
    try:
        serial = subprocess.check_output(
            "cat /proc/cpuinfo | grep Serial | cut -d ' ' -f 2",
            shell=True
        ).decode().strip()
        return serial if serial else "SERIAL_DESCONHECIDO"
    except Exception:
        return "SERIAL_ERRO"

serial_rpi = get_rpi_serial()
print(f"[INFO] Serial Raspberry: {serial_rpi}")

hx = HX711(5, 6)

REFERENCE_UNIT = 103.33
hx.set_referenceUnit(REFERENCE_UNIT)
hx.reset()
hx.tare()

print("Balança pronta. Coloque o peso!")

while True:
    try:
        peso = max(0, int(hx.get_weight(5)))
        payload = {
            "peso_atual": peso,
            "identificador_balanca": serial_rpi
        }
        url = "http://api-pesagem.vercel.app/peso-caixa"

        try:
            response = requests.post(url, json=payload)
            print(f"Peso: {peso}g | Enviado: {response.status_code} - {response.text}")
        except requests.RequestException as e:
            print(f"[ERRO] Falha ao enviar: {e}")

        hx.power_down()
        hx.power_up()
        time.sleep(5)

    except (KeyboardInterrupt, SystemExit):
        print("\n[INFO] Interrompido pelo usuário.")
        break
    except Exception as e:
        print(f"[ERRO] Problema na leitura ou envio: {e}")
        time.sleep(5)