FROM python:3.10-slim

# Instalar OpenCV y dependencias
RUN pip install opencv-python-headless

# Crear carpeta de trabajo
WORKDIR /app

# Copiar el script
COPY sobel_filter.py .

# Comando por defecto
ENTRYPOINT ["python", "sobel_filter.py"]
