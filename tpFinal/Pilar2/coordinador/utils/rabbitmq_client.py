from utils.rabbitmq_connection import RabbitMQClient
from utils.helper import EARRING_QUEUE

def publish_new_transaction(task_data):
    print(f"Publicando tarea: {task_data}")
    rabbit_client_earring = RabbitMQClient(queue_name=EARRING_QUEUE)
    if hasattr(task_data, "to_dict"):
        task_data = task_data.to_dict()

    rabbit_client_earring.publish(task_data)
    rabbit_client_earring.close()
