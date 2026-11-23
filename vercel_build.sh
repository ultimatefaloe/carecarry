#!/bin/bash
set -e

echo "Installing Python packages..."
python3 -m pip install --break-system-packages -r requirements.txt

echo "Installing Tailwind dependencies..."
python3 manage.py tailwind install

echo "Building Tailwind CSS..."
python3 manage.py tailwind build

echo "Collecting Django static files..."
python3 manage.py collectstatic --noinput

echo "Build process completed."