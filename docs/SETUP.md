# Westval - Setup and Installation Guide

## Prerequisites

### System Requirements
- **Operating System**: Linux (Ubuntu 20.04+), macOS, or Windows 10/11
- **Memory**: Minimum 8GB RAM (16GB recommended)
- **Storage**: 20GB available disk space
- **Processor**: Multi-core processor (4+ cores recommended)

### Software Requirements
- **Node.js**: v18.x or higher
- **Python**: 3.11 or higher
- **PostgreSQL**: 15.x or higher
- **Redis**: 7.x or higher
- **Docker**: 24.x or higher (optional, for containerized deployment)
- **Git**: Latest version

## Local Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/vipul-madhani/westval.git
cd westval
```

### 2. Backend Setup

#### Install Python Dependencies

```bash
cd backend
python -m venv venv

# On Linux/Mac
source venv/bin/activate

# On Windows
venv\Scripts\activate

pip install -r requirements.txt
```

#### Configure Environment Variables

Create a `.env` file in the `backend` directory:

```env
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/westval
DATABASE_POOL_SIZE=10

# Redis
REDIS_URL=redis://localhost:6379/0

# Application
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# AI/ML Services
OPENAI_API_KEY=your-openai-api-key
AI_MODEL=gpt-4

# Authentication
JWT_SECRET_KEY=your-jwt-secret
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=604800

# Email (for notifications)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@example.com
SMTP_PASSWORD=your-password

# Integrations
JIRA_URL=https://your-domain.atlassian.net
JIRA_API_TOKEN=your-jira-token
JIRA_EMAIL=your-email@example.com

AZURE_DEVOPS_ORGANIZATION=your-org
AZURE_DEVOPS_PAT=your-personal-access-token

# Storage
S3_BUCKET=westval-documents
S3_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
```

#### Initialize Database

```bash
# Create database
createdb westval

# Run migrations
flask db upgrade

# Seed initial data (optional)
python seed_data.py
```

#### Start Backend Server

```bash
flask run --port 5000
```

### 3. Frontend Setup

#### Install Node Dependencies

```bash
cd ../frontend
npm install
```

#### Configure Environment Variables

Create a `.env` file in the `frontend` directory:

```env
REACT_APP_API_URL=http://localhost:5000/api
REACT_APP_WS_URL=ws://localhost:5000/ws
REACT_APP_ENVIRONMENT=development
REACT_APP_VERSION=1.0.0
```

#### Start Frontend Development Server

```bash
npm start
```

The application will be available at `http://localhost:3000`

### 4. Redis Setup

```bash
# On Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis

# On macOS (using Homebrew)
brew install redis
brew services start redis

# On Windows
# Download and install from: https://github.com/microsoftarchive/redis/releases
```

### 5. PostgreSQL Setup

```bash
# On Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql

# On macOS (using Homebrew)
brew install postgresql
brew services start postgresql

# Create database and user
sudo -u postgres psql
CREATE DATABASE westval;
CREATE USER westval_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE westval TO westval_user;
\q
```

## Docker Setup (Recommended for Production)

### Using Docker Compose

```bash
# From project root
docker-compose up -d
```

This will start:
- Backend API (port 5000)
- Frontend (port 3000)
- PostgreSQL (port 5432)
- Redis (port 6379)
- AI Services (port 8000)

### Individual Container Setup

```bash
# Build images
docker build -t westval-backend ./backend
docker build -t westval-frontend ./frontend

# Run containers
docker run -d -p 5000:5000 --name westval-api westval-backend
docker run -d -p 3000:3000 --name westval-web westval-frontend
```

## Testing

### Backend Tests

```bash
cd backend
pytest tests/ --cov=app --cov-report=html
```

### Frontend Tests

```bash
cd frontend
npm test
npm run test:coverage
```

### End-to-End Tests

```bash
cd tests/e2e
npm install
npm run test:e2e
```

## Database Migrations

### Create New Migration

```bash
cd backend
flask db migrate -m "Description of changes"
flask db upgrade
```

### Rollback Migration

```bash
flask db downgrade
```

## Production Deployment

### Environment Preparation

1. Set `FLASK_ENV=production` and `DEBUG=False`
2. Use strong secret keys
3. Configure SSL/TLS certificates
4. Set up database backups
5. Configure monitoring and logging

### Deployment Options

#### Option 1: Cloud Platform (AWS/Azure/GCP)

```bash
# Example: AWS Elastic Beanstalk
eb init westval --platform python-3.11
eb create westval-prod --database
eb deploy
```

#### Option 2: Kubernetes

```bash
kubectl apply -f deployment/kubernetes/
```

#### Option 3: Traditional Server

```bash
# Use gunicorn for production
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"

# Nginx configuration
sudo cp deployment/nginx/westval.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/westval.conf /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Initial Admin Setup

### Create Admin User

```bash
cd backend
python manage.py create-admin
```

Or via API:

```bash
curl -X POST http://localhost:5000/api/auth/setup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "SecurePassword123!",
    "first_name": "Admin",
    "last_name": "User"
  }'
```

## Configuration

### Application Settings

Edit `backend/config.py` for:
- Database connection pooling
- Session timeout
- File upload limits
- API rate limiting
- CORS settings

### Feature Flags

Enable/disable features in `backend/app/config/features.json`:

```json
{
  "ai_document_generation": true,
  "jira_integration": true,
  "advanced_analytics": true,
  "mobile_app": false
}
```

## Troubleshooting

### Common Issues

#### Database Connection Error
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Verify connection
psql -U westval_user -d westval -h localhost
```

#### Redis Connection Error
```bash
# Check Redis is running
redis-cli ping
# Should return: PONG
```

#### Port Already in Use
```bash
# Find and kill process using port 5000
lsof -i :5000
kill -9 <PID>
```

#### Frontend Build Errors
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

## Documentation

- **API Documentation**: http://localhost:5000/api/docs
- **User Guide**: `/docs/USER_GUIDE.md`
- **Developer Guide**: `/docs/DEVELOPER_GUIDE.md`
- **Compliance Guide**: `/docs/COMPLIANCE_GUIDE.md`

## Support

For issues and questions:
- GitHub Issues: https://github.com/vipul-madhani/westval/issues
- Email: support@westval.com
- Documentation: https://docs.westval.com

## License

Proprietary - All rights reserved