## Este proyecto configura un entorno con PostgreSQL ejecutándose en un contenedor y un cliente para poder conectarse, ejecutar consultas, ver las tablas y manipular datos.

### Posicionarnos en el directorio correcto

```sh
cd docker_database_connection
```

### Levantar los contenedores

```sh
docker-compose up --build -d
```

### Verificar que los contenedores están corriendo

```sh
docker ps
```

### Acceder al contenedor cliente

```sh
docker exec -it postgres_client bash
```

### Conectarse a la base de datos desde el cliente

```sh
psql -h db -U "$POSTGRES_USER" -d "$POSTGRES_DB"
```

### Verificar las tablas

```sh
\dt
```

### Consultar los datos en la tabla users

```sh
SELECT * FROM users;
```

Crear cluster kubernetes (Linux):

- Crear cuenta de Google Cloud
- Instalar la CLI de GCP (gcloud)
- Habilitar la API de Kubernetes Engine
- Crear un clúster con Google Kubernetes Engine

Instalar la CLI de Google Cloud

```sh
sudo apt update && sudo apt install apt-transport-https ca-certificates gnupg curl -y
```

# 1. Añadir la clave GPG

curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -

# 2. Añadir el repositorio a APT

echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" \
 | sudo tee /etc/apt/sources.list.d/google-cloud-sdk.list

# 3. Importar la clave en el nuevo sistema (mejor que apt-key)

curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg \
 | gpg --dearmor \
 | sudo tee /usr/share/keyrings/cloud.google.gpg > /dev/null

# 4. Actualizar los repositorios

sudo apt update

# 5. Instalar el SDK

sudo apt install google-cloud-sdk -y

# 6. Verificamos que se haya instalado correctamente

gcloud version

# 7. Iniciamos gcloud (seleccionamos uno existente o creamos uno)

gcloud init

# Elegimos un proyecto:

gcloud config set project nombre-proyecto-ejemplo

# Activamos el servicio de Kubernetes (GKE)

ir a https://console.cloud.google.com/billing y habillitar Billing account al poryecto que querés usar y luego,

gcloud services enable container.googleapis.com

# Instalamos plugins para gke en gcloud

sudo apt-get install google-cloud-cli-gke-gcloud-auth-plugin

# Creamos un cluster kubernetes:

gcloud container clusters create <mi-cluster> \
 --zone us-central1-c \
 --num-nodes=1

# Conectamos kubectl con el clúster

gcloud container clusters get-credentials <mi-cluster> --zone us-central1-c

# Verifiquemos que todo quedo funcionando

kubectl get nodes

# Si el cluster fue creado correctamente hacer lo siguiente para conectar kubctl con el cluster

gcloud container clusters get-credentials <mi-cluster> --zone us-central1-c

# Listamos los proyectos de gcloud con:

gcloud projects list

# Liberar todo (ahorrar en gcloud - nodos, discos, redes) o poner los nodos en 0 temporalmente

gcloud container clusters delete <mi-cluster> \
 --zone us-central1-c

o

gcloud container clusters resize <mi-cluster> \
 --num-nodes=0 \
 --zone us-central1-c

# Compartir kubectl config

cp ~/.kube/config <mi-cluster-kubeconfig>

Compartir el <mi-cluster-kubeconfig>

## Algunas pruebas:

# Creamos un Docker ConfigMap con este archivo en Kubernetes (donde este init-db.sql)

kubectl create configmap postgres-initdb-config \
 --from-file=init-db.sql=init-db.sql

# Podemos verificarlo con

kubectl describe configmap postgres-initdb-config

# "Apagar" todo para no generar cobros

$ kubectl delete -f docker_database_connection/deployment-postgres.yaml
