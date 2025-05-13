import pandas as pd

# Cargar datos detallados
df = pd.read_csv("results_detailed.csv")

# Calcular estadísticas por Caso y Tipo
summary = df.groupby(["Case","Type"])["Time_s"].agg(["mean","std"]).reset_index()

# Mostrar resultados
print("Media y desviación estándar de los tiempos:")
print(summary.to_string(index=False, float_format="{:.3f}".format))

# Guardar resumen
summary.to_csv("results_summary.csv", index=False)
print("\nResumen guardado en results_summary.csv")
