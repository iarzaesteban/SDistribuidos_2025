import pandas as pd
import matplotlib.pyplot as plt

# Cargar datos detallados
df = pd.read_csv('results_detailed.csv')

# Calcular estadísticas de media y desviación estándar
stats = df.groupby(['Case','Type'])['Time_s'].agg(['mean','std']).reset_index()
pivot = stats.pivot(index='Case', columns='Type')

# Preparar datos para barras con errorbars
cases = pivot.index.tolist()
cpu_means = pivot[('mean', 'CPU')].tolist()
cpu_stds  = pivot[('std',  'CPU')].tolist()
gpu_means = pivot[('mean', 'GPU')].tolist()
gpu_stds  = pivot[('std',  'GPU')].tolist()

x = range(len(cases))
width = 0.35

# Gráfico de barras con errorbars
plt.figure()
plt.bar([i - width/2 for i in x], cpu_means, width, yerr=cpu_stds, label='CPU')
plt.bar([i + width/2 for i in x], gpu_means, width, yerr=gpu_stds, label='GPU')
plt.xticks(x, cases)
plt.xlabel('Caso')
plt.ylabel('Tiempo medio (s)')
plt.title('Comparativa Tiempos CPU vs GPU por caso de prueba')
plt.legend()
plt.tight_layout()
plt.savefig('summary_bar_chart.png')

# Boxplot de distribución de tiempos
plt.figure()
df.boxplot(column='Time_s', by=['Case','Type'], grid=False)
plt.title('Distribución de tiempos por Caso y Tipo')
plt.suptitle('')
plt.xlabel('Caso - Tipo')
plt.ylabel('Tiempo (s)')
plt.tight_layout()
plt.savefig('boxplot_times.png')

print("Gráficos generados: summary_bar_chart.png y boxplot_times.png")
