import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set(style="whitegrid")
plt.rcParams["figure.figsize"] = (10, 6)

# Cargar datos CSV
df = pd.read_csv('stress_test_results.csv')

print("Datos cargados:")
print(df)

# Gráfico 1: TPS vs Tasks
plt.figure()
sns.lineplot(x="tasks_amount", y="tps_avg", marker="o", data=df, color="blue")
plt.title("TPS promedio vs Cantidad de Tareas")
plt.xlabel("Cantidad de Tareas Enviadas")
plt.ylabel("TPS Promedio")
plt.grid(True)
plt.savefig("tps_vs_tasks.png")
plt.show()

# Gráfico 2: Latencia promedio vs Tasks
plt.figure()
sns.lineplot(x="tasks_amount", y="latency_avg", marker="o", data=df, color="green")
plt.title("Latencia Promedio vs Cantidad de Tareas")
plt.xlabel("Cantidad de Tareas Enviadas")
plt.ylabel("Latencia Promedio (segundos)")
plt.grid(True)
plt.savefig("latency_avg_vs_tasks.png")
plt.show()

# Gráfico 3: Desviación estándar de latencia vs Tasks
plt.figure()
sns.lineplot(x="tasks_amount", y="latency_stddev", marker="o", data=df, color="orange")
plt.title("Desviación Estándar de Latencia vs Cantidad de Tareas")
plt.xlabel("Cantidad de Tareas Enviadas")
plt.ylabel("Desviación Estándar de Latencia")
plt.grid(True)
plt.savefig("latency_stddev_vs_tasks.png")
plt.show()

# Gráfico 4: Porcentaje de errores vs Tasks
plt.figure()
sns.lineplot(x="tasks_amount", y="error_percentage", marker="o", data=df, color="red")
plt.title("Porcentaje de Errores vs Cantidad de Tareas")
plt.xlabel("Cantidad de Tareas Enviadas")
plt.ylabel("Error (%)")
plt.grid(True)
plt.savefig("errors_vs_tasks.png")
plt.show()

# Análisis textual automático
print("\n--- Análisis Automático ---")
max_tps = df.loc[df['tps_avg'].idxmax()]
print(f"✔️ Máximo TPS alcanzado: {max_tps['tps_avg']:.2f} con {int(max_tps['tasks_amount'])} tareas.")

min_latency = df.loc[df['latency_avg'].idxmin()]
print(f"✔️ Mínima latencia promedio: {min_latency['latency_avg']:.4f} segundos con {int(min_latency['tasks_amount'])} tareas.")

max_latency = df.loc[df['latency_avg'].idxmax()]
print(f"✔️ Máxima latencia promedio: {max_latency['latency_avg']:.4f} segundos con {int(max_latency['tasks_amount'])} tareas.")

if df['error_percentage'].max() == 0.0:
    print("✔️ No se detectaron errores en ninguna configuración de carga.")
else:
    print("⚠️ Se detectaron errores en algunas configuraciones de carga.")
