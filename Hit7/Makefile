.PHONY: build_node_d build_node_c up_node_d up_node_c down logs clean

build_node_d:
	docker-compose -f docker-compose-d.yml build

build_node_c:
	docker-compose -f docker-compose-c.yml build

up_node_d:
	docker-compose -f docker-compose-d.yml up

ifeq ($(OS),Windows_NT)
up_node_c_command = powershell -Command "$$NODEName = Read-Host 'Ingrese el nombre del nodo C'; Write-Host ('Levantando nodo C con nombre ' + $$NODEName); docker run --name $$NODEName --network hit7_network -e NODE_NAME=$$NODEName -e D_HOST=node_d -e D_PORT=4001 -v ./logs/:/app/logs hit7-node_c"
else
up_node_c_command = read -p "Ingrese el nombre del nodo C: " NODE_NAME; \
		echo "Levantando nodo C con nombre $$NODE_NAME..."; \
		docker run --name $$NODE_NAME --network hit7_network -e NODE_NAME=$$NODE_NAME -e D_HOST=node_d -e D_PORT=4001 -v ./logs/:/app/logs hit7-node_c
endif

up_node_c:
	@$(up_node_c_command)

down:
	docker-compose -f docker-compose-d.yml down
	docker-compose -f docker-compose-c.yml down

logs:
	docker-compose -f docker-compose-d.yml logs -f

clean:
	docker-compose -f docker-compose-d.yml down -v
	docker-compose -f docker-compose-c.yml down -v
	docker system prune -f
