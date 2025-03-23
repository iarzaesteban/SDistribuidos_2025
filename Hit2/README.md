# Servidor TCP en Docker

## Descripción

Este hit implementa un servidor TCP en Python, junto con un cliente TCP.  
El servidor (B) espera el saludo del cliente (A) y le responde.  
El cliente intenta conectarse a B y, si no puede o se corta la conexión, **reintenta automáticamente** cada 5 segundos hasta lograrlo.  
Una vez conectado, envía saludos de forma continua cada 5 segundos.  

## Requisitos

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- **Opcional:** [Make](https://www.gnu.org/software/make/)  
  *Si podés usar Make, se simplifican los comandos de ejecución. :)*

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

   > ⚠️ Si el servidor no está listo o se cae, el cliente va a reintentar automáticamente hasta poder conectarse otra vez.

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

   O, si querés ver todo el log de ejecución:  

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
