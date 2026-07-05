.PHONY: api-test api-migrate seed compose-up compose-down

api-test:
	cd apps/api && pytest

api-migrate:
	cd apps/api && alembic upgrade head

seed:
	cd apps/api && python -m app.db.seed

compose-up:
	docker compose up --build

compose-down:
	docker compose down

