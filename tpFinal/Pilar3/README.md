# PILAR 3 - SD 2025 - BlockChain

## Crear el proyecto

gcloud projects create blockchainsd2025 --name="BlockchainSD" --set-as-default

### obtener tu billing-account-id, ejecutar:

gcloud beta billing accounts list

### Vinculá el proyecto a esa cuenta con este comando (reemplazando <BILLING_ACCOUNT_ID> con el ID real que veas en la consola -comando anterior-):

gcloud beta billing projects link blockchainsd2025 \
 --billing-account=<BILLING_ACCOUNT_ID>

### Verifica que esté activo:

gcloud config set project blockchainsd2025

### Habilitamos las APIs :

gcloud services enable container.googleapis.com \
 compute.googleapis.com \
 iam.googleapis.com \
 cloudbuild.googleapis.com

## Crear una cuenta de servicio para Terraform

gcloud iam service-accounts create terraform \
 --description="Cuenta para administrar GKE desde Terraform" \
 --display-name="Terraform SA"

### Asignar permisos:

gcloud projects add-iam-policy-binding blockchainsd2025 \
 --member="serviceAccount:terraform@blockchainsd2025.iam.gserviceaccount.com" \
 --role="roles/container.admin"

gcloud projects add-iam-policy-binding blockchainsd2025 \
 --member="serviceAccount:terraform@blockchainsd2025.iam.gserviceaccount.com" \
 --role="roles/compute.admin"

gcloud iam service-accounts keys create terraform-key.json \
 --iam-account=terraform@blockchainsd2025.iam.gserviceaccount.com

## Autenticarse con GCP para usar Docker

gcloud auth configure-docker

## Build y push

docker build -f coordinador/deploy/Dockerfile -t gcr.io/blockchainsd2025/coordinador:latest coordinador
docker push gcr.io/blockchainsd2025/coordinador:latest

### Verificar que se haya pusheado correctamente la imagen

gcloud container images list-tags gcr.io/blockchainsd2025/coordinador

## Autenticar

gcloud auth application-default login

## Crear buckets

gsutil mb -p blockchainsd2025 -c standard -l us-central1 gs://blockchainsd2025-terraform-state
gsutil versioning set on gs://blockchainsd2025-terraform-state

## Deploy con Terraform

cd infra/

make init
make plan
make apply

## Probar con navegador o curl

terraform output coordinador_url --> nos devolverá una <IP>

curl http://<IP>

## En caso de tener que regenrar la imagen del coordinador

### Usamos tags para la imagen

- Usamos el último commit como tag único, dentro de infra/

```bash
  TAG=$(git rev-parse --short HEAD)
```

- Obtenemos el hash del TAG

```bash
echo "Usando tag: $TAG"
```

#### El comando anterior nos devolverá un hash que será colocado en el archivo terraform.tfvars indicando el tag de la imagen de docker

-Build con ese tag, desde Pilar3/

```bash
docker build -f coordinador/deploy/Dockerfile -t gcr.io/blockchainsd2025/coordinador:$TAG coordinador
```

- Push a GCR, desde Pilar3/

```bash
docker push gcr.io/blockchainsd2025/coordinador:$TAG
```

## Creamos el pod para redis
