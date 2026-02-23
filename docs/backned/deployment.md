# Deployment Documentation

## Overview

This guide provides comprehensive instructions for deploying the Podd Health Assistant backend application to various environments including development, staging, and production.

**Dual-Database Architecture**:
- **SQLite (`podd_auth.db`)**: Stores ONLY authentication data (Users, RefreshTokens tables) - no health data
- **LocusGraph SDK**: Stores ALL health and personal data (Profiles, Vitals, Medications, Schedules, Activities, Reminders, Chat) - the primary data store

## Deployment Architecture

### Production Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Load Balancer                           │
│                    (Nginx / Cloud Load Balancer)                │
└────────────────────────────┬────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│  App Server 1 │   │  App Server 2 │   │  App Server N │
│   (Worker 1)  │   │   (Worker 2)  │   │   (Worker N)  │
└───────┬───────┘   └───────┬───────┘   └───────┬───────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│  SQLite DB    │   │  LocusGraph   │   │  Redis Cache  │
│  (Auth Only)  │   │  SDK Service  │   │  (Optional)   │
│  (podd_auth.db)│  │  (Health)     │   │               │
└───────────────┘   └───────────────┘   └───────────────┘
```

---

## Prerequisites

### Required Resources

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| CPU | 2 cores | 4+ cores |
| RAM | 4 GB | 8+ GB |
| Disk Space | 50 GB | 100+ GB |
| Network | 1 Gbps | 10 Gbps+ |

### Software Requirements

- **Python**: 3.11+
- **SQLite**: Built-in (for auth database)
- **LocusGraph SDK**: Available as external service
- **Redis**: 6.0+ (optional, for caching)
- **Nginx**: 1.18+ (optional, for reverse proxy)
- **Systemd**: (Linux)
- **Supervisor**: (Linux, optional)
- **Docker**: (optional, for containerized deployment)

---

## Development Deployment

### Local Development Setup

#### 1. Clone Repository

```bash
git clone <repository-url>
cd podd/backend
```

#### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv podd_env

# Activate virtual environment
# On Linux/Mac:
source podd_env/bin/activate
# On Windows:
podd_env\Scripts\activate
```

#### 3. Install Dependencies

```bash
# Install from requirements.txt
pip install -r requirements.txt

# Or use poetry (recommended)
poetry install
```

#### 4. Configure Environment

Copy and edit `.env` file:

```bash
cp .env.example .env
nano .env
```

#### 5. Run Database Setup

```bash
# SQLite auth tables are created automatically on startup
# LocusGraph events are stored via LocusGraph SDK calls
# No manual database setup needed
```

#### 6. Run Application

```bash
# Development mode with auto-reload
python src/main.py

# Or using uvicorn
uvicorn src.main:app --reload --port 8000 --host 0.0.0.0
```

#### 7. Verify Deployment

- Open browser: http://localhost:8000
- Check API docs: http://localhost:8000/docs
- Test API endpoints
- Verify LocusGraph SDK connectivity

---

## Staging Deployment

### Staging Environment Setup

#### 1. Environment Configuration

Create staging-specific `.env` file:

```bash
# Staging Environment
DATABASE_URL=sqlite+aiosqlite:///./podd_auth_staging.db
LOCUSGRAPH_API_URL=http://staging-locusgraph.example.com
LOCUSGRAPH_API_KEY=staging-locusgraph-key
LOCUSGRAPH_GRAPH_ID=podd_staging
SARVAM_API_KEY=staging-sarvam-key
JWT_SECRET=staging-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=60
JWT_REFRESH_EXPIRATION_DAYS=7
CORS_ORIGINS=["https://staging.example.com"]
DEBUG=True
PORT=8000
```

#### 2. Setup Databases

```bash
# SQLite auth database will be created automatically
# LocusGraph will be configured via API key
```

#### 3. Deploy Application

