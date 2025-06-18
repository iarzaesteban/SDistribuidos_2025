import base64
import requests
from datetime import datetime
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

timestamp = datetime.utcnow().isoformat()

# 1. Crear par de claves (solo la primera vez, después podés guardarlas en archivo)
private_key = Ed25519PrivateKey.generate()
public_key = private_key.public_key()

# Serializar claves a base64
public_key_bytes = public_key.public_bytes(
    encoding=serialization.Encoding.Raw,
    format=serialization.PublicFormat.Raw
)
private_key_bytes = private_key.private_bytes(
    encoding=serialization.Encoding.Raw,
    format=serialization.PrivateFormat.Raw,
    encryption_algorithm=serialization.NoEncryption()
)

source_b64 = base64.b64encode(public_key_bytes).decode()
target_b64 = source_b64  # para pruebas, usamos la misma clave
amount = 100.0
description = "Prueba de transacción"
###########################################################
###########################################################
# Esto lo uso para hardcodear cosas y probar que un worker 
# no proceso una tx  
description = "pepe" 
###########################################################
###########################################################

# 2. Armar mensaje y firmarlo
message = f"{source_b64}{target_b64}{amount}{description}{timestamp}".encode()
signature = private_key.sign(message)
signature_b64 = base64.b64encode(signature).decode()

# 3. Armar el JSON de la transacción
tx = {
    "source": source_b64,
    "target": target_b64,
    "amount": amount,
    "description": description,
    "timestamp": timestamp,
    "sign": signature_b64
}

# 4. Enviar la transacción al coordinador
url = "http://localhost:8989/new-task"
response = requests.post(url, json=tx)

# 5. Mostrar resultado
print("Status Code:", response.status_code)
print("Response:", response.json())



# {
#     "Blockchain": [
#         {
#             "block_id": 0,
#             "timestamp": 1750206335,
#             "transaction": {
#                 "block_name": "GENESIS"
#             },
#             "config": {
#                 "max_tries_per_tx": 6,
#                 "monitoring_window_start": 5,
#                 "monitoring_window_end": 15,
#                 "publish_window_start": 50,
#                 "publish_window_end": 59,
#                 "window_period_seconds": 60
#             },
#             "block_hash": "ded1547cafc54950fc4dac9a3f09de8959d42eeb"
#         },
#         {
#             "block_id": 1,
#             "previous_hash": "ded1547cafc54950fc4dac9a3f09de8959d42eeb",
#             "nonce": 11574,
#             "transaction": {
#                 "tx_id": "30a95275-e74e-43cf-8a36-7737c6b50316",
#                 "source": "MRUF5Waoi0UTpEKQAT8YbQy1di/3g/MTpNXNrI/thxg=",
#                 "target": "MRUF5Waoi0UTpEKQAT8YbQy1di/3g/MTpNXNrI/thxg=",
#                 "amount": 100.0,
#                 "description": "pepe",
#                 "timestamp": "2025-06-18T00:25:38.036254",
#                 "sign": "HKTLbW8uEcVbym3JDqmSnekktX6Hyz+SIFoSrUCTAEk6ej7pNwp1mzVCv8Gjh8qAUBFIup0TF0vE7VLzilaxAA=="
#             },
#             "block_hash": "0004ada8efd8ff56d51deef0baaf9df068ca50db"
#         },
#         {
#             "block_id": 2,
#             "previous_hash": "0004ada8efd8ff56d51deef0baaf9df068ca50db",
#             "nonce": 376,
#             "transaction": {
#                 "tx_id": "797d36ea-6c3d-4ae5-9b80-9f6a22933b61",
#                 "source": "QOzzqVGhs0npyduHrfHyqvywKXbIcicREzBYNp344Y8=",
#                 "target": "QOzzqVGhs0npyduHrfHyqvywKXbIcicREzBYNp344Y8=",
#                 "amount": 100.0,
#                 "description": "pepe",
#                 "timestamp": "2025-06-18T00:25:37.236832",
#                 "sign": "x6hnJlX23Hon+kQ9wsJdaX7pbw7fhBLdzPRnjYSPFvLm91mDqspQMazCEXRUU5MBO0magsAxOMuhlKD5gei1Bw=="
#             },
#             "block_hash": "000ea6fe1fd4bdeb23478914867014febfb36dca"
#         },
#         {
#             "block_id": 3,
#             "previous_hash": "000ea6fe1fd4bdeb23478914867014febfb36dca",
#             "nonce": 1723,
#             "transaction": {
#                 "tx_id": "c97f0db0-3598-4632-83a9-1d31af0d91a6",
#                 "source": "Uq0aXfoO9t2MgY337uQI/hRtVCG4SXYnVX2zc4FWQNs=",
#                 "target": "Uq0aXfoO9t2MgY337uQI/hRtVCG4SXYnVX2zc4FWQNs=",
#                 "amount": 100.0,
#                 "description": "pepe",
#                 "timestamp": "2025-06-18T00:25:38.694900",
#                 "sign": "0iDl4M/wUhdA0TXF7tptoqS7HvOBvxYscxPG517Hvafzg19pA9LqUMtzOtJy5CvZ+bEN3wbco4CF4QKx29lgAw=="
#             },
#             "block_hash": "000b7a3a3dadcbb409531cf6c926014724137dea"
#         }
#     ]
# }

