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
#description = "pepe"

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
#    "Blockchain":[
#       {
#          "block_id":1,
#          "previous_hash":"GENESIS",
#          "transaction":{
#             "source":"ench/qqMYacsN8c8/efQ1q1W6O/oewg0kw7pp47gM9I=",
#             "target":"ench/qqMYacsN8c8/efQ1q1W6O/oewg0kw7pp47gM9I=",
#             "amount":100.0,
#             "description":"pepe",
#             "timestamp":"2025-06-08T18:10:35.414218",
#             "sign":"SAyrX9w1NyDNBCmhyf0To1ainSuM1+ItFdIiP5CcoejpQBHKoGZIpcus6qEsoCRQS0JC7KUd7EQKW0F2r4HQBQ=="
#          },
#          "hash":"f94f385916e7a929050c9a40fc0f7d0d638b242d"
#       },
#       {
#          "block_id":2,
#          "previous_hash":"f94f385916e7a929050c9a40fc0f7d0d638b242d",
#          "transaction":{
#             "source":"CSep8ZbivnvOVIeHsbE8vRlqKo1SsvaPENfjIBZ6U0g=",
#             "target":"CSep8ZbivnvOVIeHsbE8vRlqKo1SsvaPENfjIBZ6U0g=",
#             "amount":100.0,
#             "description":"pepe",
#             "timestamp":"2025-06-08T18:10:49.866175",
#             "sign":"XUuWE4c5syDKJ4nPy4gnf3W/9TKQ4oEfjqDOkx3AdO+xlpFv8nk7V9dWcptZWsC+kzWmfWrXMOoIPS0aCEnDDg=="
#          },
#          "hash":"7624847ef589d96a8843ae49e6c42a534c13bab1"
#       },
#       {
#          "block_id":3,
#          "previous_hash":"7624847ef589d96a8843ae49e6c42a534c13bab1",
#          "transaction":{
#             "source":"j3Tdh/PMwPIif6pGo3cjSrnNbVev9bsRsenS4TvfV60=",
#             "target":"j3Tdh/PMwPIif6pGo3cjSrnNbVev9bsRsenS4TvfV60=",
#             "amount":100.0,
#             "description":"pepe",
#             "timestamp":"2025-06-08T18:10:33.643420",
#             "sign":"x4osJAlm1q0yIuryvOQj+6KTjVjE8dfqBGCS6ewMDnGzA8jjUGp9g3ndRrgI2tIKX97aDQ8rQsMDYPD9XCFfCg=="
#          },
#          "hash":"d90664fd4c23a2f0305de31da68df7799a99fdb8"
#       },
#       {
#          "block_id":4,
#          "previous_hash":"d90664fd4c23a2f0305de31da68df7799a99fdb8",
#          "transaction":{
#             "source":"m0e31ylDM2QpSaN6JYyK8kZkypK9PouicVJtU6kRXL8=",
#             "target":"m0e31ylDM2QpSaN6JYyK8kZkypK9PouicVJtU6kRXL8=",
#             "amount":100.0,
#             "description":"pepe",
#             "timestamp":"2025-06-08T18:10:33.029499",
#             "sign":"9MPNufMSMZa+4G/NSTI9zyjlFaogdHkNTIUOa+a1Z3fr75/MYT8OMzUX5Rpk7cEZt82DlB9HixfXYmrFzrd4AQ=="
#          },
#          "hash":"3ee47021083270d2ef27c2eea8c3e69ced394bd5"
#       }
#    ]
# }

## Validador
# ver cuando mete nuevo bloque en redis meta tmb el nonce y previus_hash y hash del bloque (estudiar o ver como validan la cadena de la blockchain )
# pensar lo del previous_hash, como obtenerlo, por ahí pensaba el coordiandor te manda todas las TX y el preious_hash, 
# a medida que el worker las va procesando tener lo que sería el previous_hash en una variable e ir actualizandola a medida que procesa y consumirla 

## Coordinador cuando inserta
# La tearea es el input y la transaccion es el input
# Tanto source como target son el mismo
# Tener o modificar endoiint blockchain para que si te enbian un id, devolver esa tx, si te envian un ranto [10,20] devolver las tx entre ese rango, si no viene nada devolver toda la blockchain

# Pensar si tenemos que guardar las TX dropiadas para obtner su status digamos y tener un histroioal de las dropiadas

## RELOJ para sincro
# Ver el tema de sincro de relojes


# Falta tambien lo del pool

# Worker
# Tener algun raner que borre los workers que tiene registrado en coordiandor registrados, le pegariamos a un health y si no devuelve, lo borramos 