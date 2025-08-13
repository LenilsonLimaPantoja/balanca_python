import time
from hx711 import HX711

# Inicializa HX711
hx = HX711(5, 6)
hx.set_reference_unit(103.33)
hx.reset()
hx.power_up()

print("[INFO] Coloque o objeto/recipiente que deseja tarar e pressione Enter")
input("Pressione Enter para realizar a tara...")

# Executa a tara
hx.tare()
print("[INFO] Tara concluída! O peso do objeto agora é considerado zero.")

# Apenas mantém sensor ativo por alguns segundos (opcional)
time.sleep(2)