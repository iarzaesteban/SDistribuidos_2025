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
#             "transaction": {
#                 "block_name": "GENESIS"
#             },
#             "block_hash": "75d1b55850fced2b185594ccbbe74d0afb29b769"
#         },
#         {
#             "block_id": 1,
#             "previous_hash": "75d1b55850fced2b185594ccbbe74d0afb29b769",
#             "nonce": 17511,
#             "transaction": {
#                 "tx_id": "83809746-2547-4782-af0b-a4b29e6341f4",
#                 "source": "BjIQ4QQAJT93CpL5bStm4zmfenHXgtJFyu73IzqoJ74=",
#                 "target": "BjIQ4QQAJT93CpL5bStm4zmfenHXgtJFyu73IzqoJ74=",
#                 "amount": 100.0,
#                 "description": "pepe",
#                 "timestamp": "2025-06-16T03:43:54.543092",
#                 "sign": "axDIDgmZ67I/jQnUP64ZS/Pb8TKmDmZQPizSijtjekKH1owrqWIos5HIR/xFiwxt6jBlnGYyXVmIg1dchNklCg=="
#             },
#             "block_hash": "00091bd2f844b9e8b2668b601209c07c1daef5cd"
#         },
#         {
#             "block_id": 2,
#             "previous_hash": "00091bd2f844b9e8b2668b601209c07c1daef5cd",
#             "nonce": 1832,
#             "transaction": {
#                 "tx_id": "f8c45a6c-2057-4497-9de2-8b1cbb8a7f95",
#                 "source": "1Jh+cmcgTmz6HrgPCQ8gOKWhPCCGButoZfElibyawHM=",
#                 "target": "1Jh+cmcgTmz6HrgPCQ8gOKWhPCCGButoZfElibyawHM=",
#                 "amount": 100.0,
#                 "description": "pepe",
#                 "timestamp": "2025-06-16T03:43:53.861236",
#                 "sign": "7+H0++pH9qtbdv1MRTGyjU2QvKGrplsmyp/hOMlWxG3aVLxZxtrqabGOF7SRdWUYSBFUb1Y0HAdj4NAK41ELAA=="
#             },
#             "block_hash": "00085121dc6a9392a1353cff77617d4b7ef76a2a"
#         },
#         {
#             "block_id": 3,
#             "previous_hash": "00085121dc6a9392a1353cff77617d4b7ef76a2a",
#             "nonce": 5121,
#             "transaction": {
#                 "tx_id": "6339bf45-28d8-44eb-bbe1-63347b516adb",
#                 "source": "3RTzBKqPWMRRtNn9nHB8F2GCqJNbGjrWJl4Ouqco1x8=",
#                 "target": "3RTzBKqPWMRRtNn9nHB8F2GCqJNbGjrWJl4Ouqco1x8=",
#                 "amount": 100.0,
#                 "description": "pepe",
#                 "timestamp": "2025-06-16T03:43:55.098744",
#                 "sign": "qp3xWpjEUrv7z/7cDf6BwNvB2gwlJRrVvycLug9xk2BY4RiBTXghUl0GJv0RMTh1LO+rNhsNSRd58jmukgUpCQ=="
#             },
#             "block_hash": "0000c62fb68622419430a6efb846bcc16807a4f3"
#         }
#     ]
# }


## Coordinador cuando inserta -------- tener lo siguiente en cuenta, ver que ondis con esto
# La tearea es el input y la transaccion es el input
# Tanto source como target son el mismo
# Ver el tema de sincro de relojes, coordinador será el encargado de manejar los tiempos, si llega algo en un tiemmpo que no tiene habilitado ese endpoint patea



## Validador
# Cuando se obtenga la blockchain ver si  se puede validar que este bien encadenada que cumpla con el block_hash con lo que hashea
# Ver si se puede modificar el validate_register_tx.py para que trabaja parelo tal vez, o que lance workers para ayudarlo a procesar de forma distribuida


## Worker
# Tener algun raner que borre los workers que tiene registrado en coordiandor registrados, le pegariamos a un health y si no devuelve, lo borramos 
# Lógica del ttl para los workers, lo explico nehu, recordar que fue


 

