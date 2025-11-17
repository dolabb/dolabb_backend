#!/bin/bash

# Deployment script for Django backend on VPS
# Make this file executable: chmod +x deploy.sh

set -e  # Exit on error

echo "🚀 Starting deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo -e "${RED}Please do not run as root${NC}"
    exit 1
fi

# Get project directory
PROJECT_DIR=$(pwd)
echo -e "${GREEN}Project directory: $PROJECT_DIR${NC}"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo -e "${YELLOW}Activating virtual environment...${NC}"
    source venv/bin/activate
elif [ -d ".venv" ]; then
    echo -e "${YELLOW}Activating virtual environment...${NC}"
    source .venv/bin/activate
else
    echo -e "${YELLOW}No virtual environment found. Creating one...${NC}"
    python3 -m venv venv
    source venv/bin/activate
fi

# Install/Update dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn  # Add gunicorn for production

# Create necessary directories
echo -e "${YELLOW}Creating necessary directories...${NC}"
mkdir -p logs
mkdir -p media/uploads/profiles
mkdir -p staticfiles

# Set environment to production
export DJANGO_SETTINGS_MODULE=dolabb_backend.settings_production

# Collect static files
echo -e "${YELLOW}Collecting static files...${NC}"
python manage.py collectstatic --noinput

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${RED}Warning: .env file not found!${NC}"
    echo -e "${YELLOW}Please create .env file with required environment variables${NC}"
fi

echo -e "${GREEN}✅ Deployment preparation complete!${NC}"
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Make sure .env file is configured with production values"
echo "2. Start Redis: sudo systemctl start redis"
echo "3. Start Gunicorn: sudo systemctl start dolabb-backend"
echo "4. Start Daphne: sudo systemctl start dolabb-daphne"
echo "5. Reload Nginx: sudo systemctl reload nginx"

