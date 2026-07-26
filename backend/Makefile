C ?= 3

all: run

run:
	python -m file_catalog.main

generate-files:
	python scripts/generate_files.py --count=${C}

lint:
	ruff format
	ruff check --fix
