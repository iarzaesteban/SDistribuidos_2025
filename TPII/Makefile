SERVER_TASKS_IMAGE = tasks_image


# Comando para construir la imagen del servidor
build_server_image:
	docker-compose build

# Construimos la imagen del servidor de tareas
build_server_tasks_image:
	docker build -t $(SERVER_TASKS_IMAGE) ./server/task_service

# Levantamos el servidor
up_server:
	docker-compose up

# Detenemos el servidor
down_server:
	docker-compose down

# Reiniciamos el servidor
restart_server:
	docker-compose down && docker-compose up


# Correr tests dentro del contenedor Docker
test_docker:
	docker-compose run --rm fastapi_app python -m pytest tests/

# Testea el servidor principal (FastAPI)
test_main:
	docker-compose run --rm fastapi_app python -m pytest tests/test_main.py

# Testea el microservicio de tareas
test_tasks:
	docker-compose run --rm fastapi_app python -m pytest tests/test_task_service.py
