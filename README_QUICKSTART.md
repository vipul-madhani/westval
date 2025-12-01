# Westval - Quick Start Guide

## What Has Been Implemented

### ✅ Complete Backend (Flask/Python)
- User authentication with JWT
- Validation project management (CRUD)
- Document management with version control
- Electronic signatures (21 CFR Part 11 compliant)
- Requirements management
- Test case management and execution
- Risk assessment
- Comprehensive audit trails
- AI-powered document generation
- Jira and Azure DevOps integration

### ✅ Complete Frontend (React/TypeScript)
- Login page with authentication
- Dashboard with statistics
- Validation projects listing and creation
- Document management interface
- Requirements tracking
- Test management with statistics
- Compliance dashboard
- Material-UI components throughout

### ✅ Database
- PostgreSQL schema with migrations
- All models implemented
- Audit trail tables
- Electronic signature tracking

### ✅ DevOps
- Docker Compose setup
- Dockerfile for backend and frontend
- Environment configuration

## How to Run

### Option 1: Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/vipul-madhani/westval.git
cd westval

# Create environment file
cp .env.example .env
# Edit .env with your configuration

# Start all services
docker-compose up -d

# Initialize database
docker-compose exec backend flask init-db

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:5000
# Login: admin@westval.com / Admin@Westval2025!
```

### Option 2: Local Development

#### Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp ../.env.example .env
# Edit .env with your database and Redis connection strings

# Initialize database
flask init-db

# Run backend
python run.py
```

#### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Create .env file
echo "REACT_APP_API_URL=http://localhost:5000/api" > .env

# Run frontend
npm run dev
```

### Prerequisites

**For Docker:**
- Docker Engine 20.x+
- Docker Compose 2.x+

**For Local Development:**
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+

## Default Login Credentials

- **Email:** admin@westval.com
- **Password:** Admin@Westval2025!

## Key Features Demonstrated

1. **Validation Project Management**
   - Create projects with different validation types (CSV, Lab, Cleaning, Process)
   - Multiple methodologies (Waterfall, Agile, CSA)
   - GAMP categorization
   - Risk-based approach

2. **Document Control**
   - Version control
   - Electronic signatures
   - Audit trails
   - Status workflows

3. **Requirements Traceability**
   - Link requirements to test cases
   - Traceability matrix
   - Priority and criticality tracking

4. **Test Management**
   - Test case creation and execution
   - Pass/fail tracking
   - Evidence attachment
   - Statistics and reporting

5. **AI Capabilities**
   - Protocol generation
   - Test case generation from requirements
   - Document review and gap analysis
   - Risk assessment

6. **Integrations**
   - Jira bidirectional sync
   - Azure DevOps integration
   - RESTful API for custom integrations

7. **Compliance**
   - 21 CFR Part 11 electronic signatures
   - Complete audit trails (WHO, WHAT, WHEN, WHY)
   - Data integrity (ALCOA+)
   - Version control at all levels

## API Documentation

Once running, access interactive API documentation at:
- Swagger UI: http://localhost:5000/api/docs (to be added)

## Testing the Application

### Create a Validation Project

1. Login with default credentials
2. Navigate to "Projects" from dashboard
3. Click "New Project"
4. Fill in:
   - Title: "ERP System Validation"
   - Type: "Computer System Validation"
   - Methodology: "CSA"
   - GAMP Category: "5"
   - Risk Level: "High"
5. Click "Create"

### Create a Document

1. Navigate to "Documents"
2. Click "New Document"
3. Fill in document details
4. Document will be created with version 1.0

### Use AI Features

AI features require OpenAI API key in .env:

```bash
# Generate protocol
curl -X POST http://localhost:5000/api/ai/generate-protocol \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "template_type": "IQ",
    "project_data": {
      "title": "System Validation",
      "validation_type": "CSV"
    }
  }'
```

## What's Working

✅ User authentication and authorization
✅ Validation project CRUD operations
✅ Document management with versioning
✅ Electronic signature workflow
✅ Requirements management
✅ Test case management
✅ Audit trail generation
✅ Statistics and dashboards
✅ AI-powered features (with API key)
✅ Jira integration (with credentials)
✅ Azure DevOps integration (with credentials)

## Next Steps for Production

1. **Security Hardening**
   - Enable HTTPS/TLS
   - Implement rate limiting
   - Add CSRF protection
   - Configure firewall rules

2. **Performance Optimization**
   - Add Redis caching
   - Database query optimization
   - CDN for static assets
   - Load balancing

3. **Additional Features**
   - Advanced reporting and analytics
   - Mobile app (React Native)
   - Workflow automation
   - Custom template builder
   - Advanced search

4. **Testing**
   - Unit tests
   - Integration tests
   - End-to-end tests
   - Load testing

5. **Deployment**
   - Kubernetes deployment
   - CI/CD pipeline
   - Monitoring and logging
   - Backup and disaster recovery

## Troubleshooting

### Database Connection Error
```bash
# Check PostgreSQL is running
docker-compose ps

# View logs
docker-compose logs postgres
```

### Frontend Not Loading
```bash
# Check if backend is running
curl http://localhost:5000/health

# Check frontend logs
docker-compose logs frontend
```

### Authentication Issues
```bash
# Reinitialize database
docker-compose exec backend flask init-db
```

## Support

For issues or questions:
- GitHub Issues: https://github.com/vipul-madhani/westval/issues
- Documentation: See `/docs` folder

## License

Proprietary - All rights reserved