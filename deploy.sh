#!/bin/bash

# Deployment script for Folder Structure Manager
# Usage: ./deploy.sh [environment]
# Environment: development, staging, production

set -e  # Exit on any error

ENVIRONMENT=${1:-development}
PROJECT_NAME="folder-structure-manager"

echo "🚀 Starting deployment for $ENVIRONMENT environment..."

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Function to deploy to development
deploy_development() {
    print_status "Deploying to development environment..."
    
    # Copy environment file
    if [ ! -f .env ]; then
        print_warning ".env file not found. Creating from .env.example..."
        cp .env.example .env
        print_warning "Please edit .env file with your configuration before running again."
        exit 1
    fi
    
    # Build and start services
    docker-compose -f docker-compose.yml up --build -d
    
    # Wait for services to be ready
    print_status "Waiting for services to be ready..."
    sleep 10
    
    # Run migrations
    print_status "Running database migrations..."
    docker-compose exec web python manage.py migrate
    
    # Create superuser if it doesn't exist
    print_status "Creating superuser (if not exists)..."
    docker-compose exec web python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
"
    
    # Load initial data
    print_status "Loading initial data..."
    docker-compose exec web python manage.py shell -c "
from projects.models import PredefinedStructure
from django.contrib.auth.models import User

admin_user = User.objects.get(username='admin')

# Motion Graphics structure
if not PredefinedStructure.objects.filter(name='Motion Graphics Default').exists():
    motion_graphics_structure = [
        {'name': 'audio', 'children': []},
        {'name': 'out_images', 'children': [
            {'name': 'afterEffects', 'children': []},
            {'name': 'photoshop', 'children': []},
            {'name': 'premierePro', 'children': []}
        ]},
        {'name': 'out_movies', 'children': [
            {'name': 'afterEffects', 'children': []},
            {'name': 'photoshop', 'children': []},
            {'name': 'premierePro', 'children': []}
        ]},
        {'name': 'reference', 'children': [
            {'name': 'images', 'children': []},
            {'name': 'videos', 'children': []},
            {'name': 'template_files', 'children': []}
        ]},
        {'name': 'work_file', 'children': [
            {'name': 'afterEffects', 'children': []},
            {'name': 'photoshop', 'children': []},
            {'name': 'premierePro', 'children': []}
        ]},
        {'name': 'client_Out', 'children': []},
        {'name': 'script', 'children': []}
    ]
    
    PredefinedStructure.objects.create(
        name='Motion Graphics Default',
        structure_type='motion_graphics',
        structure_data=motion_graphics_structure,
        description='Default structure for motion graphics projects',
        created_by=admin_user,
        is_public=True
    )
    print('Motion Graphics structure created')

# Graphic Design structure
if not PredefinedStructure.objects.filter(name='Graphic Design Default').exists():
    graphic_design_structure = [
        {'name': 'out_images', 'children': [
            {'name': 'photoshop', 'children': []},
            {'name': 'Illustrator', 'children': []},
            {'name': 'CorelDraw', 'children': []}
        ]},
        {'name': 'reference', 'children': [
            {'name': 'images', 'children': []},
            {'name': 'template_files', 'children': []}
        ]},
        {'name': 'work_file', 'children': [
            {'name': 'photoshop', 'children': []},
            {'name': 'Illustrator', 'children': []},
            {'name': 'CorelDraw', 'children': []}
        ]},
        {'name': 'client_Out', 'children': []}
    ]
    
    PredefinedStructure.objects.create(
        name='Graphic Design Default',
        structure_type='graphic_design',
        structure_data=graphic_design_structure,
        description='Default structure for graphic design projects',
        created_by=admin_user,
        is_public=True
    )
    print('Graphic Design structure created')
"
    
    print_status "Development deployment completed!"
    print_status "Application is running at: http://localhost:8000"
    print_status "Admin panel: http://localhost:8000/admin"
    print_status "API documentation: http://localhost:8000/api/v1/"
    print_status "Superuser credentials: admin/admin123"
}

# Function to deploy to production
deploy_production() {
    print_status "Deploying to production environment..."
    
    # Check for required environment variables
    if [ ! -f .env ]; then
        print_error ".env file is required for production deployment"
        exit 1
    fi
    
    # Build production image
    print_status "Building production Docker image..."
    docker build -t $PROJECT_NAME:latest .
    
    # Deploy with production compose file
    print_status "Starting production services..."
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
    
    # Run migrations
    print_status "Running database migrations..."
    docker-compose exec web python manage.py migrate --settings=folder_structure_manager.settings_production
    
    # Collect static files
    print_status "Collecting static files..."
    docker-compose exec web python manage.py collectstatic --noinput --settings=folder_structure_manager.settings_production
    
    print_status "Production deployment completed!"
}

# Function to show logs
show_logs() {
    print_status "Showing application logs..."
    docker-compose logs -f web
}

# Function to stop services
stop_services() {
    print_status "Stopping services..."
    docker-compose down
}

# Function to restart services
restart_services() {
    print_status "Restarting services..."
    docker-compose restart
}

# Main deployment logic
case $ENVIRONMENT in
    development|dev)
        deploy_development
        ;;
    production|prod)
        deploy_production
        ;;
    logs)
        show_logs
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    *)
        echo "Usage: $0 {development|production|logs|stop|restart}"
        echo ""
        echo "Commands:"
        echo "  development  - Deploy to development environment"
        echo "  production   - Deploy to production environment"
        echo "  logs         - Show application logs"
        echo "  stop         - Stop all services"
        echo "  restart      - Restart all services"
        exit 1
        ;;
esac
