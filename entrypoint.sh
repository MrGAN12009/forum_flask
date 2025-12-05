#!/bin/bash
set -e

echo "Waiting for PostgreSQL..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "PostgreSQL started"

echo "Running database migrations..."
flask db upgrade

echo "Creating upload directories..."
mkdir -p /app/uploads/avatars
mkdir -p /app/uploads/posts
mkdir -p /app/uploads/chat
chmod -R 755 /app/uploads

echo "Starting application..."
exec gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 "run:app"

