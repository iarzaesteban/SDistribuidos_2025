import base64
import requests
from datetime import datetime, timezone
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

timestamp = datetime.now(timezone.utc).isoformat()

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
#             "timestamp": 1750295917,
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
#             "block_hash": "8a8c22117d74047203bb1ae1c709231cd3215ed4"
#         },
#         {
#             "block_id": 1,
#             "previous_hash": "8a8c22117d74047203bb1ae1c709231cd3215ed4",
#             "nonce": 6061,
#             "miner": "2207a7388e8bb3b7c3380c6186c22800115f1711eaee7a9caf59c3cfa8b0e04b",
#             "prefix": "000",
#             "transaction": {
#                 "tx_id": "2074b98d-ccd0-4aa8-996d-f5cb7484f14c",
#                 "source": "2207b4e00d4f704c7ed61acfd4e8603ab1bd10d53a0b46a7cca8b1b22f1b0c45",
#                 "target": "8J+esJ+ymea5qK51MP5xSvgdWB5CANOBNdJh8r+iDSY=",
#                 "amount": 100.0,
#                 "description": "pepe",
#                 "timestamp": "2025-06-19T01:18:41.421402+00:00",
#                 "sign": "pFnVYntXeza9xa76uBMkHpcVwr953ZaPLtCi6JDl1ZacuKu+YO/hqiNuzfu2LHMPF3YrbqV34Nyz29zlBCHTAQ=="
#             },
#             "block_hash": "000b5f1ff95210dda62d32b09bc87b5997b654c1"
#         },
#         {
#             "block_id": 2,
#             "previous_hash": "000b5f1ff95210dda62d32b09bc87b5997b654c1",
#             "nonce": 5866,
#             "miner": "2207a7388e8bb3b7c3380c6186c22800115f1711eaee7a9caf59c3cfa8b0e04b",
#             "prefix": "000",
#             "transaction": {
#                 "tx_id": "a056ab4b-b616-4d8c-9a77-e1ce054c5163",
#                 "source": "2207a42a52f3e65493e7b901a5f272ba5a530fec65e13967c5eabc9ed1881df3",
#                 "target": "8AgYbndTPYo8aBpZRkm3q+DjBSqRlFyUIPafhRkb/Y0=",
#                 "amount": 100.0,
#                 "description": "pepe",
#                 "timestamp": "2025-06-19T01:18:56.728578+00:00",
#                 "sign": "uRe8AghbTNMiiWR6DBhkaq8h8sy8AREP16QSh3ZnuXpZYp9OJFjImj8+1WiatXyDkgp3crecNQHugha78AynDQ=="
#             },
#             "block_hash": "000c99ebe3c7d2f8db355ae92b0bea84bf2d6f03"
#         },
#         {
#             "block_id": 3,
#             "previous_hash": "000c99ebe3c7d2f8db355ae92b0bea84bf2d6f03",
#             "nonce": 0,
#             "miner": "COORDINATOR",
#             "prefix": "reward",
#             "transaction": {
#                 "tx_id": "7e602486-edff-4da3-be49-fa4e7628797a",
#                 "source": "0000000000",
#                 "target": "2207a7388e8bb3b7c3380c6186c22800115f1711eaee7a9caf59c3cfa8b0e04b",
#                 "amount": 20000.0,
#                 "description": "Recompensa minería",
#                 "timestamp": "2025-06-19T01:21:00.919912",
#                 "sign": "-"
#             },
#             "block_hash": "ac53908d6f6d1fd97d80af5f72b56c681f44d5b0e8e7e7b326b46e7c39c70ab8"
#         },
#         {
#             "block_id": 4,
#             "previous_hash": "ac53908d6f6d1fd97d80af5f72b56c681f44d5b0e8e7e7b326b46e7c39c70ab8",
#             "nonce": 10717,
#             "miner": "2207a7388e8bb3b7c3380c6186c22800115f1711eaee7a9caf59c3cfa8b0e04b",
#             "prefix": "000",
#             "transaction": {
#                 "tx_id": "7e9492e0-57c6-49bb-aad9-330f3dac0ac9",
#                 "source": "2207cce9c5e6414c6bb1282e11866c9be7f6d21d5d2af35d3573b6b6325229be",
#                 "target": "pim8G6kb4EiwloFoKulYmBQpit0fszhbJxwj9SxHfoc=",
#                 "amount": 100.0,
#                 "description": "pepe",
#                 "timestamp": "2025-06-19T01:28:13.089231+00:00",
#                 "sign": "RD0vNg8qF26+DmDm+rylfPDMhTi7+bfVv98Q0Q79mr3gzX9ZpFNfaS0U5bS4t1oM9b0uS8dBnWu+QVjpgzJsBg=="
#             },
#             "block_hash": "000ce68917350fbf0b2a8b98950b5014be6d0abc"
#         },
#         {
#             "block_id": 5,
#             "previous_hash": "000ce68917350fbf0b2a8b98950b5014be6d0abc",
#             "nonce": 0,
#             "miner": "COORDINATOR",
#             "prefix": "reward",
#             "transaction": {
#                 "tx_id": "8d969c80-11a4-45ae-a1ad-83b4893af34d",
#                 "source": "0000000000",
#                 "target": "2207a7388e8bb3b7c3380c6186c22800115f1711eaee7a9caf59c3cfa8b0e04b",
#                 "amount": 20000.0,
#                 "description": "Recompensa minería",
#                 "timestamp": "2025-06-19T01:30:00.396407",
#                 "sign": "-"
#             },
#             "block_hash": "2d73a443fca1bf768fb7becaa7f8310d897c98f44f1485e213296b761d6dd2e9"
#         },
#         {
#             "block_id": 6,
#             "previous_hash": "2d73a443fca1bf768fb7becaa7f8310d897c98f44f1485e213296b761d6dd2e9",
#             "nonce": 7068,
#             "miner": "2207a7388e8bb3b7c3380c6186c22800115f1711eaee7a9caf59c3cfa8b0e04b",
#             "prefix": "000",
#             "transaction": {
#                 "tx_id": "b2c3c4c1-53ca-4f6b-b9e8-882646499271",
#                 "source": "220798ecee0532ea3894fc6d72ee65bcc9963b9ae9f29966d4c31e0b265bc592",
#                 "target": "MmnN78M2EtSAA/HzWHx2DWSgc+oNUrmU0PZkwI750ew=",
#                 "amount": 100.0,
#                 "description": "pepe",
#                 "timestamp": "2025-06-19T01:28:41.879586+00:00",
#                 "sign": "Akn4cJVSFza+6BL/DZRgNKXNnDXLWqqb5mDB0mxNxxQVGDp/gnfiL1x0FwtOzoNPCZZTOcgUJ1nqHmaX6IV1DQ=="
#             },
#             "block_hash": "0001f131cb5b014cdc6497cf5b40bf755cb421a0"
#         },
#         {
#             "block_id": 7,
#             "previous_hash": "0001f131cb5b014cdc6497cf5b40bf755cb421a0",
#             "nonce": 5831,
#             "miner": "2207a7388e8bb3b7c3380c6186c22800115f1711eaee7a9caf59c3cfa8b0e04b",
#             "prefix": "000",
#             "transaction": {
#                 "tx_id": "bbb1b165-a7bc-47aa-990c-64e3db18b758",
#                 "source": "2207ccb6b51072429786479b4f97fb6e8539d0323f6a46273b572ce0e3b19831",
#                 "target": "Oeo6iyGXrCLl0152Kt+V9H2cJxtw3/QwFDzMivjt3Ds=",
#                 "amount": 100.0,
#                 "description": "pepe",
#                 "timestamp": "2025-06-19T01:28:32.008618+00:00",
#                 "sign": "xr9P/c7cxoqzDmRw50Lo+ZWy3GJKyaYOq9cMOXfCLA3yQn3w7t21daSVviPGU7hLvXZV5aVye7Sz7F+jXufrDQ=="
#             },
#             "block_hash": "00007c0fae065ab498879d94afa3fc01c359d74d"
#         },
#         {
#             "block_id": 8,
#             "previous_hash": "00007c0fae065ab498879d94afa3fc01c359d74d",
#             "nonce": 314,
#             "miner": "2207a7388e8bb3b7c3380c6186c22800115f1711eaee7a9caf59c3cfa8b0e04b",
#             "prefix": "000",
#             "transaction": {
#                 "tx_id": "c488ba64-06eb-4478-bd5f-9f6cddcbef12",
#                 "source": "22077e40351fb89d68c84f93fa1646d1c218ad46659386f37339c6861d460b72",
#                 "target": "RSmGRXDzANYrkqjpmk71FPISgVSzSqfzISk/5sfqpO0=",
#                 "amount": 100.0,
#                 "description": "pepe",
#                 "timestamp": "2025-06-19T01:28:23.180291+00:00",
#                 "sign": "WDNdM/lxFPBcFLQiRh6sVrQwPKPiPaXETy/m0CISoTlY4IFYuH7Z5bXw0aB6rt1QHwX8jhdFjxN05NpVz5sZAQ=="
#             },
#             "block_hash": "000846948a7a808a75d40b14c5f2c851ea4d0262"
#         },
#         {
#             "block_id": 9,
#             "previous_hash": "000846948a7a808a75d40b14c5f2c851ea4d0262",
#             "nonce": 0,
#             "miner": "COORDINATOR",
#             "prefix": "reward",
#             "transaction": {
#                 "tx_id": "a7d6bb6e-8275-4d5a-b5a3-8124a4b9becf",
#                 "source": "0000000000",
#                 "target": "2207a7388e8bb3b7c3380c6186c22800115f1711eaee7a9caf59c3cfa8b0e04b",
#                 "amount": 20000.0,
#                 "description": "Recompensa minería",
#                 "timestamp": "2025-06-19T01:31:00.533757",
#                 "sign": "-"
#             },
#             "block_hash": "31f08456bcfebd4357751c256825ec79ca3b7a062d1b85c947e0d5f467e8fd7a"
#         }
#     ]
# }


        

"""
## Coordinador 
- La tearea es el input y la transaccion es el input
- Tanto source como target son el mismo
- Meter el premio encadenado a la blockchain

"""


"""
## Validador
- Cuando se obtenga la blockchain ver si  se puede validar que este bien encadenada que cumpla con el block_hash 
con lo que hashea
- Ver si se puede modificar el validate_register_tx.py para que trabaja parelo tal vez, o que lance workers para 
ayudarlo a procesar de forma distribuida
- Validar que no encadena 2 veces la misma tx en caso de que algo se cayó

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
    8. Endpoint GET /get-block/{block_hash} este endpoint nos permite obtener una trasacción de la blockchain por block_hash 

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