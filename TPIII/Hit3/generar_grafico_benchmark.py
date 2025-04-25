import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Cargar CSV
df = pd.read_csv("benchmark_results.csv")

# Filtrar respuestas exitosas
df = df[df["status"] == 200]

# Crear gráfico
plt.figure(figsize=(10, 6))
sns.lineplot(data=df, x="size_kb", y="elapsed", hue="concurrency", marker="o")
plt.title("Tiempo de respuesta según tamaño de imagen y concurrencia")
plt.xlabel("Tamaño de imagen (KB)")
plt.ylabel("Tiempo de respuesta (segundos)")
plt.grid(True)
plt.legend(title="Concurrencia")
plt.tight_layout()

# Guardar imagen
plt.savefig("benchmark_result_plot.png", dpi=300)  # o .jpg si preferís
print("✅ Imagen guardada como benchmark_result_plot.png")
