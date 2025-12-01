# Westval Setup Guide - MySQL & Active Directory Integration

## Quick Start with MySQL

### 1. Prerequisites
- Docker & Docker Compose
- Access to your Active Directory (optional)
- MySQL client (optional, for testing)

### 2. Initial Setup

```bash
# Clone repository
git clone https://github.com/vipul-madhani/westval.git
cd westval

# Copy environment file
cp .env.example .env

# Edit .env file with your settings
nano .env  # or use any text editor
```

### 3. Configure Database (MySQL)

In `.env` file:

```bash
# Database Configuration
DB_TYPE=mysql
DB_HOST=mysql
DB_PORT=3306
DB_NAME=westval
DB_USER=westval_user
DB_PASSWORD=YOUR_SECURE_PASSWORD_HERE  # Change this!
```

### 4. Configure Active Directory (If using)

In `.env` file:

```bash
# Enable AD Authentication
AUTH_TYPE=ad
LDAP_ENABLED=true

# Your AD Settings
AD_DOMAIN=YOURCOMPANY           # e.g., ACME
AD_SERVER=ad.yourcompany.com    # Your AD server
AD_SEARCH_BASE=DC=yourcompany,DC=com

# Service Account for LDAP Queries (recommended)
LDAP_BIND_USER=CN=WestvalService,OU=ServiceAccounts,DC=yourcompany,DC=com
LDAP_BIND_PASSWORD=service_account_password
```

#### Example for common AD setup:

```bash
# If your domain is "example.com"
AD_DOMAIN=EXAMPLE
AD_SERVER=dc01.example.com
AD_SEARCH_BASE=DC=example,DC=com

# Service account
LDAP_BIND_USER=CN=svc_westval,OU=Service Accounts,DC=example,DC=com
LDAP_BIND_PASSWORD=SecurePass123!
```

### 5. Start Services

```bash
# Start all services
docker-compose up -d

# Check if services are running
docker-compose ps

# View logs
docker-compose logs -f backend
```

### 6. Initialize Database

```bash
# Create tables and default data
docker-compose exec backend flask init-db

# Load demo data (optional)
docker-compose exec backend flask init-demo
```

### 7. Access Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000

**Default Admin Login** (if not using AD):
- Email: `admin@westval.com`
- Password: `Admin@Westval2025!`

**Demo User** (if loaded demo data):
- Email: `demo.validator@westval.com`
- Password: `Demo@2025!`

---

## Active Directory Integration Details

### How AD Authentication Works

1. User enters username and password
2. System attempts AD authentication
3. If successful, user details are synced from AD
4. AD groups are mapped to application roles
5. User is logged in with appropriate permissions

### AD Group Mapping

Edit `backend/app/services/ldap_service.py` to map your AD groups:

```python
group_role_mapping = {
    'CN=Westval_Admins,OU=Groups,DC=example,DC=com': 'Admin',
    'CN=Westval_Validators,OU=Groups,DC=example,DC=com': 'Validator',
    'CN=Westval_QA,OU=Groups,DC=example,DC=com': 'QA',
    'CN=Westval_Approvers,OU=Groups,DC=example,DC=com': 'Approver',
}
```

### Testing AD Connection

1. Login as admin
2. Go to Settings → Test LDAP
3. Enter test AD credentials
4. Check connection result

---

## MySQL Configuration Options

### Using Existing MySQL Server

If you have an existing MySQL server:

```bash
# In .env
DB_HOST=your-mysql-server.com
DB_PORT=3306
DB_NAME=westval
DB_USER=westval_user
DB_PASSWORD=your_password
```

Then modify `docker-compose.yml` to remove the mysql service and update backend:

```yaml
backend:
  environment:
    DB_HOST: your-mysql-server.com
  # Remove depends_on: mysql
```

### Manual MySQL Setup

If setting up MySQL manually:

```sql
-- Connect to MySQL
mysql -u root -p

-- Create database
CREATE DATABASE westval CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create user
CREATE USER 'westval_user'@'%' IDENTIFIED BY 'your_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON westval.* TO 'westval_user'@'%';
FLUSH PRIVILEGES;
```

