# Docker Operations Skill

**PURPOSE**: Command-line Docker and Compose operations reference

## Container Management

### List & Inspect
```bash
# List running containers
docker compose ps

# Container resource usage
docker stats --no-stream

# Inspect container
docker inspect <container_id>
```

### Service Control
```bash
# Start all services
docker compose up -d

# Restart service
docker compose restart <service>

# Stop all
docker compose down
```

### Logs & Debugging
```bash
# Follow logs
docker compose logs -f <service>

# Last 100 lines
docker compose logs --tail=100 <service>
```

### Exec into Containers
```bash
# Bash shell
docker compose exec <service> bash

# Run command
docker compose exec magento bin/magento cache:clean
```

## BuildKit & Image Management

### Building
```bash
# Build with BuildKit
DOCKER_BUILDKIT=1 docker build -t myimage:tag .

# Build with compose
docker compose build

# Force rebuild
docker compose build --no-cache <service>
```

### Cache Management
```bash
# Prune build cache
docker builder prune -f

# Aggressive cleanup
docker system prune -a --volumes
```

## Testing & Development

### Database Operations
```bash
# Create test database
docker compose exec mysql mysql -u root -p$MYSQL_ROOT_PASSWORD << SQL
DROP DATABASE IF EXISTS magento_test;
CREATE DATABASE magento_test;
GRANT ALL ON magento_test.* TO 'magento'@'%';
SQL
```

### Service Health Checks
```bash
# Wait for healthy
timeout 60 bash -c 'until docker compose ps | grep healthy; do sleep 2; done'

# Check MySQL readiness
docker compose exec mysql mysqladmin ping -h localhost

# Magento setup status
docker compose exec magento bin/magento setup:db:status
```

## Network Debugging

### Connectivity Tests
```bash
# Test inter-container networking
docker compose exec magento ping mysql

# Port check
docker compose exec magento nc -zv mysql 3306
```

## Common Workflows

### Fresh Start
```bash
#!/bin/bash
docker compose down -v
docker compose build --no-cache
docker compose up -d
timeout 120 bash -c 'until docker compose ps | grep -q "healthy"; do sleep 5; done'
echo "✅ Fresh environment ready"
```

### Quick Reset
```bash
#!/bin/bash
docker compose restart
docker compose exec magento bin/magento cache:flush
docker compose exec redis redis-cli FLUSHALL
echo "✅ Environment reset"
```

## Best Practices

1. **Always use `docker compose` (not `docker-compose`)**
2. **Enable BuildKit globally**
3. **Use named volumes for persistence**
4. **Add health checks in compose**
5. **Set resource limits for stability**
6. **Regular cleanup** - weekly prune

## Troubleshooting

### Container won't start
```bash
docker compose logs <service>
docker compose up <service>
```

### Out of disk space
```bash
docker system df
docker builder prune -f
docker image prune -a
```

### Performance issues
```bash
docker stats
# Increase memory in docker-compose.yml
```
