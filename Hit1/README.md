# Servidor TCP en Docker

## Descripción

Este proyecto implementa un servidor TCP en Python, junto con un cliente TCP.  
El servidor (B) espera el saludo del cliente (A) y le responde, mientras que el cliente se conecta a B y envía un saludo.  

## Requisitos

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- **Opcional:** [Make](https://www.gnu.org/software/make/)  
  *Si podes usar Make, se simplifican los comandos de ejecución. :)*

## Instalación y Uso

### Uso con Make

Si tenes Make instalado, podes utilizar los siguientes comandos:

1. **Levantar el servidor**  

   ```sh
   make up_server
   ```

2. **Ejecutar el cliente**  

   ```sh
   make run_client
   ```

3. **Ejecutar tests**  

   ```sh
   make test
   ```

---

### Uso sin Make

Si no tenes Make :(, podes ejecutar los comandos de Docker Compose directamente:

1. **Construir las imágenes**  
   Ejecuta el siguiente comando en la raíz del proyecto:  

   ```sh
   docker-compose build
   ```

2. **Levantar el servidor**  
   Levanta el contenedor del servidor:  

   ```sh
   docker-compose up server
   ```

3. **Ejecutar el cliente**  
   En una terminal aparte (después de haber levantado el servidor), ejecutar:  

   ```sh
   docker-compose run client
   ```

   O, si queres ver el log de la ejecución:  

   ```sh
   docker-compose up client
   ```

4. **Ejecutar tests**  

   ```sh
   docker-compose run tests
   ```

5. **Apagar los contenedores**  
   Cuando finalices, remove los contenedores con:  

   ```sh
   docker-compose down
   ```