```bash
# Option 1: Direct deployment
source podd_env/bin/activate
python src/main.py

# Option 2: Using systemd (Linux)
sudo systemctl start podd-staging
```

#### 4. Verify Staging

- Test all endpoints
- Verify SQLite auth database connectivity
- Verify LocusGraph SDK integration
- Check AI service integration
- Test with staging users

---

## Production Deployment

### 1. Infrastructure Preparation

#### SQLite Authentication Database Setup

```bash
# Install SQLite (usually pre-installed on Linux)
sqlite3 --version

# SQLite will create podd_auth.db automatically on first run
# No manual database setup required
```

#### LocusGraph SDK Setup

```bash
# Ensure LocusGraph service is available
curl http://localhost:8001/health

# Verify API key is configured in LocusGraph service
```

#### Redis Setup (Optional but Recommended)

```bash
# Install Redis
sudo apt-get install redis-server

# Configure Redis
sudo nano /etc/redis/redis.conf

# Set these parameters:
bind 127.0.0.1
port 6379
requirepass your_redis_password
maxmemory 2gb
maxmemory-policy allkeys-lru

# Start Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

### 2. Application Configuration

#### Production Environment Variables

Create `.env.production`:

```env
# SQLite Authentication Database
DATABASE_URL=sqlite+aiosqlite:///./podd_auth.db

# LocusGraph SDK Configuration
LOCUSGRAPH_API_URL=http://localhost:8001
LOCUSGRAPH_API_KEY=your-locusgraph-api-key
LOCUSGRAPH_GRAPH_ID=podd_production

# AI Service Configuration
OPENAI_API_KEY=your-openai-api-key
SARVAM_API_KEY=your-sarvam-api-key

# JWT Configuration
JWT_SECRET=generate-a-strong-secret-key-using-openssl
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=60
JWT_REFRESH_EXPIRATION_DAYS=7

# CORS Configuration
CORS_ORIGINS=["https://app.example.com", "https://www.example.com"]

# Application Configuration
DEBUG=False
PORT=8000
HOST=0.0.0.0

# Optional - Redis Cache
REDIS_URL=redis://:your_redis_password@localhost:6379/0
CACHE_TTL=3600

# Optional - Sentry Error Tracking
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id

# Optional - Rate Limiting
RATE_LIMIT_PER_MINUTE=100
```

#### Generate Secure JWT Secret

```bash
# Generate a secure secret key
openssl rand -hex 32

# Use the output in your .env file
```

### 3. Server Setup

#### System Dependencies

```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y python3.11 python3.11-venv nginx sqlite3 postgresql-client redis-server libpq-dev

# Install Python packages
pip install --upgrade pip

# Create application directory
sudo mkdir -p /opt/podd
sudo chown $USER:$USER /opt/podd
cd /opt/podd
```

#### Virtual Environment Setup

```bash
# Create virtual environment
python3.11 -m venv podd_env

# Activate virtual environment
source podd_env/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Create .env file
nano .env.production

# Deactivate virtual environment
deactivate
```

#### Deploy Application Files

```bash
# Copy application files
cd /opt/podd
git clone <repository-url> .
cd backend

# Set up environment
cp .env.production .env
source podd_env/bin/activate
pip install -r requirements.txt
deactivate

# Set permissions
sudo chown -R www-data:www-data /opt/podd
```

### 4. Web Server Configuration (Nginx)

#### Create Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/podd

# Add configuration:
server {
    listen 80;
    server_name api.example.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.example.com;

    # SSL Configuration
    ssl_certificate /etc/ssl/certs/podd.crt;
    ssl_certificate_key /etc/ssl/private/podd.key;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Logging
    access_log /var/log/nginx/podd_access.log;
    error_log /var/log/nginx/podd_error.log;

    # Maximum upload size
    client_max_body_size 10M;

    # Proxy settings
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Timeouts
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }

    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
```

#### Enable Site

```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/podd /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

### 5. Application Service (Systemd)

#### Create Systemd Service

```bash
sudo nano /etc/systemd/system/podd.service

