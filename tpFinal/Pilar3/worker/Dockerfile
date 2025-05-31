# Etapa de compilación
FROM nvidia/cuda:11.4.2-devel-ubuntu20.04 AS builder
RUN apt-get update && apt-get install -y build-essential python3 python3-pip
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
COPY main.cu md5.cu md5.cuh config.h ./
RUN nvcc -arch=sm_75 main.cu md5.cu -o brute_range

# Etapa final (runtime)
FROM nvidia/cuda:11.4.2-runtime-ubuntu20.04
RUN apt-get update && apt-get install -y python3 python3-pip
COPY --from=builder /brute_range /brute_range
COPY worker.py .
CMD ["python3", "worker.py"]
