import requests
import base64
import os
from datetime import datetime, timezone
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
from concurrent.futures import ProcessPoolExecutor, as_completed
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env.client")

ip = "172.22.1.3"  # Simulamos IP del contenedor
ip_split = ip.split(".")
target_suffix = ip_split[1] + ip_split[2] + ip_split[3]
print(f"El sufijo a buscar es {target_suffix}")
MAX_WORKERS = os.cpu_count()

def generate_key_pair():
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )
    public_hex = public_bytes.hex()

    if public_hex.startswith(target_suffix):
        priv_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        pub_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return priv_pem, pub_pem, public_hex

    return None

def worker(_):
    while True:
        res = generate_key_pair()
        if res:
            return res

def main():
    nct_url = os.getenv("NCT_URL", "http://localhost:8989") + "/new-task"
    print(f"Enviando transacción a: {nct_url}")
    print(f"Buscando clave pública que comience con '{target_suffix}' usando {MAX_WORKERS} cores...")

    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(worker, i) for i in range(MAX_WORKERS)]
        for future in as_completed(futures):
            priv_pem, pub_pem, public_hex = future.result()
            private_key_obj = serialization.load_pem_private_key(priv_pem, password=None)

            timestamp = datetime.now(timezone.utc).isoformat()
            amount = 100.0
            description = "Prueba de transacción (GCloud)"

            private_key_target = ed25519.Ed25519PrivateKey.generate()
            public_key_target = private_key_target.public_key()

            target_raw = public_key_target.public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw
            )
            target_b64 = base64.b64encode(target_raw).decode()

            message = f"{public_hex}{target_b64}{amount}{description}{timestamp}".encode()
            signature = private_key_obj.sign(message)
            signature_b64 = base64.b64encode(signature).decode()

            tx = {
                "source": public_hex,
                "target": target_b64,
                "amount": amount,
                "description": description,
                "timestamp": timestamp,
                "sign": signature_b64
            }

            response = requests.post(nct_url, json=tx)
            print("Status Code:", response.status_code)
            try:
                print("Response:", response.json())
            except Exception:
                print("Error al interpretar la respuesta:", response.text)
            break

if __name__ == "__main__":
    main()
