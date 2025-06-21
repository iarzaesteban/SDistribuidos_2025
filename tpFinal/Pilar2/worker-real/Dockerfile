FROM nvidia/cuda:12.2.0-devel-ubuntu22.04

# 1. Instalar Python y dependencias
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      build-essential \
      python3 \
      python3-pip && \
    rm -rf /var/lib/apt/lists/*

# 2. Crear directorio de trabajo
WORKDIR /app

# 3. Instalar requerimientos
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# 4. Copiar todo el código fuente
COPY . .

# 5. Compilar el código CUDA
RUN nvcc -o brute_range main.cu md5.cu \
    -gencode arch=compute_50,code=sm_50 \
    -gencode arch=compute_75,code=sm_75 \
    -gencode arch=compute_50,code=compute_50

# 6. Ejecutar el worker
CMD ["python3", "worker.py"]
