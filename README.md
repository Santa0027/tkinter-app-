# Folder Structure Manager

A comprehensive Django web application for managing project folder structures, converted from the original Tkinter desktop application. This application provides a modern web interface for creating, managing, and deploying standardized folder structures for various project types.

## 🚀 Features

### Core Functionality
- **Client Management**: Create and manage client information with contact details
- **Project Management**: Organize projects by client with status tracking and metadata
- **Folder Structure Creation**: Design custom folder hierarchies with drag-and-drop interface
- **Predefined Templates**: Use built-in templates for Motion Graphics, Graphic Design, and more
- **Physical Folder Creation**: Generate actual directory structures on the file system
- **Import/Export**: Share folder structures via JSON files
- **ZIP Download**: Download folder structures as ZIP files with placeholder files

### Web Interface
- **Responsive Design**: Modern Bootstrap-based UI that works on all devices
- **Real-time Preview**: Live preview of folder structures as you build them
- **AJAX Operations**: Smooth, dynamic interactions without page reloads
- **User Authentication**: Secure login system with profile management
- **Dashboard**: Overview of projects, clients, and recent activity

### API Integration
- **REST API**: Complete RESTful API for mobile app integration
- **Authentication**: Token-based authentication for API access
- **Rate Limiting**: Built-in rate limiting for API endpoints
- **Documentation**: Auto-generated API documentation

### Security & Performance
- **User Isolation**: Each user can only access their own data
- **CSRF Protection**: Built-in protection against cross-site request forgery
- **SQL Injection Protection**: Parameterized queries and ORM protection
- **Caching**: Redis-based caching for improved performance
- **Logging**: Comprehensive logging for monitoring and debugging

## 🛠️ Technology Stack

### Backend
- **Django 5.2.4**: Web framework
- **Django REST Framework**: API development
- **PostgreSQL**: Primary database
- **Redis**: Caching and session storage
- **Celery**: Background task processing

### Frontend
- **Bootstrap 5.3**: CSS framework
- **jQuery**: JavaScript library
- **Font Awesome**: Icons
- **Custom CSS/JS**: Enhanced user experience

### DevOps & Deployment
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration
- **Nginx**: Reverse proxy and static file serving
- **Gunicorn**: WSGI HTTP Server
- **WhiteNoise**: Static file serving

## 📋 Prerequisites

- Python 3.12+
- Docker and Docker Compose
- PostgreSQL (for production)
- Redis (for caching)

## 🚀 Quick Start

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd folder-structure-manager
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Web Interface: http://localhost:8000
   - Admin Panel: http://localhost:8000/admin
   - API: http://localhost:8000/api/v1/

### Docker Deployment

1. **Quick deployment**
   ```bash
   ./deploy.sh development
   ```

2. **Manual Docker setup**
   ```bash
   docker-compose up --build -d
   ```

## 📁 Project Structure

