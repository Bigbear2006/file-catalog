C ?= 3

up:
	docker-compose up --build -d

down:
	docker-compose down

generate-files:
	docker-compose exec backend python scripts/generate_files.py --count=${C}
