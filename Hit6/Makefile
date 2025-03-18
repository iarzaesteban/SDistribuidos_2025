.PHONY: build up down logs clean up_node_d up_nodo_c

build_node_d:
	docker-compose -f docker-compose-d.yml build

build_node_c:
	docker-compose -f docker-compose-c.yml build

up_node_d:
	docker-compose -f docker-compose-d.yml up

up_node_c:
	@read -p "Ingrese el nombre del nodo C: " NODE_NAME; \
	echo "Levantando nodo C con nombre $$NODE_NAME..."; \
	docker run --name $$NODE_NAME \
		--network hit6_network \
		-e NODE_NAME=$$NODE_NAME \
		-e D_HOST=node_d \
		-e D_PORT=4000 \
		-v ./logs/:/app/logs \
		hit6-node_c

down:
	docker-compose -f docker-compose-d.yml down
	docker-compose -f docker-compose-c.yml down

logs:
	docker-compose -f docker-compose-d.yml logs -f

clean:
	docker-compose -f docker-compose-d.yml down -v
	docker-compose -f docker-compose-c.yml down -v
	docker system prune -f
