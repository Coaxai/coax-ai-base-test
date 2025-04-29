#!/bin/bash

set -o errexit  # Exit on error
set -o nounset  # Treat unset variables as an error
set -o pipefail # Catch errors in piped commands

echo "🔹 Installing dependencies..."
pip install --no-cache-dir -r requirements.txt

echo "🔹 Running database migrations..."
python manage.py makemigrations
python manage.py migrate
# python manage.py loaddata db_backup.json
python manage.py collectstatic --noinput


echo "✅ Build completed successfully!"