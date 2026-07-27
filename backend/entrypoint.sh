#!/bin/sh
alembic upgrade head
python -m file_catalog.main