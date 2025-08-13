import time
import requests
from hx711 import HX711

hx = HX711(5, 6)

# Calcule e defina o novo reference_unit
hx.set_reference_unit(103.33)  # Use o valor que você calcular

hx.reset()
hx.tare()

print("Balança pronta. Coloque o peso!")

while True:
    try:
        peso = max(0, int(hx.get_weight(5)))
        payload = {
            "peso_atual": peso,
            "identificador_balanca": "cxTCC"
        }
        url = "http://api-pesagem.vercel.app/peso-caixa"
        response = requests.post(url, json=payload)
        print(f"Peso: {peso}g | Enviado: {response.status_code} - {response.text}")

        hx.power_down()
        hx.power_up()
        time.sleep(5)
    except (KeyboardInterrupt, SystemExit):
        print("\nInterrompido pelo usuário.")
        break
    except Exception as e:
        print(f"Erro ao ler ou enviar peso: {e}")
        time.sleep(5)