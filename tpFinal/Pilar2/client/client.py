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
