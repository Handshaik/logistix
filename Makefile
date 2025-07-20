.PHONY: up down build terraform-init terraform-apply test

up:
	docker-compose up --build

down:
	docker-compose down

build:
	docker-compose build

terraform-init:
	cd infra && terraform init

terraform-apply:
	cd infra && terraform apply -auto-approve

test:
	curl -X POST http://localhost:8000/assign \
	  -H "Content-Type: application/json" \
	  -d '{"driver_ids":["driver_1","driver_2"],"max_per_driver":2}'