.PHONY: up down logs ps health build test-api

up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f

ps:
	docker compose ps

health:
	curl -s http://localhost:8000/health | python -m json.tool

build:
	docker compose build

test-api:
	curl -f http://localhost:8000/health
