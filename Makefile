install-local:
	/opt/homebrew/Cellar/poetry/1.8.2/libexec/bin/python -m pip install .

check: install-local
	/opt/homebrew/Cellar/poetry/1.8.2/libexec/bin/poetry vet check

init: install-local
	/opt/homebrew/Cellar/poetry/1.8.2/libexec/bin/poetry vet init

lock: install-local
	/opt/homebrew/Cellar/poetry/1.8.2/libexec/bin/poetry vet lock

list: install-local
	/opt/homebrew/Cellar/poetry/1.8.2/libexec/bin/poetry list

schema:
	python -m vet.scripts.generate_schemas

lint:
	ruff check . --fix

format:
	ruff format .

test:
	pytest vet

type:
	pyright

all: schema format lint type test