# Add configuration:
[Unit]
Description=Podd Health Assistant Backend
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/podd/backend
Environment="PATH=/opt/podd/backend/podd_env/bin"
ExecStart=/opt/podd/backend/podd_env/bin/uvicorn src.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4 \
    --log-level info \
    --access-log
Restart=always
RestartSec=10

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/podd

[Install]
WantedBy=multi-user.target
```

#### Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable podd

# Start service
sudo systemctl start podd

# Check status
sudo systemctl status podd

# View logs
sudo journalctl -u podd -f
```

### 6. Firewall Configuration

```bash
# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable
```

### 7. SSL Certificate Setup (Let's Encrypt)

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d api.example.com

# Auto-renewal is configured automatically
sudo certbot renew --dry-run
```

### 8. Monitoring & Logging

#### Configure Logging

```python
# In src/main.py or config.py
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/podd/app.log'),
        logging.StreamHandler()
    ]
)
```

#### Set up log rotation

```bash
sudo nano /etc/logrotate.d/podd

# Add configuration:
/opt/podd/backend/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0644 www-data www-data
    sharedscripts
    postrotate
        systemctl reload podd > /dev/null 2>&1 || true
    endscript
}
```

#### Set up Monitoring

```bash
# Install monitoring tools
sudo apt-get install htop iotop nethogs

# Set up log monitoring
tail -f /var/log/podd/app.log

# Check resource usage
htop
```

---

## Docker Deployment

### Dockerfile

```dockerfile
# Use Python 3.11 as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    sqlite3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite+aiosqlite:///./podd_auth.db
      - LOCUSGRAPH_API_URL=http://locusgraph:8001
      - LOCUSGRAPH_API_KEY=${LOCUSGRAPH_API_KEY}
      - LOCUSGRAPH_GRAPH_ID=podd
      - SARVAM_API_KEY=${SARVAM_API_KEY}
      - JWT_SECRET=${JWT_SECRET}
      - CORS_ORIGINS=["http://localhost:3000"]
    depends_on:
      - locusgraph
    volumes:
      - ./data:/app/data
    restart: unless-stopped

  locusgraph:
    image: locusgraph/service:latest
    ports:
      - "8001:8001"
    environment:
      - LOCUSGRAPH_API_KEY=${LOCUSGRAPH_API_KEY}
    restart: unless-stopped

  nginx:
    image: nginx:latest
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend
    restart: unless-stopped
```

### Docker Deployment Commands

```bash
# Build Docker image
docker build -t podd-backend:latest .

# Run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down

# Clean up
docker-compose down -v
```

---

## Kubernetes Deployment

### Kubernetes Manifests

```yaml
# podd-backend.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: podd-backend
  labels:
    app: podd-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: podd-backend
  template:
    metadata:
      labels:
        app: podd-backend
    spec:
      containers:
      - name: backend
        image: podd-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          value: "sqlite+aiosqlite:///podd_auth.db"
        - name: LOCUSGRAPH_API_URL
          valueFrom:
            configMapKeyRef:
              name: podd-config
              key: locusgraph-api-url
        - name: SARVAM_API_KEY
          valueFrom:
            secretKeyRef:
              name: podd-secrets
              key: sarvam-key
        - name: JWT_SECRET
          valueFrom:
            secretKeyRef:
              name: podd-secrets
              key: jwt-secret
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: podd-backend-service
spec:
  selector:
    app: podd-backend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: podd-config
data:
  locusgraph-api-url: "http://locusgraph-service"
---
apiVersion: v1
kind: Secret
metadata:
  name: podd-secrets
type: Opaque
stringData:
  sarvam-key: "your-sarvam-api-key"
  jwt-secret: "your-jwt-secret"
```

### Kubernetes Deployment Commands

```bash
# Apply manifests
kubectl apply -f podd-backend.yaml

# Check deployment status
kubectl get pods -l app=podd-backend
kubectl get services

