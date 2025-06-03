gcloud:
	gcloud container clusters get-credentials blockchain-cluster --zone=southamerica-east1-a --project=blockchainsd2025

fmt:
	terraform fmt

init:
	terraform init -upgrade

plan:
	terraform plan -var-file=terraform.tfvars

apply:
	terraform apply -var-file=terraform.tfvars -auto-approve

all:
	gcloud container clusters get-credentials blockchain-cluster --zone=southamerica-east1-a --project=blockchainsd2025
	terraform fmt
	terraform init
	terraform plan -var-file=terraform.tfvars
	terraform apply -var-file=terraform.tfvars -auto-approve

destroy:
	terraform destroy -var-file=terraform.tfvars -auto-approve

get_urls:
	terraform output coordinador_url

