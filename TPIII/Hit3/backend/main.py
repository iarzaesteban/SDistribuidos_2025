from fastapi import FastAPI, File, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uuid
import redis
import pika
import os
import io
from PIL import Image
import numpy as np
import asyncio
import redis.asyncio as aioredis

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

redis_host = os.getenv("REDIS_HOST", "redis")
# Conexión correcta para manejar binarios
r = redis.Redis(host=redis_host, port=6379, decode_responses=False)

def try_assemble_image(job_id):
    parts_expected = int(r.get(f"{job_id}:parts_expected") or 0)
    parts = r.hgetall(job_id)

    if len(parts) < parts_expected:
        print(f"⏳ Esperando más partes para {job_id}: {len(parts)}/{parts_expected}")
        return

    ordered_parts = []
    for i in range(parts_expected):
        key = str(i).encode()  # claves como bytes: b'0', b'1', ...
        part_data = parts.get(key)

        if part_data is None:
            print(f"⚠️ Parte {i} no encontrada en Redis para job_id {job_id}. Abortando ensamblado.")
            return

        try:
            img = Image.open(io.BytesIO(part_data))
            ordered_parts.append(img)
        except Exception as e:
            print(f"❌ Error abriendo parte {i} para job_id {job_id}: {e}")
            return

    widths, heights = zip(*(img.size for img in ordered_parts))
    total_height = sum(heights)
    width = widths[0]

    final_image = Image.new('L', (width, total_height))
    y_offset = 0
    for part in ordered_parts:
        final_image.paste(part, (0, y_offset))
        y_offset += part.size[1]

    output_buffer = io.BytesIO()
    final_image.save(output_buffer, format='PNG')
    r.set(f"{job_id}:image", output_buffer.getvalue())
    r.set(f"{job_id}:status", b"done")

    print(f"✅ Imagen final almacenada para {job_id}")


def publish_part(job_id, part_index, total_parts, part_data):
    rabbit_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbit_host))
        channel = connection.channel()
        channel.queue_declare(queue="sobel_tasks", durable=True)

        separator = b'###SPLIT###'
        metadata = f"{job_id}||{part_index}||{total_parts}".encode()
        body = metadata + separator + part_data

        print("======== MENSAJE DEBUG ========")
        print(f"job_id: {job_id}")
        print(f"part_index: {part_index}")
        print(f"total_parts: {total_parts}")
        print(f"separator in body: {separator in body}")
        print(f"part_data size: {len(part_data)} bytes")
        print("================================")

        channel.basic_publish(
            exchange='',
            routing_key='sobel_tasks',
            body=body,
            properties=pika.BasicProperties(delivery_mode=2)
        )
        channel.close()
        connection.close()

        print(f"📤 Parte {part_index + 1}/{total_parts} enviada para job {job_id}")
    except Exception as e:
        print(f"❌ Error enviando parte {part_index}: {e}")

@app.post("/upload")
async def upload_image(image: UploadFile = File(...)):
    image_data = await image.read()
    job_id = str(uuid.uuid4())

    try:
        img = Image.open(io.BytesIO(image_data)).convert("L")
    except Exception as e:
        return {"error": f"No se pudo leer la imagen: {e}"}

    arr = np.array(img)
    total_parts = 3
    height = arr.shape[0]
    part_height = height // total_parts

    r.set(f"{job_id}:status", b"processing")
    r.set(f"{job_id}:parts_expected", str(total_parts).encode())

    for i in range(total_parts):
        start = i * part_height
        end = (i + 1) * part_height if i < total_parts - 1 else height
        part = arr[start:end, :]

        if part.shape[0] == 0:
            print(f"⚠️ Parte {i} vacía, saltando envío.")
            continue

        part_bytes = io.BytesIO()
        Image.fromarray(part).save(part_bytes, format="PNG")
        publish_part(job_id, i, total_parts, part_bytes.getvalue())

    return {"id": job_id}

@app.get("/result/{job_id}")
async def get_result(job_id: str):
    status = r.get(f"{job_id}:status")
    if not status:
        return {"error": "Job ID no encontrado"}

    if status != b"done":
        try_assemble_image(job_id)
        # volver a consultar después de intentar ensamblar
        status = r.get(f"{job_id}:status")
        if status == b"done":
            image_data = r.get(f"{job_id}:image")
            if not image_data:
                return {"error": "Resultado no disponible"}
            return StreamingResponse(io.BytesIO(image_data), media_type="image/png")
        return {"status": status.decode()}


    image_data = r.get(f"{job_id}:image")
    if not image_data:
        return {"error": "Resultado no disponible"}

    return StreamingResponse(io.BytesIO(image_data), media_type="image/png")

@app.websocket("/ws/results")
async def results_ws(websocket: WebSocket):
    await websocket.accept()
    redis = await aioredis.from_url("redis://redis", decode_responses=True)
    pubsub = redis.pubsub()
    await pubsub.subscribe("results")

    print("🌐 WebSocket conectado y suscripto al canal Redis 'results'")

    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                job_id = message["data"]
                print(f"📥 Recibido job_id desde Redis: {job_id}")
                await websocket.send_text(job_id)
                print(f"📤 Enviado job_id a frontend vía WebSocket: {job_id}")
    except WebSocketDisconnect:
        print("🔌 Cliente WebSocket desconectado")
    finally:
        await pubsub.unsubscribe("results")
        await pubsub.close()
        await redis.close()

