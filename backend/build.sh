#!/usr/bin/env bash
set -o errexit

# Force upgrade pip and setuptools first
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Run migrations and collectstatic
python manage.py collectstatic --no-input
python manage.py migrate