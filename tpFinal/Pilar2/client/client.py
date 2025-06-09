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
#    "Blockchain":[
#       {
#          "block_id":1,
#          "previous_hash":"GENESIS",
#          "nonce":837,
#          "transaction":{
#             "tx_id":"41720bb6-52df-4d57-b735-1d8ffcac9f1c",
#             "source":"0y/Rn5iEPMG4KFGVS19lQtVPToXT6GUfBDw+gW4d49A=",
#             "target":"0y/Rn5iEPMG4KFGVS19lQtVPToXT6GUfBDw+gW4d49A=",
#             "amount":100.0,
#             "description":"pepe",
#             "timestamp":"2025-06-09T00:09:39.352941",
#             "sign":"WuURyIUzhER5e35qFq1/lTdTemVx26L/Jf8/LjVGN3aMUmZ+ZyEmNTtQ8L6H5ZMvofi+g0J5uqQmt6R6yvvbBA=="
#          },
#          "block_hash":"a89ea39dec1cda6b84a8edabe096d61953d9eff6"
#       },
#       {
#          "block_id":2,
#          "previous_hash":"a89ea39dec1cda6b84a8edabe096d61953d9eff6",
#          "nonce":2780,
#          "transaction":{
#             "tx_id":"1fa3373f-7bc8-4f05-928c-259eca0377db",
#             "source":"xV6+BqGWtM7Dd4Tfq5WPjeKK3GjLhc4pRBP4Qrg7ro8=",
#             "target":"xV6+BqGWtM7Dd4Tfq5WPjeKK3GjLhc4pRBP4Qrg7ro8=",
#             "amount":100.0,
#             "description":"pepe",
#             "timestamp":"2025-06-09T00:09:42.453014",
#             "sign":"B+rYyiLSTfoGgusvzN71nu03cwmpRnVhHXGnHK3MdSozZEwzybJycDw3kKBliH/bWupTDJdivxutiPawGmHCCA=="
#          },
#          "block_hash":"1eb08647341cce5717ae2b6c9cece2da9ce1c138"
#       },
#       {
#          "block_id":3,
#          "previous_hash":"1eb08647341cce5717ae2b6c9cece2da9ce1c138",
#          "nonce":656,
#          "transaction":{
#             "tx_id":"ad44e64d-cfa2-4725-87f8-f1b4b70d6e09",
#             "source":"y4Wy+PbXFJ7Vry1ok8TMfHXmAd3FJk4Attzi0VMvOVw=",
#             "target":"y4Wy+PbXFJ7Vry1ok8TMfHXmAd3FJk4Attzi0VMvOVw=",
#             "amount":100.0,
#             "description":"pepe",
#             "timestamp":"2025-06-09T00:09:56.850979",
#             "sign":"Do3SGLosoLDhM4Y/0K+p/63umnum/prGPmfSO4CP/R2va7y0VXMy16Ix1utldtlOzKD3TyT+JUk1Qlylb0xcCA=="
#          },
#          "block_hash":"c3392b7f7204bd841e056ce5ed39843242f0789f"
#       },
#       {
#          "block_id":4,
#          "previous_hash":"c3392b7f7204bd841e056ce5ed39843242f0789f",
#          "nonce":6182,
#          "transaction":{
#             "tx_id":"a8b76703-b5bc-45b7-9dcb-c4f9d3de6e50",
#             "source":"cBMZl2sU2UvUhhz2Ucli3Y5u6IGz12VnFhJPKlZ6ukk=",
#             "target":"cBMZl2sU2UvUhhz2Ucli3Y5u6IGz12VnFhJPKlZ6ukk=",
#             "amount":100.0,
#             "description":"pepe",
#             "timestamp":"2025-06-09T00:09:57.349771",
#             "sign":"WQR7etdKrYn9vC0lA7k59CTbAJgiu/27MkMlZjvD0WnJwm5XIlZLD3tdLKTjCRmJ19gVnOUI+B7X35EWtcjQCQ=="
#          },
#          "block_hash":"681b28347df9840fb95378eea8b2bd260acb6cab"
#       },
#       {
#          "block_id":5,
#          "previous_hash":"681b28347df9840fb95378eea8b2bd260acb6cab",
#          "nonce":11080,
#          "transaction":{
#             "tx_id":"8aaf96a1-3d48-49f7-b3c2-77d395cc6544",
#             "source":"RpWlzU8R/FN/6t7cAMGQXz8ZpMAIbus2zqXfjXovNzw=",
#             "target":"RpWlzU8R/FN/6t7cAMGQXz8ZpMAIbus2zqXfjXovNzw=",
#             "amount":100.0,
#             "description":"pepe",
#             "timestamp":"2025-06-09T00:09:56.310636",
#             "sign":"5dvSnh3YVFYvOaxg8rVFLBrhpFGb1ZShhlhOcZmxGbSii0KEtpuVfYEv1pPCynLCIkOmdWulCIXVALYSX2seDw=="
#          },
#          "block_hash":"56b66089db86d4fa1d5be60f485677400203241c"
#       }
#    ]
# }


## Coordinador cuando inserta -------- tener lo siguiente en cuenta, ver que ondis con esto
# La tearea es el input y la transaccion es el input
# Tanto source como target son el mismo

# Ver si se puede modificar el validate_register_tx.py para que trabaja parelo tal vez, o que lance workers para ayudarlo a procesar de forma distribuida

## Validador
# Cuando se obtenga la blockchain ver si  se puede validar que este bien encadenada que cumpla con el block_hash con lo que hashea


## RELOJ para sincro
# Ver el tema de sincro de relojes


# Falta tambien lo del pool

# Worker
# Tener algun raner que borre los workers que tiene registrado en coordiandor registrados, le pegariamos a un health y si no devuelve, lo borramos 


### IN_PROGRESS

