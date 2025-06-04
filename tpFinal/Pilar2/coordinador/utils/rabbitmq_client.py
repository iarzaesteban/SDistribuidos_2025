import json
from utils.rabbitmq_connection import RabbitMQClient
from utils.helper import EARRING_QUEUE, MONITORING_IN_PROGRESS_QUEUE

rabbit_client_earring = RabbitMQClient(queue_name=EARRING_QUEUE)
rabbit_client_monitoring = RabbitMQClient(queue_name=MONITORING_IN_PROGRESS_QUEUE)


def peek_monitoring_transactions(limit=100):
    """
        Lee hasta `limit` transacciones de la cola de monitoreo sin eliminarlas.
    """
    messages = []

    def callback(ch, method, properties, body):
        if len(messages) < limit:
            try:
                messages.append(json.loads(body.decode()))
            except json.JSONDecodeError:
                pass
        else:
            ch.stop_consuming()

    try:
        rabbit_client_monitoring.channel.basic_consume(
            queue=MONITORING_IN_PROGRESS_QUEUE,
            on_message_callback=callback,
            auto_ack=False
        )
        rabbit_client_monitoring.channel._connection.process_data_events(time_limit=1)  # consume por 1 segundos
        rabbit_client_monitoring.channel.cancel()  # cancela el consumer para que no quede abierto
    except Exception as e:
        print(f"[ERROR] Peek consume failed: {e}")

    return messages


def publish_new_transaction(task_data):
    print(f"Publicando tarea: {task_data}")
    
    if hasattr(task_data, "to_dict"):
        task_data = task_data.to_dict()

    rabbit_client_earring.publish(task_data)
