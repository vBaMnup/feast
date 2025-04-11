#!/bin/sh

alembic upgrade head

exec python -m src.main