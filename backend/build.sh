#!/usr/bin/env bash
set -o errexit

# Upgrade pip, then force install setuptools globally in the venv
python -m pip install --upgrade pip
pip install setuptools wheel
pip install -r requirements.txt

# Run migrations and collectstatic
python manage.py collectstatic --no-input
python manage.py migrate