import pika
import redis
import os
import io
import time
import socket
from PIL import Image
import numpy as np
from scipy import ndimage

redis_host = os.getenv("REDIS_HOST", "redis")
r = redis.Redis(host=redis_host, port=6379, decode_responses=False)

def sobel_filter(img_array):
    dx = ndimage.sobel(img_array, axis=1)
    dy = ndimage.sobel(img_array, axis=0)
    return np.hypot(dx, dy).astype(np.uint8)

def connect_and_consume():
    rabbit_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbit_host))
    channel = connection.channel()
    channel.queue_declare(queue="sobel_tasks", durable=True)

    pod_name = os.getenv("POD_NAME", socket.gethostname())
    print(f"🆔 Worker iniciado en pod: {pod_name}")
    print("🔌 Conectando a Redis...")
    print("📡 Conectando a RabbitMQ...")

    def callback(ch, method, properties, body):
        try:
            separator = b'###SPLIT###'
            print("======== MENSAJE RECIBIDO ========")
            print(f"Tamaño total del mensaje: {len(body)} bytes")

            if separator not in body:
                print("❌ Separador NO encontrado en el mensaje. Ignorando...")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return

            metadata, image_data = body.split(separator, 1)
            print(f"✔️ Separador encontrado. Metadata: {metadata}")
            print(f"Tamaño de parte de imagen: {len(image_data)} bytes")

            try:
                job_id, part_index, total_parts = metadata.decode().split("||")
            except Exception as e:
                print(f"❌ Error desempaquetando metadata: {e}")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return

            print(f"🧩 job_id: {job_id}, parte: {int(part_index) + 1}/{total_parts}")

            img = Image.open(io.BytesIO(image_data)).convert("L")
            img_array = np.array(img)

            result_array = sobel_filter(img_array)
            result_image = Image.fromarray(result_array)

            output_buffer = io.BytesIO()
            result_image.save(output_buffer, format='PNG')
            r.hset(job_id, str(part_index).encode(), output_buffer.getvalue())

            # Verificar si ya están todas las partes
            parts_expected = int(r.get(f"{job_id}:parts_expected") or 0)
            parts_actuales = r.hlen(job_id)

            print(f"🔍 Partes actuales para {job_id}: {parts_actuales}/{parts_expected}")
            if parts_actuales == parts_expected:
                # No marcamos como "done", solo notificamos
                print(f"📡 Todas las partes listas. Publicando job_id en canal Redis: {job_id}")
                r.publish("results", job_id)


            print(f"✅ Parte {int(part_index) + 1} procesada y almacenada")
            print("==========================================")

            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            print(f"❌ Error general en callback: {e}")
            ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue="sobel_tasks", on_message_callback=callback)

    print("🟢 Worker listo. Esperando tareas...")
    channel.start_consuming()

if __name__ == "__main__":
    while True:
        try:
            connect_and_consume()
        except Exception as e:
            print(f"🔁 Error en conexión, reintentando: {e}")
            time.sleep(2)