# View logs
kubectl logs -l app=podd-backend -f

# Scale deployment
kubectl scale deployment podd-backend --replicas=5

# Rollout update
kubectl set image deployment/podd-backend backend=podd-backend:v2.0

# Rollback if needed
kubectl rollout undo deployment/podd-backend
```

---

## Monitoring & Observability

### Health Checks

```python
# Add health check endpoint in src/main.py
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected",
        "locusgraph": "connected",
        "ai_service": "connected",
        "timestamp": datetime.utcnow().isoformat()
    }
```

### Metrics Collection

```python
from prometheus_fastapi_instrumentator import Instrumentator

# Add Prometheus metrics
Instrumentator().instrument(app).expose(app)
```

### Error Tracking (Sentry)

```python
import sentry_sdk

# Initialize Sentry
sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)

# Set environment
sentry_sdk.set_context({
    "environment": "production"
})
```

### Logging Configuration

```python
import logging

# Configure production logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/podd/app.log'),
        logging.StreamHandler()
    ]
)
```

---

## Backup & Recovery

### SQLite Backup

```bash
#!/bin/bash
# backup.sh

# SQLite auth database backup
sqlite3 podd_auth.db ".backup 'podd_auth_backup_$(date +%Y%m%d_%H%M%S).db'"

# Backup external data (LocusGraph)
# Add custom backup logic here

# Keep only last 7 days
find /backup -name "podd_auth_backup_*.db" -mtime +7 -delete

echo "Backup completed at $(date)"
```

#### Cron Job for Backups

```bash
# Add to crontab
crontab -e

# Daily backup at 2 AM
0 2 * * * /opt/podd/backup.sh
```

### LocusGraph Backup

```bash
#!/bin/bash
# locusgraph_backup.sh

# Export LocusGraph graph data
curl -X POST "http://localhost:8001/export" \
  -H "X-API-Key: $LOCUSGRAPH_API_KEY" \
  -o "locusgraph_backup_$(date +%Y%m%d_%H%M%S).json"

# Keep only last 7 days
find /backup -name "locusgraph_backup_*.json" -mtime +7 -delete

echo "LocusGraph backup completed at $(date)"
```

### Recovery Procedure

```bash
# Restore SQLite auth database
sqlite3 podd_auth.db ".restore 'podd_auth_backup_20260218_020000.db'"

# Restore LocusGraph graph data
curl -X POST "http://localhost:8001/import" \
  -H "X-API-Key: $LOCUSGRAPH_API_KEY" \
  -d @locusgraph_backup_20260218_020000.json

# Verify restoration
sqlite3 podd_auth.db "SELECT COUNT(*) FROM users;"

# Restart application
sudo systemctl restart podd
```

---

## Security Hardening

### Security Best Practices

1. **Always use HTTPS**
2. **Use strong passwords**
3. **Enable CORS properly**
4. **Rate limiting**
5. **Input validation**
6. **Secure JWT secrets**
7. **Regular security updates**
8. **Security headers**
9. **Firewall configuration**
10. **Database encryption at rest**

### Security Checklist

- [ ] SSL certificates installed and valid
- [ ] Strong database passwords
- [ ] Secure JWT secrets
- [ ] CORS configured correctly
- [ ] Rate limiting enabled
- [ ] Input validation in place
- [ ] Security headers configured
- [ ] Firewall rules set up
- [ ] Regular security updates
- [ ] Backup strategy in place
- [ ] Monitoring and alerting
- [ ] Error messages sanitized
- [ ] No sensitive data in logs
- [ ] User authentication enabled
- [ ] Role-based access control

---

## Performance Optimization

### SQLite Optimization

```sql
-- Analyze query performance
EXPLAIN QUERY PLAN SELECT * FROM users WHERE email = 'test@example.com';

-- Optimize database periodically
VACUUM;
ANALYZE;
```

### Application Optimization

```python
# Connection pooling
engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# Cache frequently accessed data
from functools import lru_cache

