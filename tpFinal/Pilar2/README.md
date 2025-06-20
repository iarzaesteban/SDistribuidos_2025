# Levantar el entorno local

## 1- Ingresar al directorio Pilar2
```bash
cd Pilar2
```
##  2- Levantamos los contenedores:
```bash
docker-compose up
```

## Correr un cliente
## 1- Ingresar al directorio client desde Pilar2
```bash
cd client
```
## 2- Ingresar al entorno vitual
```bash
source venv/bin/activate
```
## 3- Ejecutar el script del cliente para generar una nueva tarea
```bash
python3 client_keys_prefix.py
```

## Levantar el frontend localmmente
## 1- Ingresar al directorio frontend desde Pilar2
```bash
cd frontend
```
## 2- Instalar las dependencias necesarias
```bash
npm install
```
## 3- Levantar el frontend
```bash
npm run dev
```
