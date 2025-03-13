.PHONY: up_server run_client test build up down clean

up_server:
	docker-compose up server

run_client:
	docker-compose run --rm client

test:
	docker-compose run --rm tests

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

clean:
	docker-compose down -v
	docker system prune -f
