down:
	docker compose down -v

executor:
	SCENARIO=$(S) docker compose up -d --force-recreate --build --no-deps executor

scenario:
	SCENARIO=$(S) docker compose up -d --force-recreate --build --no-deps target