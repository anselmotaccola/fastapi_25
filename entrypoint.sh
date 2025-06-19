#!/bin/sh

# Executa as migraççoes do banco de dados
poetry run alembic upgrade head

# Inicia o aplicaão
poetry run uvicorn --host 0.0.0.0 --port 8000 fast_zero.app:app