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

# Ver si se puede modificar el validate_register_tx.py para que trabaja parelo tal vez, o que lance workers para ayudarlo a procesar de forma distribuida

## Validador
# Cuando se obtenga la blockchain ver si  se puede validar que este bien encadenada que cumpla con el block_hash con lo que hashea


## RELOJ para sincro
# Ver el tema de sincro de relojes, coordinador será el encargado de manejar los tiempos, si llega algo en un tiemmpo que no tiene habilitado ese endpoint patea


# Falta tambien lo del pool

# Worker
# Tener algun raner que borre los workers que tiene registrado en coordiandor registrados, le pegariamos a un health y si no devuelve, lo borramos 


# Moficiar el tema del hash_previo se manda toda la TX con el last_hash y el minero tiene que irse guardarse el ultimo hash para ir encadenando

#Endpoint para buscar tx por hash.
# Pool de tx, se deberia regfistrar los worker y determinar su potencia

# Lógica del ttl para los workers, lo explico nehu, recordar que fue
#manejar sincronizmos coordinador
 

### IN_PROGRESS
