import pandas as pd
import matplotlib.pyplot as plt

# Leer CSV
df = pd.read_csv("comparacion_cpu_gpu.csv")

# Crear gráfico
plt.figure(figsize=(10, 6))
plt.plot(df["Longitud"], df["Tiempo_CPU_s"], marker='o', label="CPU", linestyle="--")
plt.plot(df["Longitud"], df["Tiempo_GPU_s"], marker='s', label="GPU", linestyle="-")
plt.title("Comparación de tiempos CPU vs GPU para prefijos MD5")
plt.xlabel("Longitud del prefijo")
plt.ylabel("Tiempo (segundos)")
plt.xticks(df["Longitud"])
plt.yscale("log")  # Escala logarítmica por la gran diferencia de tiempos
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("comparacion_cpu_gpu.png")
plt.show()