"""
## Coordinador 
- La tearea es el input y la transaccion es el input
- Tanto source como target son el mismo
- Meter el premio encadenado a la blockchain
- Hacer endpoint para obtner tx por hash

"""


"""
## Validador
- Cuando se obtenga la blockchain ver si  se puede validar que este bien encadenada que cumpla con el block_hash 
con lo que hashea
- Ver si se puede modificar el validate_register_tx.py para que trabaja parelo tal vez, o que lance workers para ayudarlo a procesar de forma distribuida

"""


"""
## Worker
- Tener algun raner que borre los workers que tiene registrado en coordiandor registrados, le pegariamos a un 
health y si no devuelve, lo borramos 
- Lógica del ttl para los workers, lo explico nehu, recordar que fue
- El worker tiene que mandar clave publica para su billetera cuando mina una tx minar clave publica para que 
termine con cierto valor ejemplo la parte final de la ip(E.j 104)
"""

### IN_PROGRESS


""" 
## POOL

-El pool dsp de cada ciclo pide las transacciones y tiene que ser un get por 'hash' para ver que tiene la ultima tx 
y ver si el es el ganador para crear nuevas transaciones 



Pool de tx, se deberia regfistrar los worker y determinar su potencia
1- Registrar workers por ip y poner si cuenta con placa CPU o GPU
2- Endpoint para que los workers soliciten transacciones
    El pool deberá
    2.1 Calcular la complejidad del desafio (cantidad de workers activos, tipo de worker(CPU/GPU), cantidad de TXs a minar, dificultad deseada)
        EJEMPLO: difficulty = base_difficulty + (0.1 * num_cpu_workers) + (0.05 * num_gpu_workers)
    2.2 Dividir las tareas
        Por cada TX pendiente
        2.2.1 Decidir un rango de nonce total (0 a 4,000,000)
        2.2.2 Dividir ese rango en n partes, donde n = número de workers registrados.
        {
            "transaction": {...},
            "hash_previo": "xxxx",
            "nonce_range": [start, end],
            "difficulty": difficulty
        }
    2.3 Verificar que se cunpla el desafio correctamente, guardarla para luego mandarsela al coordinador
    2.4 Pasado n tiempo publicar las tareas al coordinador

    El pool debe saber que workers estan activos para enviarles la/s TXs para que las minen
    Si detecta que hay pocas transacciones debería matar workers para evitar consumo innecesario.


    - Provar que mas de 1 worker se registre al pool
    - Tengo que ver como manejar el hash_previo desde el pool al worker
    - Sobre todo ver lo de manejar los tiempos desde el coordinador para que no se procesen 2 veces lo mismo


Ver como implementar lo de manejar el hash_previo entre tx entre el pool y workers


************************************************************************************************************************************
************************************************************************************************************************************
IMPLEMENTACIONES - INFORME:

COORDINADOR
    Ni bien inicia inserta, si no existe, el bloque GENESIS, con block_id: 0 y toda la config de la blockchain
    {
        "block_id": 0,
        "timestamp": 1750206335,
        "transaction": {
            "block_name": "GENESIS"
        },
        "config": {
            "max_tries_per_tx": 6,
            "monitoring_window_start": 5,
            "monitoring_window_end": 15,
            "publish_window_start": 50,
            "publish_window_end": 59,
            "window_period_seconds": 60
        },
        "block_hash": "ded1547cafc54950fc4dac9a3f09de8959d42eeb"
    },
    
    Habilita el endpoint GET /monitoring-tasks en el horario de XX:XX:05 hasta XX:XX:15
    Habilita el endpoint POST /publish-results en el horario de XX:XX:50 hasta XX:XX:59

    1. Registra workers (POST /register-worker con ip, puerto y tipo -CPU o GPU-)
    2. Enpoint que nos permite recuperar todos los workers registrados (GET /registered-workers)
    3. Nos permite recibir transacciones del cliente (POST /new-task -source, target, amount, description, sign-)
        3.1 Valida que este firmada la TX con la clave privada del source y si es correcto la encola en la cola de rabbit "earrings"
    4. Endpoint que nos permite obtener el estado de cierta transacccion/tarea por id (GET /get-transaction/{tx_id})
    5. Endpoint que nos permite obtener toda la blockchain completa, o las que esten en cierto rango que el cliente filtre, o por un id específico(GET /blockchain)
        Ejemplo: http://localhost:8989/blockchain (Todos los bloques) --- curl http://localhost:8989/blockchain?id=2 (Bloque de ese ID) --- curl http://localhost:8989/blockchain?start=2&end=4 (Bloques entre ese rango)
    6. Endpoint que utilizan los workers o pool para obtener todas las transacciones que deben ser minadas que se encuentran en in_progress(cola rabbitmq y redis por backup) (GET /monitoring-tasks)
    7. Endpoint POST /publish-results utilizado por los workers o pool para publicar todas las TXs procesadas/minadas o no

REDIS


RABBITMQ
    1- Cola earring (pendientes)
        1.1 Contendrá todas las TXs que el cliente le envía al coordiandor, y este último las validó.
    2- Cola in_progress (en proceso)
        2.1 Contendrá todas las TXs que el exchanger movió de la cola de earring para que luego sean procesadas por los workers/pool


EXCHANGER-MOVER
    Corre el hilo de forma ciclica en el horario de XX:XX:16 (osea despues que los workers o pool pidieron para minar)
    1. Cada cierto tiempo (E.j 1 minuto) se encarga de mover todas las transacciones que se encuentran en la 
        cola earring (pendiente) a la cola (in_progress) y por backup y facilidad de manejo, a redis también bajo 
        la key 'monitoring_transactions' para luego ser minadas por los workers/pool
        
        1.1 Además le cambia el estado de la TX a En proceso, y el challenge que obtiene del .env (CHALLENGE)

VALIDATOR-PUBLICADOR
    Corre el hilo de forma ciclica en el horario de XX:XX:00 (osea despues que los workers o pool publiquen sus resultados)
    1. Cada cierto tiempo (E.j 1 munuto) se corre:
        1.1 Obtiene todas las TXs de redis bajo la key de 'pending_transactions'
        1.2 Luego busca a aquel worker que haya resulto la mayor cantidad de TXs en el menor tiempo posible (para luego premiar)
        1.3 Ya teniendo el worker ganador, por c/u de sus TXs minadas, las validamos que cumplan con el desafío correctamente y encadena el bloque, 
            agregandole el block_id y el hash_previo correspondiente
        1.4 Luego de encadenar los bloques, calcula un porcentaje para el premio y se lo envia al worker ganador por ip/puerto /reward
        1.4.1 En el caso de que alguna/s no se haya/n procesado se les aumentará los intentos y pasado cierta cantidad de intentos (3 o 6) la TX sera borrada y 
            pasada a redis bajo la key 'dropped_txs' para tener como un historial de TXs no procesadas

POOL(FALTA)
    1. Endpoint para que los workers se registren, POST /register-worker facilitando su IP, puerto y tipo CPU o GPU
    2. Enpoint para obtener todos los workers que tiene registrado, GET /workers
    3. Cada cierto tiempo (E.j 1 minuto) el pool solicitará todas la transacciones que el coordinador tenga para procesar/minar y este :
        3.1 Calcular la complejidad del desafó
        3.2 Preparar las TXs para ser enviadas a los workers por rango de nonce, hash_previo y dificultad
        3.3 Enviar a cada worker registrado el 'pedazo' de TX a ser minada en los rangos especificados y la dificultad 


WORKER
    1. Al iniciar verifica si debe conectarse a un pool o coodirnador y de acuerdo a ello, se registra ante el mediante ip, puerto y tipo de placa (CPU o GPU)
    2. Dependiende a que nodo se tiene que conectar:
        Si se conecta al coordinador:
        2.1 Cada cierto tiempo (E.j 1 minuto sincronizado con el coordinador XX:XX:05 hasta XX:XX:15) les solicita al 
        coordinador (GET /monitoring-tasks) todas las transacciones que tenga para minarlas, junto con el último hash_previo
        
        2.2 Una vez recibida todas las TXs, las comienza a minar, para ello busca un nonce tal que satisfaga el 
            desafío de que al aplicar hash sobre la transacción (tx_id, source, target, sign,
              amount, description, timestamp, hash_previo) + el nonce su resultado comienze con cierto CHALLENGE.
        
        2.3 Pasado cierto tiempo (E.j 1 minuto sincronizado con coordinador para publicar entre XX:XX:50 hasta XX:XX:59) 
            se deberan publicar los resultados de las TXs que se hayan y minado y las que no a POST /publish-results    
        
        Si se conecta al pool (FALTAA):
        2.1 Cada cierto tiempo (E.j 1 minuto) el pool será el encargado de enviarle la/s TXs que debe procesar en cierto rango para buscar el nonce a partir
            de los workers que tenga registrado
    3. Enpoint GET /reward para obtener los puntos que ha obtenido por ser el ganador
    

""" 