# Servidor TCP en Docker

## Descripción

Este proyecto implementa un sistema distribuido basado en contenedores Docker que permite la comunicación entre un nodo central (Nodo D) y múltiples nodos cliente (Nodos C). El Nodo D gestiona las conexiones de los Nodos C y distribuye información a todos los nodos conectados para facilitar la comunicación entre ellos.

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
