# Nodo C - Cliente y Servidor TCP en Docker (mensajes JSON)

## Descripción

Este proyecto implementa un **único nodo C** en Python que funciona como **cliente y servidor TCP al mismo tiempo**.  
Ahora los mensajes se **intercambian en formato JSON**, y se realiza la serialización/deserialización de forma automática.

Cada nodo escucha por un puerto y a su vez intenta conectarse a otro nodo para saludarse mutuamente.  
El sistema también cuenta con logs persistentes, reintentos automáticos de conexión, y está todo containerizado(?) con Docker.

## Requisitos

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- **Opcional:** [Make](https://www.gnu.org/software/make/)  
  *Re contra útil para correr todo fácil 😎*

## Instalación y Uso

### 1. Levantar los nodos

```sh
make up
```

Esto levanta dos nodos: `node1_c` y `node2_c`, cada uno configurado con su `.env`.

### 2. Ver logs del nodo 1

```sh
make nodo1_log
```

### 3. Ver logs del nodo 2

```sh
make nodo2_log
```

---

## Formato de los mensajes

Los mensajes entre nodos son objetos JSON como este:

```json
{
  "node": "node1",
  "message": "Hola desde node1"
}
```

---

## Detalles técnicos

- Cada nodo:
  - Escucha conexiones entrantes (modo servidor).
  - Intenta conectarse al otro nodo (modo cliente).
  - Envia y recibe mensajes cada 5 segundos.
- Los mensajes se serializan a JSON antes de enviarse, y se deserializan al recibirse.
- Los logs se guardan en `logs/output.log` .

## Requisitos Python

Se usa una dependencia externa para manejar variables de entorno:

```txt
python-dotenv
```
