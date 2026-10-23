up:               ## start targets + network
	docker compose up -d --build --wait

down:
	docker compose down -v

reset-targets:    ## fresh DVWA + db state
	docker compose up -d --wait --force-recreate --renew-anon-volumes

eval:
	python -m eval.run_eval

build:
	docker compose build

executor:
	SCENARIO=$(S) docker compose up -d --force-recreate --no-deps executor

scenario:
	SCENARIO=$(S) docker compose up -d --force-recreate --no-deps target