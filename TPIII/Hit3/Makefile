PROJECT_ID=alert-parsec-456902-u3
CLUSTER_NAME=hit3-sobel-cluster
REGION=us-central1

# Terraform infra
infra:
	cd infra && terraform apply -auto-approve

# Obtener credenciales del cluster
kubeconfig:
	gcloud container clusters get-credentials $(CLUSTER_NAME) --region $(REGION) --project $(PROJECT_ID)

# Aplicar todos los deployments y services
.PHONY: deploy

deploy:
	cd infra && terraform init && terraform apply -auto-approve
	cd infra/workers && terraform init && terraform apply -auto-approve
	gcloud container clusters get-credentials hit3-sobel-cluster --zone=us-central1-c

deploy-infra:
	cd infra && terraform init && terraform apply -auto-approve

deploy-workers:
	cd infra/workers && terraform init && terraform apply -auto-approve

# Reiniciar todo
restart:
	kubectl rollout restart deployment backend
	kubectl rollout restart deployment frontend
	kubectl rollout restart deployment worker

# Borrar todo
destroy:
	cd infra && terraform destroy -auto-approve
	cd infra/workers && terraform destroy -auto-approve

# Todo junto
all: infra kubeconfig deploy


.PHONY: deploy-all deploy-k8s deploy-services deploy-apps deploy-workers

deploy-all: deploy-k8s deploy-services deploy-apps deploy-workers

deploy-k8s:
	@echo "🚀 Desplegando infraestructura Kubernetes (Terraform)..."
	bash deploy/pipeline_1_k8s_infra.sh

deploy-services:
	@echo "📡 Desplegando servicios base (Redis, RabbitMQ)..."
	bash deploy/pipeline_1.1_services.sh

deploy-apps:
	@echo "🖥️ Desplegando aplicaciones..."
	bash deploy/pipeline_1.2_apps.sh

deploy-workers:
	@echo "🧠 Desplegando máquinas virtuales (workers)..."
	bash deploy/pipeline_2_workers.sh