```
folder-structure-manager/
├── folder_structure_manager/    # Django project settings
│   ├── settings.py             # Base settings
│   ├── settings_production.py  # Production settings
│   ├── urls.py                 # URL configuration
│   └── wsgi.py                 # WSGI configuration
├── projects/                   # Main application
│   ├── models.py              # Database models
│   ├── views.py               # Web views
│   ├── api_views.py           # API views
│   ├── serializers.py         # API serializers
│   ├── urls.py                # URL patterns
│   ├── admin.py               # Admin interface
│   └── tests.py               # Test cases
├── accounts/                   # User authentication
│   ├── views.py               # Auth views
│   ├── urls.py                # Auth URLs
│   └── tests.py               # Auth tests
├── templates/                  # HTML templates
│   ├── base.html              # Base template
│   ├── accounts/              # Auth templates
│   └── projects/              # Project templates
├── static/                     # Static files
│   ├── css/                   # Stylesheets
│   ├── js/                    # JavaScript
│   └── images/                # Images
├── media/                      # User uploads
├── docker-compose.yml          # Docker configuration
├── Dockerfile                  # Docker image
├── nginx.conf                  # Nginx configuration
├── requirements.txt            # Python dependencies
├── deploy.sh                   # Deployment script
└── README.md                   # This file
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

# Database
DATABASE_URL=postgresql://username:password@localhost:5432/folder_structure_manager

# Redis
REDIS_URL=redis://localhost:6379/0

# Email (for password reset)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Database Models

#### Client
- Name, email, phone, address
- User association for data isolation
- Project count tracking

#### Project
- Name, description, status
- Client association
- Save location configuration
- Metadata (start date, end date, budget)

#### FolderStructure
- JSON-based structure storage
- Project association
- Creation status tracking
- Predefined template linking

#### PredefinedStructure
- Template definitions
- Structure type categorization
- Public/private visibility
- User-created templates

## 🔌 API Endpoints

### Authentication
- `POST /accounts/login/` - User login
- `POST /accounts/register/` - User registration
- `POST /accounts/logout/` - User logout

### Clients
- `GET /api/v1/clients/` - List clients
- `POST /api/v1/clients/` - Create client
- `GET /api/v1/clients/{id}/` - Get client details
- `PUT /api/v1/clients/{id}/` - Update client
- `DELETE /api/v1/clients/{id}/` - Delete client

### Projects
- `GET /api/v1/projects/` - List projects
- `POST /api/v1/projects/` - Create project
- `GET /api/v1/projects/{id}/` - Get project details
- `PUT /api/v1/projects/{id}/` - Update project
- `DELETE /api/v1/projects/{id}/` - Delete project

### Folder Structures
- `GET /api/v1/projects/{id}/structures/` - List structures
- `POST /api/v1/projects/{id}/structures/` - Create structure
- `GET /api/v1/projects/{id}/structures/{id}/` - Get structure
- `PUT /api/v1/projects/{id}/structures/{id}/` - Update structure
- `DELETE /api/v1/projects/{id}/structures/{id}/` - Delete structure

### Utilities
- `GET /api/v1/predefined-structures/` - List templates
- `POST /api/v1/projects/{id}/structures/{id}/create-folders/` - Create physical folders
- `POST /api/v1/projects/{id}/import-structure/` - Import structure from JSON

## 🧪 Testing

### Run Tests
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test projects
python manage.py test accounts

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

### Test Categories
- **Model Tests**: Database model validation
- **View Tests**: Web interface functionality
- **API Tests**: REST API endpoints
- **Security Tests**: Authentication and authorization
- **Integration Tests**: End-to-end workflows

## 🚀 Deployment

### Development
```bash
./deploy.sh development
```

### Production
```bash
# Set up environment
cp .env.example .env
# Edit .env with production values

# Deploy
./deploy.sh production
```

### Manual Production Setup
```bash
# Build image
docker build -t folder-structure-manager:latest .

# Run with production settings
docker-compose -f docker-compose.yml up -d

# Run migrations
docker-compose exec web python manage.py migrate --settings=folder_structure_manager.settings_production

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput
```

## 📊 Monitoring

### Logs
```bash
# View application logs
./deploy.sh logs

# View specific service logs
docker-compose logs web
docker-compose logs db
docker-compose logs nginx
```

### Health Checks
- Application: `http://localhost:8000/api/v1/dashboard/stats/`
- Nginx: `http://localhost/health/`
- Database: Built-in PostgreSQL health checks
- Redis: Built-in Redis health checks

## 🔒 Security Features

- **Authentication**: Django's built-in authentication system
- **Authorization**: User-based data isolation
- **CSRF Protection**: Cross-site request forgery protection
- **SQL Injection**: ORM-based query protection
- **XSS Protection**: Template auto-escaping
- **Rate Limiting**: API endpoint throttling
- **HTTPS**: SSL/TLS support in production
- **Security Headers**: Comprehensive security headers via Nginx

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guide
- Write tests for new features
- Update documentation
- Use meaningful commit messages

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check this README and inline code comments
- **Issues**: Report bugs via GitHub Issues
- **Discussions**: Use GitHub Discussions for questions

## 🎯 Roadmap

### Planned Features
- [ ] Real-time collaboration on folder structures
- [ ] Version control for folder structures
- [ ] Advanced template sharing marketplace
- [ ] Mobile app for iOS and Android
- [ ] Integration with cloud storage providers (AWS S3, Google Drive, Dropbox)
- [ ] Automated folder structure validation
- [ ] Custom folder naming conventions
- [ ] Bulk operations for multiple projects
- [ ] Advanced reporting and analytics
- [ ] Plugin system for custom integrations

### Recent Updates
- ✅ Complete Django web application
- ✅ REST API implementation
- ✅ Docker containerization
- ✅ Comprehensive testing suite
- ✅ Production deployment configuration
- ✅ User authentication and authorization
- ✅ File import/export functionality

## 🙏 Acknowledgments

- Original Tkinter application developers
- Django and Django REST Framework communities
- Bootstrap and jQuery teams
- All contributors and testers

---

**Built with ❤️ using Django and modern web technologies**
