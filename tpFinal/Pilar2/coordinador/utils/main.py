import threading
import time
import json
from utils.rabbitmq_connection import RabbitMQClient
from utils.helper import EARRING_QUEUE, IN_PROGRESS_QUEUE, MONITORING_IN_PROGRESS_QUEUE

rabbit_earring_queue = RabbitMQClient(queue_name=EARRING_QUEUE)
rabbit_in_progress_queue = RabbitMQClient(queue_name=IN_PROGRESS_QUEUE)
rabbit_monitoring_in_progress_queue = RabbitMQClient(queue_name=MONITORING_IN_PROGRESS_QUEUE)

def move_transactions_to_in_progress():
    while True:
        moved = 0
        while True:
            method_frame, _, body = rabbit_earring_queue.channel.basic_get(EARRING_QUEUE, auto_ack=False)

            if method_frame:
                tx = json.loads(body)
                # Mandamos a in_progress
                rabbit_in_progress_queue.channel.basic_publish(exchange='',
                                      routing_key='IN_PROGRESS_QUEUE',
                                      body=json.dumps(tx))
                rabbit_monitoring_in_progress_queue.channel.basic_publish(exchange='',
                                      routing_key='MONITORING_IN_PROGRESS_QUEUE',
                                      body=json.dumps(tx))
                # Eliminamos de earrings
                rabbit_earring_queue.channel.basic_ack(method_frame.delivery_tag)

                # Eliminamos de monitoring (si usás fanout probablemente sea solo lectura)
                # No se puede eliminar de fanout, así que dejamos monitoring como solo observación
                moved += 1
            else:
                break
        if moved:
            print(f"[INFO] Movidas {moved} transacciones a in_progress.")
        time.sleep(60)  # 2 minutos

# En el main
def start_move_transactions_into_queues():
    threading.Thread(target=move_transactions_to_in_progress, daemon=True).start()

