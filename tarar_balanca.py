import time
from hx711 import HX711

# Inicializa HX711
hx = HX711(5, 6)
hx.set_reference_unit(103.33)
hx.reset()
hx.power_up()

print("[INFO] Sensor pronto para tarar.")

# Executa tara
hx.tare()
print("[INFO] Tara concluída. Peso zerado!")

# Apenas mantém sensor ativo por alguns segundos (opcional)
time.sleep(2)