### Connecting from Local Machine

```bash
# Connect to Docker MySQL
mysql -h 127.0.0.1 -P 3306 -u westval_user -p westval

# Show tables
USE westval;
SHOW TABLES;

# Check data
SELECT * FROM users LIMIT 5;
```

---

## Common Configuration Scenarios

### Scenario 1: Local Development (No AD)

```bash
AUTH_TYPE=local
LDAP_ENABLED=false
DB_TYPE=mysql
DB_HOST=mysql
```

### Scenario 2: Production with AD

```bash
AUTH_TYPE=ad
LDAP_ENABLED=true
AD_DOMAIN=MYCOMPANY
AD_SERVER=ad.mycompany.com
AD_SEARCH_BASE=DC=mycompany,DC=com
DB_TYPE=mysql
DB_HOST=production-mysql.mycompany.com
```

### Scenario 3: Standard LDAP (not AD)

```bash
AUTH_TYPE=ldap
LDAP_ENABLED=true
LDAP_HOST=ldap://ldap.mycompany.com
LDAP_PORT=389
LDAP_BASE_DN=dc=mycompany,dc=com
LDAP_USER_DN=ou=users,dc=mycompany,dc=com
```

---

## Troubleshooting

### AD Connection Issues

**Problem**: "LDAP connection error"

**Solutions**:
1. Check AD server is reachable:
   ```bash
   ping ad.yourcompany.com
   telnet ad.yourcompany.com 389
   ```

2. Verify service account credentials
3. Check firewall rules (port 389 or 636 for LDAPS)
4. Ensure Docker container can reach AD server

### MySQL Connection Issues

**Problem**: "Can't connect to MySQL server"

**Solutions**:
1. Check MySQL is running:
   ```bash
   docker-compose ps mysql
   ```

2. Check MySQL logs:
   ```bash
   docker-compose logs mysql
   ```

3. Verify credentials in .env match docker-compose.yml

4. Try connecting manually:
   ```bash
   docker-compose exec mysql mysql -u westval_user -p
   ```

### Database Not Initializing

```bash
# Reset everything
docker-compose down -v
docker-compose up -d

# Wait 30 seconds for MySQL to start
sleep 30

# Initialize again
docker-compose exec backend flask init-db
```

### AD Users Not Getting Correct Roles

1. Check AD group membership
2. Verify group mapping in `ldap_service.py`
3. Check logs:
   ```bash
   docker-compose logs backend | grep LDAP
   ```

---

## Security Best Practices

### Production Deployment

1. **Change all default passwords**
   ```bash
   SECRET_KEY=<generate-random-key>
   JWT_SECRET_KEY=<generate-random-key>
   DB_PASSWORD=<strong-password>
   ```

2. **Use SSL for AD** (LDAPS on port 636)
   ```bash
   LDAP_HOST=ldaps://ad.yourcompany.com
   LDAP_PORT=636
   LDAP_USE_SSL=true
   ```

3. **Enable strict password policy**
   ```bash
   PASSWORD_MIN_LENGTH=12
   PASSWORD_EXPIRY_DAYS=90
   MAX_LOGIN_ATTEMPTS=3
   ```

4. **Limit CORS origins**
   ```bash
   CORS_ORIGINS=https://westval.yourcompany.com
   ```

5. **Use production database**
   - Separate MySQL server
   - Regular backups
   - Encrypted connections

---

## Next Steps

1. ✅ Configure your AD settings
2. ✅ Test AD login with your account
3. ✅ Map AD groups to roles
4. ✅ Load demo data or create first project
5. ✅ Configure email notifications
6. ✅ Set up backup strategy
7. ✅ Plan production deployment

## Support

For issues or questions:
- Check logs: `docker-compose logs -f`
- GitHub Issues: https://github.com/vipul-madhani/westval/issues
- Review `DEMO_SETUP.md` for features