# Deployment Guide for System//Zero

This guide covers deploying System//Zero in production using Docker, systemd, or PM2.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Docker Deployment](#docker-deployment)
- [Systemd Deployment](#systemd-deployment)
- [PM2 Deployment](#pm2-deployment)
- [Configuration](#configuration)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements
- **OS**: Linux (Ubuntu 20.04+, Debian 11+, RHEL 8+)
- **Python**: 3.12+
- **RAM**: 512MB minimum, 1GB recommended
- **Disk**: 1GB for application + logs
- **Network**: Port 8000 (or custom port)

### Dependencies
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y python3.12 python3.12-venv python3-pip

# RHEL/CentOS
sudo dnf install -y python3.12 python3-pip
```

---

## Docker Deployment

### 1. Build Image

```bash
# From repository root
docker build -t systemzero:latest .
```

### 2. Run Container

**Quick Start**:
```bash
docker run -d \
  --name systemzero \
  -p 8000:8000 \
  -v systemzero-logs:/app/logs \
  -v systemzero-data:/app/data \
  -e LOG_LEVEL=INFO \
  systemzero:latest
```

**Production with Docker Compose**:
```bash
# Edit docker-compose.yml for environment-specific settings
docker-compose up -d

# View logs
docker-compose logs -f systemzero

# Stop
docker-compose down
```

### 3. Configuration

Environment variables:
- `SYSTEMZERO_ENV`: `development` or `production` (default: `development`)
- `LOG_LEVEL`: `DEBUG`, `INFO`, `WARNING`, `ERROR` (default: `INFO`)
- `LOG_JSON`: `true` or `false` (default: `false`)
- `API_HOST`: Bind address (default: `0.0.0.0`)
- `API_PORT`: Bind port (default: `8000`)

### 4. Verify Deployment

```bash
# Check health
curl http://localhost:8000/health

# Check metrics
curl http://localhost:8000/metrics

# Check API status
curl http://localhost:8000/status
```

---

## Systemd Deployment

### 1. Install Application

```bash
# Create application directory
sudo mkdir -p /opt/systemzero
sudo chown $USER:$USER /opt/systemzero

# Clone repository
cd /opt/systemzero
git clone https://github.com/SaltProphet/SystemZero.git .

# Create virtual environment
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Create systemzero User

```bash
sudo useradd -r -s /bin/false systemzero
sudo chown -R systemzero:systemzero /opt/systemzero
```

### 3. Install Service

```bash
# Copy service file
sudo cp systemzero/scripts/systemzero.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable systemzero

# Start service
sudo systemctl start systemzero

# Check status
sudo systemctl status systemzero
```

### 4. View Logs

```bash
# Follow logs
sudo journalctl -u systemzero -f

# View recent logs
sudo journalctl -u systemzero -n 100

# View logs since boot
sudo journalctl -u systemzero -b
```

### 5. Management Commands

```bash
# Restart
sudo systemctl restart systemzero

# Stop
sudo systemctl stop systemzero

# Disable (prevent start on boot)
sudo systemctl disable systemzero

### 3. Configuration (SZ_* envs)

Environment variables (prefer SZ_* names; legacy vars are deprecated):

| Variable | Purpose | Default | Production Recommendation |
|---|---|---|---|
| SZ_LOG_LEVEL | Log level | INFO | INFO or WARNING |
| SZ_JSON_LOGS | Enable JSON logs | true in container | true |
| SZ_LOG_PATH | Log file path | /app/logs/systemzero.log | Point to writable volume |
| SZ_ENABLE_HEALTH | Enable /health | true | true (optionally behind firewall) |
| SZ_ENABLE_METRICS | Enable /metrics | true | true (scope via firewall) |
| SZ_ENABLE_RATE_LIMITING | Rate limiting middleware | true | true |
| SZ_RATE_LIMIT_RPM | Requests/minute | 60 | 60–200 based on capacity |
| SZ_RATE_LIMIT_BURST | Burst in 5s window | 40 | 10–40 |
| SZ_MAX_REQUEST_SIZE_MB | Request size limit | 10 | 5–10 |
| SZ_CORS_ORIGINS | Comma-separated origins | http://localhost,... | Restrict to your domains |
| SZ_TRUSTED_HOSTS | Trusted Host headers | (empty) | your-api.example.com |
| SZ_API_KEYS_PATH | API keys file | /app/config/api_keys.yaml | Mount secrets volume |

**Example (production)**:
```bash
### 1. Install PM2

```bash
# Install Node.js (required for PM2)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install PM2 globally
sudo npm install -g pm2
```

### 2. Install Application

```bash
# Create application directory
sudo mkdir -p /opt/systemzero
sudo chown $USER:$USER /opt/systemzero

# Clone repository
cd /opt/systemzero
git clone https://github.com/SaltProphet/SystemZero.git .

# Create virtual environment
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Start with PM2

```bash
cd /opt/systemzero

# Start in production mode
pm2 start deployment/ecosystem.config.js --env production

# Or in development mode
pm2 start deployment/ecosystem.config.js --env development

# Save PM2 process list
pm2 save

# Setup PM2 to start on boot
pm2 startup
# (follow the command output)
```

### 4. Management Commands

```bash
# View status
pm2 status
pm2 list

# View logs
pm2 logs systemzero-api
pm2 logs systemzero-api --lines 100

# Restart
pm2 restart systemzero-api

# Stop
pm2 stop systemzero-api

# Delete
pm2 delete systemzero-api

# Reload (zero-downtime)
pm2 reload systemzero-api

# Monitor
pm2 monit
```

### 5. Cluster Mode

PM2 automatically runs 4 instances in cluster mode (configured in ecosystem.config.js). Adjust based on CPU cores:

```javascript
// In ecosystem.config.js
instances: 'max',  // Use all CPU cores
// or
instances: 2,      // Specific number
```

---


### Security Hardening Tips

- Restrict `SZ_CORS_ORIGINS` to trusted domains (avoid `*` in production)
- Set `SZ_TRUSTED_HOSTS` to your public hostnames to block Host header spoofing
- Keep `/metrics` behind firewall or allowlist; rely on `SZ_ENABLE_METRICS` only when monitored
- Store `api_keys.yaml` on a read-only secret volume and rotate keys regularly
## Configuration

### Environment Variables

Create `.env` file (never commit to git):
```bash
# Application
SYSTEMZERO_ENV=production
LOG_LEVEL=INFO
LOG_JSON=true

# API
API_HOST=0.0.0.0
API_PORT=8000

# Security (Phase 6.4)
SECRET_KEY=your-secret-key-here
API_KEY_FILE=/opt/systemzero/config/api_keys.yaml
```

### API Keys

Generate initial admin key:
```bash
cd /opt/systemzero
source .venv/bin/activate
python3 -c "
from systemzero.interface.api.auth import APIKeyManager
manager = APIKeyManager()
key = manager.create_key('admin', 'admin', 'Bootstrap admin key')
print(f'Admin API Key: {key}')
"
```

Save the key securely and use it in API requests:
```bash
curl -H "X-API-Key: YOUR_ADMIN_KEY" http://localhost:8000/auth/token
```

---

## Monitoring

### Health Checks

```bash
# Manual health check
curl http://localhost:8000/health

# Expected response
{
  "status": "healthy",
  "timestamp": "2026-01-07T18:00:00Z",
  "checks": [
    {"name": "log_directory", "status": "healthy", ...},
    {"name": "template_directory", "status": "healthy", ...},
    {"name": "api_keys_file", "status": "healthy", ...}
  ]
}
```

### Metrics

```bash
# Get metrics
curl http://localhost:8000/metrics

# Key metrics to monitor
- http_requests_total: Total requests
- http_errors_total: Error count
- http_request_duration_seconds: Response times (p50, p95, p99)
- http_requests_active: Concurrent requests
```

### External Monitoring

**Prometheus** (future):
- Metrics endpoint: `GET /metrics` (convert to Prometheus format)
- Scrape interval: 15s

**Grafana** (future):
- Import dashboard for System//Zero metrics
- Alert on error rates, response times

**Uptime Monitoring**:
```bash
# Add to monitoring service (Pingdom, UptimeRobot, etc.)
Endpoint: http://your-server:8000/health
Expected: HTTP 200, {"status": "healthy"}
Interval: 1 minute
```

---

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker logs systemzero

# Common issues:
# 1. Port already in use
docker ps | grep 8000
# Kill conflicting process or use different port

# 2. Permission issues
docker run --user $(id -u):$(id -g) ...

# 3. Missing volumes
docker volume ls
docker volume inspect systemzero-logs
```

### Systemd Service Fails

```bash
# Check detailed status
sudo systemctl status systemzero -l

# Check logs with timestamps
sudo journalctl -u systemzero -e --no-pager

# Common issues:
# 1. Python path incorrect
which python3.12
# Update ExecStart in systemzero.service

# 2. Permissions
ls -la /opt/systemzero/logs
sudo chown -R systemzero:systemzero /opt/systemzero

# 3. Port in use
sudo lsof -i :8000
# Kill process or change port in service file
```

### PM2 Process Crashes

```bash
# View error logs
pm2 logs systemzero-api --err --lines 50

# Common issues:
# 1. Memory limit exceeded
pm2 restart systemzero-api --max-memory-restart 2G

# 2. Port conflicts
pm2 delete systemzero-api
# Edit ecosystem.config.js to use different port

# 3. Missing dependencies
cd /opt/systemzero
source .venv/bin/activate
pip install -r requirements.txt
pm2 restart systemzero-api
```

### High Memory Usage

```bash
# Check current usage
docker stats systemzero
# or
ps aux | grep systemzero

# Solutions:
# 1. Reduce worker count (systemd/PM2)
# 2. Implement metrics pruning (Phase 6.2)
# 3. Add log rotation
```

### Network Issues

```bash
# Test from server
curl http://localhost:8000/health

# Test from external
curl http://YOUR_SERVER_IP:8000/health

# Check firewall
sudo ufw status
sudo ufw allow 8000/tcp

# Check binding
sudo netstat -tulpn | grep 8000
```

---

## Security Hardening

### 1. Use HTTPS

```bash
# Use reverse proxy (nginx/Apache)
# Or use Cloudflare/AWS ALB for TLS termination
```

### 2. Restrict Access

```bash
# Firewall rules
sudo ufw allow from TRUSTED_IP to any port 8000
sudo ufw deny 8000/tcp
```

### 3. Environment Secrets

```bash
# Never commit .env or api_keys.yaml
echo ".env" >> .gitignore
echo "config/api_keys.yaml" >> .gitignore

# Use secure file permissions
chmod 600 config/api_keys.yaml
chmod 600 .env
```

### 4. Regular Updates

```bash
# Update application
cd /opt/systemzero
git pull
pip install -r requirements.txt --upgrade

# Restart service
sudo systemctl restart systemzero
# or
pm2 reload systemzero-api
```

---

## Production Checklist

- [ ] Environment set to `production`
- [ ] JSON logging enabled (`LOG_JSON=true`)
- [ ] API keys configured with strong credentials
- [ ] Firewall rules configured
- [ ] HTTPS/TLS enabled (reverse proxy)
- [ ] Health checks configured in load balancer
- [ ] Log rotation configured
- [ ] Monitoring/alerting configured
- [ ] Backup strategy for config/data
- [ ] Documentation for team
- [ ] Incident response procedures

---

## Support

- **GitHub Issues**: https://github.com/SaltProphet/SystemZero/issues
- **Documentation**: See project README.md and ARCHITECTURE.md
- **Logs**: Check application logs for detailed error messages
