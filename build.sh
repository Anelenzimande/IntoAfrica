#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Make sure this line is present and executing without errors
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate