#!/bin/bash
# Quick deployment script for GoDaddy VPS
# Run this on your server after uploading code

set -e

echo "🚀 Starting deployment..."

# Project directory
PROJECT_DIR="/home/vps_YAPVeT/dolabb_backend"
cd $PROJECT_DIR

# Activate virtual environment
source venv/bin/activate

# Install/Update dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p media/uploads/profiles
mkdir -p staticfiles

# Collect static files
echo "📦 Collecting static files..."
export DJANGO_SETTINGS_MODULE=dolabb_backend.settings_production
python manage.py collectstatic --noinput

# Set permissions
echo "🔐 Setting permissions..."
chown -R vps_YAPVeT:vps_YAPVeT $PROJECT_DIR

# Restart services
echo "🔄 Restarting services..."
systemctl daemon-reload
systemctl restart dolabb-backend
systemctl restart dolabb-daphne
systemctl reload nginx

echo "✅ Deployment complete!"
echo "🌐 Your API is available at: http://68.178.161.175/api/"


