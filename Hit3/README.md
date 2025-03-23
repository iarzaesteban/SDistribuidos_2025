# Servidor TCP en Docker

## Descripción

Este hit implementa un servidor TCP en Python, junto con un cliente TCP.  
El servidor (B) puede manejar múltiples clientes de forma simultánea, gracias al uso de threads.  
Además, si el cliente (A) se desconecta (por ejemplo, si se mata el proceso), el servidor **sigue funcionando normalmente** y puede aceptar nuevas conexiones.  
El cliente también reintenta automáticamente si la conexión se pierde.  

## Requisitos

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- **Opcional:** [Make](https://www.gnu.org/software/make/)  
  *Si podés usar Make, se simplifican los comandos. :)*

## Instalación y Uso

### Uso con Make

Si tenés Make instalado, podés correr:

1. **Levantar el servidor**  

   ```sh
   make up_server
   ```

2. **Ejecutar el cliente**  

   ```sh
   make run_client
   ```

   > ⚠️ El cliente va a reintentar conectarse automáticamente si no puede o si se corta la conexión.

3. **Ejecutar tests**  

   ```sh
   make test
   ```

---

### Uso sin Make

Si no tenés Make :(, podés usar Docker Compose directamente:

1. **Construir las imágenes**  

   ```sh
   docker-compose build
   ```

2. **Levantar el servidor**  

   ```sh
   docker-compose up server
   ```

3. **Ejecutar el cliente**  

   En otra terminal:  

   ```sh
   docker-compose run client
   ```

   O si querés ver todos los logs:

   ```sh
   docker-compose up client
   ```

4. **Ejecutar tests**  

   ```sh
   docker-compose run tests
   ```

5. **Apagar todo**  

   ```sh
   docker-compose down
   ```
