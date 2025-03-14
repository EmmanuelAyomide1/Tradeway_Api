#!/bin/bash
echo "Installing dependencies..."
python3.12 -m pip install --upgrade pip
python3.12 -m pip install -r requirements/staging.txt

echo "Running database migrations..."
python3.12 manage.py makemigrations
python3.12 manage.py migrate

echo "Collecting static files..."
python3.12 manage.py collectstatic --noinput --clear

echo "Build completed!"