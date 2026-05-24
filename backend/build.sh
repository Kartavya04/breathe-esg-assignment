#!/usr/bin/env bash
set -o errexit

# Yeh line purani environment ko hata degi
rm -rf .venv

# Naya environment aur dependencies
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate