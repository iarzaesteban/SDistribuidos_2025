#! /bin/bash

# Instalamos dependencias
apt-get update
apt-get install -y docker.io wget apt-transport-https ca-certificates gnupg curl

# Instalamos Google Cloud SDK (para usar gsutil)
echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" | \
  tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -
apt-get update && apt-get install -y google-cloud-sdk

# Habilitamos Docker
systemctl start docker
systemctl enable docker
usermod -aG docker $USER

# Login a DockerHub
DOCKER_USER=$(curl "http://metadata.google.internal/computeMetadata/v1/instance/attributes/dockerhub_user" -H "Metadata-Flavor: Google")
DOCKER_PASS=$(curl "http://metadata.google.internal/computeMetadata/v1/instance/attributes/dockerhub_pass" -H "Metadata-Flavor: Google")
echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin

# Obtenemos el nombre del bucket desde metadata
BUCKET_NAME=$(curl "http://metadata.google.internal/computeMetadata/v1/instance/attributes/bucket_name" -H "Metadata-Flavor: Google")

# Creamos carpetas locales reales (no FUSE)
mkdir -p /data/input
mkdir -p /data/output
mkdir -p /data/shared_volume

# Script para sincronizar bucket GCS → carpeta local
cat <<EOF > /usr/local/bin/sync_gcs_input.sh
#!/bin/bash
while true; do
  gsutil -m rsync -r gs://sobel-distribuido-images/input/ /data/input/
  sleep 5
done
EOF
chmod +x /usr/local/bin/sync_gcs_input.sh
nohup /usr/local/bin/sync_gcs_input.sh > /var/log/sync_input.log 2>&1 &

# Script para sincronizar carpeta local → bucket GCS
cat <<EOF > /usr/local/bin/sync_gcs_output.sh
#!/bin/bash
while true; do
  gsutil -m rsync -r /data/output/ gs://sobel-distribuido-images/output/
  sleep 5
done
EOF
chmod +x /usr/local/bin/sync_gcs_output.sh
nohup /usr/local/bin/sync_gcs_output.sh > /var/log/sync_output.log 2>&1 &

# Pull de imagen del maestro
docker pull iarzaesteban94/maestro:latest

# Ejecutamos contenedor maestro con volúmenes REALES (no gcsfuse)
docker run -d --name maestro \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /data/input:/app/input \
  -v /data/output:/app/output \
  -v /data/shared_volume:/app/shared_volume \
  iarzaesteban94/maestro:latest