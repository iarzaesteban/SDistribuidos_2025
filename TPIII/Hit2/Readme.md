# TP3 hit2.

## Procesamiento de Imágenes Distribuido con Filtro Sobel

## Autores

Iarza Esteban
Rodriguez Emanuel

## Descripcion del proyecto:

Este proyecto implementa un sistema distribuido de procesamiento de imágenes en la nube, aplicando el filtro Sobel para detección de bordes. El procesamiento se realiza de manera distribuida dividiendo una imagen en partes, las cuales son procesadas por múltiples workers en contenedores separados. Luego, un contenedor maestro se encarga de ensamblar el resultado final y almacenarlo nuevamente en un bucket de Google Cloud Storage.

## Tecnologías Utilizadas

Google Cloud Platform (GCP)

Google Cloud Storage (GCS)

Docker

Terraform

Bash scripting

Python

gsutil para sincronización de archivos

## Infraestructura en GCP (Terraform)

google_compute_instance
Creamos una instancia de VM llamada maestro-instance con Debian 12 y Docker preinstalado. Se le asignan permisos de cloud-platform para poder interactuar con GCS y se le inyecta un script de arranque personalizado (startup-script.sh).

google_storage_bucket
Se crea un bucket llamado ${project_id}-images donde se definen dos carpetas lógicas:

input/: donde el usuario sube imágenes a procesar.

output/: donde se guardan los resultados procesados.

## Despliegue Automático (startup-script.sh)

El script de arranque automatiza el setup de la instancia maestro:

1. Instala dependencias
   docker.io, Google Cloud SDK (gsutil)

2. Autenticación en DockerHub
   Obtiene credenciales vía metadata e inicia sesión para hacer pull de imágenes.

   - iarzaesteban94/maestro:latest
   - iarzaesteban94/worker:latest

3. Crea carpetas locales
   /data/input
   /data/output
   /data/shared_volume

Se evita el uso de gcsfuse, utilizando sincronización con gsutil rsync.

4. Sincronización automática
   sync_gcs_input.sh: sincroniza del bucket GCS → /data/input
   sync_gcs_output.sh: sincroniza de /data/output → bucket GCS

Ambos scripts se ejecutan en segundo plano con nohup.

### Worker

Imagen pequeña con Python + OpenCV

Lógica que toma porción de imagen, aplica Sobel y guarda en output

### Maestro

Imagen con Python que:

Monitorea bucket

Descarga imagen, la corta, lanza workers

Recolecta resultados y guarda en output

## Configuraciones

### Permisos Requeridos

La instancia necesita una cuenta de servicio con los siguientes permisos:

roles/storage.admin

roles/compute.instanceAdmin

roles/container.admin

1. Creamos el proyecto en google cloud

- Ir a https://console.cloud.google.com/
- Creamos nuevo proyecto o new project
- Colocamos el nombre del proyecto
- Oprimimos botón crear o create
- Anotarno en algún lado el project ID

Project info:

Project name
sobel-distribuido
Project number
261274038705
Project ID
sobel-distribuido

2. Activamos las API necesarias:
   Desde la consola web
   2.1 Ir a Api & Services, luego Library
   2.2 Habilitar Compute Engine API y Cloud Storage API
   2.3 Crear una new keys .json y guardarla localmente. JAMÁS DEBE SER ENVIADA A NADIE.

3. Configuramos todo localemente

3.1 Intalamos gcloud y terraform
Verificamos las versiones:

```bash
gcloud version
terraform version
```

3.2 Nos logueamos con google cloud

```bash
gcloud auth login

```

## Archivo de configuración sensible

Este proyecto requiere un archivo `secret.auto.tfvars` con credenciales de GCP y DockerHub para poder funcionar. Este archivo **no se encuentra en el repositorio por motivos de seguridad**.

Si formás parte del equipo o necesitás correr el proyecto, solicitá el archivo `secret.auto.tfvars` al responsable del proyecto.

Además, asegurate de tener el archivo JSON de credenciales de Google Cloud en una ruta local accesible, y modificá `credentials_file` en `secret.auto.tfvars` para que apunte a dicha ruta.

## Flujo de deploy

1. Dentro del directorio SDistribuidos_2025/Hit2/

```bash
terraform apply
```

## Flujo de Procesamiento

1. El usuario sube una imagen al bucket /input con:

```bash
gsutil cp images/imagen1.jpg gs://sobel-distribuido-images/input/

```

## Comando utiles

- Destuir todo lo deployado con terraform apply:

```bash
terraform destroy
```

- Ver si se subió la imagen correctamente en el bucket:

```bash
gsutil ls gs://sobel-distribuido-images/input/
```

- Ver el resultado del procesamiento de la imagen sobel:

```bash
gsutil ls gs://sobel-distribuido-images/output/
```

- Descargar imagen del bucket /output:

```bash
gsutil cp gs://sobel-distribuido-images/output/processed_imagen1.png ~/images/
```
