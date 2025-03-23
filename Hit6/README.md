# Sistema Distribuido TCP - Registro de contactos (Hit #6)

## Descripción

Este sistema está compuesto por dos tipos de nodos:

- **Nodo D**: actúa como "Registro de contactos". Se encarga de llevar un registro en memoria de todos los nodos C que se están ejecutando.
- **Nodos C**: cada uno al iniciar se registra en D y obtiene la lista de otros nodos C para poder saludarlos. C también escucha en un puerto aleatorio.

Los nodos se comunican entre sí usando mensajes en formato JSON, y todo el sistema está montado sobre Docker.

> Esto permite levantar múltiples instancias de C que automáticamente se registran y se saludan sin necesidad de conocer las IPs de antemano.

---

## Instalación y uso

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

Al ejecutar ese comando, te va a pedir que ingreses un nombre para el nodo, por ejemplo: `node1_c`, `node2_c`, etc.

---

## Uso sin Make

Si no querés usar `make`, podés correr todo manualmente con los siguientes pasos:

### Crear la red (solo una vez)

```sh
docker network create hit6_network
```

### Levantar Nodo D

```sh
docker build -t hit6-node_d -f node_d/Dockerfile ./node_d
docker run --name node_d --network hit6_network -e NODE_NAME=node_d -e LISTEN_HOST=0.0.0.0 -e LISTEN_PORT=4000 -p 4000:4000 -v $(pwd)/logs/node_d:/app/logs hit6-node_d
```

### Levantar Nodo C (repetir para cada instancia)

```sh
docker build -t hit6-node_c -f node_c/Dockerfile ./node_c
docker run --name node1_c --network hit6_network -e NODE_NAME=node1_c -e D_HOST=node_d -e D_PORT=4000 -v $(pwd)/logs/:/app/logs hit6-node_c
```

Cambiá `node1_c` por el nombre que quieras asignarle al nodo.

---

## Cómo funciona

1. El nodo C arranca y se le asigna un **puerto aleatorio** donde escucha.
2. Se conecta a **D** (cuyo host/puerto se pasa por variable de entorno) y le envía:

   ```json
   { "node_name": "node1", "ip": "xxx.xxx.x.x", "port": 54321 }
   ```

3. D lo registra y le devuelve la lista de todos los nodos C que ya conoce.
4. C se conecta a cada uno de ellos y les envía un saludo.
5. Además, D reenvía la lista actualizada a todos los nodos C para que estén sincronizados.

---

## Logs

Cada nodo genera logs rotativos en su propia carpeta `logs/<nodo>/output.log`.

---

## Requisitos Python

Se utiliza:

```txt
python-dotenv
```

Este enfoque permite que los nodos escalen dinámicamente, sin configuración manual de pares.
