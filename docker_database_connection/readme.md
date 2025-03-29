## Este proyecto configura un entorno con PostgreSQL ejecutándose en un contenedor y un cliente para poder conectarse, ejecutar consultas, ver las tablas y manipular datos.

### Posicionarnos en el directorio correcto

```sh
cd docker_database_connection
```

### Levantar los contenedores

```sh
docker-compose up --build -d
```

### Verificar que los contenedores están corriendo

```sh
docker ps
```

### Acceder al contenedor cliente

```sh
docker exec -it postgres_client bash
```

### Conectarse a la base de datos desde el cliente

```sh
psql -h db -U "$POSTGRES_USER" -d "$POSTGRES_DB"
```

### Verificar las tablas

```sh
\dt
```

### Consultar los datos en la tabla users

```sh
SELECT * FROM users;
```