@lru_cache(maxsize=1000)
async def get_user_profile(user_id: str):
    # Return cached user profile
    pass
```

### Load Balancing

Configure Nginx as reverse proxy with multiple workers:

```nginx
upstream podd_backend {
    least_conn;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
    server 127.0.0.1:8004;
}

server {
    location / {
        proxy_pass http://podd_backend;
    }
}
```

---

## Troubleshooting

### Common Issues

#### 1. Database Connection Issues

**Symptoms**: Application can't connect to database

**Solution**:
```bash
# Check SQLite database exists
ls -la podd_auth.db

# Check SQLite version
sqlite3 podd_auth.db ".version"

# Check database integrity
sqlite3 podd_auth.db "PRAGMA integrity_check;"

# Restart application
sudo systemctl restart podd
```

#### 2. Application Won't Start

**Symptoms**: Service fails to start

**Solution**:
```bash
# Check service status
sudo systemctl status podd

# View logs
sudo journalctl -u podd -n 50

# Check application logs
tail -f /var/log/podd/app.log

# Restart service
sudo systemctl restart podd
```

#### 3. LocusGraph SDK Connection Issues

**Symptoms**: LocusGraph SDK can't connect

**Solution**:
```bash
# Check LocusGraph service is running
curl http://localhost:8001/health

# Check API key
echo $LOCUSGRAPH_API_KEY

# Verify LocusGraph configuration
nano .env.production

# Restart application
sudo systemctl restart podd
```

#### 4. High Memory Usage

**Symptoms**: Application using excessive memory

**Solution**:
```bash
# Check memory usage
free -h

# Check application logs for memory leaks
tail -f /var/log/podd/app.log

# Restart application
sudo systemctl restart podd

# Check worker configuration
# Increase number of workers if needed
```

---

## Maintenance

### Routine Maintenance Tasks

#### Daily
- [ ] Monitor application health
- [ ] Check application logs
- [ ] Monitor database performance

#### Weekly
- [ ] Review system logs
- [ ] Check backup integrity
- [ ] Review security logs
- [ ] Update dependencies (if needed)

#### Monthly
- [ ] Database maintenance and optimization
- [ ] Security audit
- [ ] Backup verification
- [ ] Performance tuning

### Maintenance Schedule

| Task | Frequency | Responsible |
|------|-----------|-------------|
| Application monitoring | Daily | DevOps |
| Log review | Weekly | DevOps |
| Database backup | Daily | Automated |
| Security updates | Weekly | Security Team |
| Dependency updates | Monthly | DevOps |
| Performance tuning | Monthly | DevOps |

---

## Rollback Procedure

### Quick Rollback

```bash
# Stop current version
sudo systemctl stop podd

# Restore from backup
cd /opt/podd
git checkout previous-version

# Reinstall dependencies
source podd_env/bin/activate
pip install -r requirements.txt
deactivate

# Start service
sudo systemctl start podd

# Verify
sudo systemctl status podd
```

### Database Rollback

```bash
# Restore SQLite auth database
sqlite3 podd_auth.db ".restore 'podd_auth_backup_20260218_020000.db'"

# Restart application
sudo systemctl restart podd
```

---

## Support & Contacts

### Contact Information

- **Technical Support**: support@example.com
- **Emergency**: 24/7 hotline: 1-800-123-4567
- **System Status**: https://status.example.com

### Documentation Links

- API Documentation: https://docs.example.com/api
- Architecture Overview: https://docs.example.com/architecture
- Database Schema: https://docs.example.com/database

---

## References

- FastAPI Deployment: https://fastapi.tiangolo.com/deployment/
- SQLite Performance: https://www.sqlite.org/performance.html
- LocusGraph Documentation: [External Documentation]
- Nginx Configuration: https://nginx.org/en/docs/
- Docker Best Practices: https://docs.docker.com/develop/dev-best-practices/