### IN_PROGRESS


"""
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
IMPLEMENTACIONES:

COORDINADOR
    Ni bien inicia inserta, si no existe, el bloque GENESIS, con block_id: 0
    1. Registra workers (POST /register-worker con ip, puerto y tipo -CPU o GPU-)
    2. Enpoint que nos permite recuperar todos los workers registrados (GET /registered-workers)
    3. Nos permite recibir transacciones del cliente (POST /new-task -source, target, amount, description, sign-)
        3.1 Valida que este firmada la TX con la clave privada del source y si es correcto la encola en la cola de rabbit "earrings"
    4. Endpoint que nos permite obtener el estado de cierta transacccion/tarea por id (GET /get-transaction/{tx_id})
    5. Endpoint que nos permite obtener toda la blockchain completa, o las que esten en cierto rango que el cliente filtre, o por un id específico(GET /blockchain)
        Ejemplo: http://localhost:8989/blockchain (Todos los bloques) --- curl http://localhost:8989/blockchain?id=2 (Bloque de ese ID) --- curl http://localhost:8989/blockchain?start=2&end=4 (Bloques entre ese rango)
    6. Endpoint que utilizan los workers o pool para obtener todas las transacciones que deben ser minadas que se encuentran en in_progress(cola rabbitmq y redis por backup) (GET /monitoring-tasks)


REDIS


RABBITMQ
    1- Cola earring (pendientes)
        1.1 Contendrá todas las TXs que el cliente le envía al coordiandor, y este último las validó.
    2- Cola in_progress (en proceso)
        2.1 Contendrá todas las TXs que el exchanger movió de la cola de earring para que luego sean procesadas por los workers/pool


EXCHANGER
    1. Cada cierto tiempo (E.j 1 minuto) se encarga de mover todas las transacciones que se encuentran en la cola earring (pendiente) a la cola (in_progress) 
        y por backup y facilidad de manejo, a redis también bajo la key 'monitoring_transactions' para luego ser minadas por los workers/pool
        1.1 Además le cambia el estado de la TX a En proceso, y el challenge que obtiene del .env (CHALLENGE)

VALIDATOR
    1. Cada cierto tiempo (E.j 1 munuto) se corre:
        1.1 Obtiene todas las TXs de redis bajo la key de 'pending_transactions'
        1.2 Luego busca a aquel worker que haya resulto la mayor cantidad de TXs en el menor tiempo posible (para luego premiar)
        1.3 Ya teniendo el worker ganador, por c/u de sus TXs minadas, las validamos que cumplan con el desafío correctamente y encadena el bloque, 
            agregandole el block_id y el hash_previo correspondiente
        1.4 Luego de encadenar los bloques, calcula un porcentaje para el premio y se lo envia al worker ganador por ip/puerto /reward
        1.4.1 En el caso de que alguna/s no se haya/n procesado se les aumentará los intentos y pasado cierta cantidad de intentos (3 o 6) la TX sera borrada y 
            pasada a redis bajo la key 'dropped_txs' para tener como un historial de TXs no procesadas

POOL
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
        2.1 Cada cierto tiempo (E.j 1 minuto) les solicita al coordinador (GET /monitoring-tasks) todas las transacciones que tenga para minarlas, junto con el último hash_previo
        2.2 Una vez recibida todas las TXs, las comienza a minar, para ello busca un nonce tal que satisfaga el desafío de que al aplicar hash sobre la 
            transacción (tx_id, source, target, sign, amount, description, timestamp, hash_previo) + el nonce su resultado comienze con cierto CHALLENGE.
        2.3 Pasado cierto tiempo (E.j 5 minutos) se deberan publicar los resultados de las TXs que se hayan y minado y las que no a POST /publish-results    
        Si se conecta al pool:
        2.1 Cada cierto tiempo (E.j 1 minuto) el pool será el encargado de enviarle la/s TXs que debe procesar en cierto rango para buscar el nonce a partir
            de los workers que tenga registrado
    3. Enpoint GET /reward para obtener los puntos que ha obtenido por ser el ganador
    

""" 