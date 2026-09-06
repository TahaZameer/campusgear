#!/bin/sh
set -e

echo "Running Alembic migrations..."
alembic upgrade head

echo "Running Seed Data..."
python seed.py

echo "Starting application..."
exec "$@"