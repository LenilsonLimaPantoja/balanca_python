import time
import requests
from hx711 import HX711
import subprocess
from datetime import datetime, timedelta

# Função para obter o serial único do Raspberry Pi
def get_raspberry_serial():
    try:
        serial = subprocess.check_output(
            "cat /proc/cpuinfo | grep Serial | cut -d ' ' -f 2", shell=True
        )
        return serial.decode("utf-8").strip()
    except Exception as e:
        print(f"[ERRO] Não foi possível obter o serial do Raspberry Pi: {e}")
        return "serial_desconhecido"

# Identificador da balança
IDENTIFICADOR_BALANCA = get_raspberry_serial()
print(f"[INFO] Identificador da balança: {IDENTIFICADOR_BALANCA}")

# Inicializa o HX711
hx = HX711(5, 6)
hx.set_reference_unit(103.33)
hx.reset()
hx.tare()

print("[INFO] Balança pronta. Coloque o peso!")

# Horário da leitura diária (hora e minuto)
LEITURA_HORA = 10
LEITURA_MINUTO = 0

while True:
    try:
        # Calcula quanto tempo falta até o próximo horário
        agora = datetime.now()
        proxima_leitura = agora.replace(hour=LEITURA_HORA, minute=LEITURA_MINUTO, second=0, microsecond=0)
        if agora >= proxima_leitura:
            # Se já passou do horário hoje, agenda para amanhã
            proxima_leitura += timedelta(days=1)
        
        segundos_ate_proxima = (proxima_leitura - agora).total_seconds()
        print(f"[INFO] Próxima leitura em {int(segundos_ate_proxima)} segundos ({proxima_leitura})")
        
        # Aguarda até o horário da próxima leitura
        time.sleep(segundos_ate_proxima)

        # Faz a leitura do peso
        peso = max(0, int(hx.get_weight(5)))
        print(f"[DEBUG] Peso lido: {peso}g")

        # Monta payload e envia para API
        payload = {
            "peso_atual": peso,
            "identificador_balanca": IDENTIFICADOR_BALANCA
        }
        url = "http://api-pesagem.vercel.app/peso-caixa"
        try:
            response = requests.post(url, json=payload)
            print(f"[INFO] Peso enviado: {peso}g | Status: {response.status_code} | Resposta: {response.text}")
        except requests.RequestException as req_err:
            print(f"[ERRO] Falha no envio para API: {req_err}")

        # Reinicia o sensor
        hx.power_down()
        hx.power_up()

    except (KeyboardInterrupt, SystemExit):
        print("\n[INFO] Programa interrompido pelo usuário.")
        break

    except Exception as e:
        print(f"[ERRO] Falha geral: {e}")
        time.sleep(60)  # Espera um minuto antes de tentar novamente em caso de erro