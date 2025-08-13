import time
from hx711 import HX711

# Inicializa HX711 nos pinos DOUT=5 e SCK=6
hx = HX711(5, 6)
hx.set_reference_unit(103.33)
hx.reset()
hx.power_up()

print("[INFO] Sensor pronto para tarar.")

# Executa tara com várias amostras para maior precisão
tare_value = hx.tare(times=20)  # 20 amostras para estabilidade
print(f"[INFO] Tara concluída. Valor de offset registrado: {tare_value}")

# Mantém sensor ativo alguns segundos (opcional)
time.sleep(2)
