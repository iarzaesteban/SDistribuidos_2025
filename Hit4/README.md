# Nodo C - Cliente y Servidor TCP en Docker

## Descripción

Este proyecto implementa un **único nodo C** en Python que actúa como **cliente y servidor TCP al mismo tiempo**.  
Al iniciar cada nodo C, se le indica por variables de entorno:

- Qué IP y puerto debe **escuchar** (modo servidor).
- Qué IP y puerto debe **contactar** (modo cliente).

De esta forma, si levantás dos nodos (por ejemplo, `node1` y `node2`), cada uno puede **saludarse mutuamente**.

## Requisitos

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- **Opcional:** [Make](https://www.gnu.org/software/make/)  
  *Te simplifica bastante levantar todo y ver logs 😉*

## Instalación y Uso

### 1. Levantar los nodos

```sh
make up
```

Esto levanta dos nodos: `node1_c` y `node2_c`, cada uno con su configuración de IP y puerto.

### 2. Ver los logs del nodo 1

```sh
make nodo1_log
```

### 3. Ver los logs del nodo 2

```sh
make nodo2_log
```

---

## Detalles técnicos

- Cada nodo escucha conexiones entrantes (modo servidor).
- Al mismo tiempo, cada nodo intenta conectarse a su par (modo cliente).
- Los mensajes se intercambian cada 5 segundos.
- Si un nodo no puede conectarse, reintenta cada 5 segundos hasta lograrlo.
- Todos los logs se guardan en archivos (`logs/output.log`) por nodo, con nombre, fecha y módulo del mensaje.

## Requisitos Python internos

El único paquete externo que usamos es:

```txt
python-dotenv
```

Para escalar, Copiá y adaptá los `.env` y agregá entradas en `docker-compose.yml`.
