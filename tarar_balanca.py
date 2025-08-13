import time
from hx711 import HX711

# Inicializa HX711
hx = HX711(5, 6)
hx.reset()
hx.power_up()
print("[INFO] Sensor pronto para tarar.")

# Aguarda o usuário colocar o objeto a ser tarado
input("Coloque o objeto a ser tarado e pressione Enter...")

# Executa a tara
hx.tare()
print("[INFO] Tara concluída. Peso do objeto tarado agora é zero.")

# Lê rapidamente para confirmar
peso = hx.get_weight(5)
print(f"[INFO] Peso lido após tara: {peso:.2f} g")