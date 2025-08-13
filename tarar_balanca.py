import time
from hx711 import HX711

hx = HX711(5, 6)
hx.set_reference_unit(103.33)
hx.reset()
hx.power_up()

print("[INFO] Coloque o recipiente/peso sobre a balança e aguarde alguns segundos...")
time.sleep(5)  # Aguarda estabilização do peso

# Executa a tara
hx.tare(15)  # Lê 15 amostras para definir offset
print("[INFO] Tara concluída. Peso zerado!")

# Apenas mantém sensor ativo por alguns segundos (opcional)
time.sleep(2)