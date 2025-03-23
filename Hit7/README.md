# Sistema Distribuido TCP - Sistema de Inscripciones por Ventana (Hit #7)

## Descripción

Este sistema distribuido está compuesto por:

- **Nodo D**: actúa como registro de contactos e implementa un **sistema de inscripciones por ventana de tiempo**. Cada ventana dura **1 minuto**.
- **Nodos C**: se registran en el nodo D y solo pueden ver a los otros nodos activos en la **ventana actual**.  
  Los nodos C que se conectan durante una ventana, son anotados para la **próxima**.

Al final de cada minuto:

- Nodo D guarda en un archivo JSON la lista de nodos activos.
- Se pasa el registro "futuro" a la ventana actual.
- Cualquier nuevo nodo que se registre pasará a la siguiente ventana.

---

## Instalación y uso (con Make)

### 1. Generamos la imagen para el nodo D

```sh
make build_node_d
```

### 2. Generamos la imagen para el nodo C

```sh
make build_node_c
```

### 3. Levantamos un nodo D

```sh
make up_node_d
```

### 4. Para levantar nodos C

```sh
make up_node_c
```

Esto deja al nodo D escuchando en el puerto 4001 y gestionando las ventanas de inscripción.

### 5. Levantar nodos C (pueden ser múltiples)

```sh
make up_node_c
```

El comando te va a pedir que ingreses un nombre para el nodo C.  
Cada uno se registrará para la **próxima** ventana.

---

## Uso sin Make

### 1. Crear la red (solo una vez)

```sh
docker network create hit7_network
```

### 2. Construir y levantar el nodo D

```sh
docker build -t hit7-node_d -f node_d/Dockerfile ./node_d
docker run --name node_d --network hit7_network -e NODE_NAME=node_d -e LISTEN_HOST=0.0.0.0 -e LISTEN_PORT=4001 -p 4001:4001 -v $(pwd)/logs/node_d:/app/logs hit7-node_d
```

### 3. Construir la imagen del nodo C

```sh
docker build -t hit7-node_c -f node_c/Dockerfile ./node_c
```

### 4. Levantar un nodo C

```sh
docker run --name node1_c --network hit7_network -e NODE_NAME=node1_c -e D_HOST=node_d -e D_PORT=4001 -v $(pwd)/logs/:/app/logs hit7-node_c
```

Repetí ese comando con diferentes nombres para lanzar más nodos C.

---

## Cómo funciona el sistema de inscripción

- Cada nodo C se registra indicando su IP, puerto y hora de ingreso.
- Si el registro se hace a las 11:28:34, entra en la **ventana de las 11:29**.
- Cuando llega las 11:29:00:
  - Se guarda en archivo JSON la ventana que se está cerrando.
  - La lista de inscritos pasa a estar "activa".
  - Se comienza a aceptar inscripciones para la siguiente ventana (11:30).

Los nodos C:

- Solo conocen a los nodos **activos en la ventana actual**.
- No conocen con quién van a compartir la próxima ventana.

---

## Almacenamiento de inscripciones

- Cada archivo se guarda con nombre `inscriptions_YYYY-MM-DD_HH-MM.json` en el directorio `/logs`.
- Contiene la lista de nodos registrados en esa ventana.

---

## Requisitos Python

Solo se necesita:

```txt
python-dotenv
```
