FROM nvidia/cuda:12.2.0-devel-ubuntu22.04

# Instalar herramientas necesarias
RUN apt-get update && apt-get install -y build-essential python3 python3-pip

# Instalar dependencias Python
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copiar archivos fuente CUDA
COPY main.cu md5.cu md5.cuh config.h ./

# Compilar el ejecutable
RUN nvcc -arch=sm_75 main.cu md5.cu -o brute_range

# Copiar script Python
COPY worker.py .

CMD ["python3", "worker.py"]
