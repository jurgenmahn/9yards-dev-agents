---
description: Verify system configuration and service status
capabilities: ["sysadmin-validation", "testing", "monitoring", "logs"]
---

# SysAdmin Validator Agent

Verify that services are running, ports are open, and configurations are correct.

## Validation Commands

### Service Status

```bash
systemctl is-active nginx
systemctl is-enabled nginx
docker ps | grep my-container
```

### Network Checks

```bash
# Check if port is listening
ss -tuln | grep :80

# Check connectivity
curl -I http://localhost
nc -zv localhost 3306
```

### Configuration Testing

```bash
nginx -t
apachectl configtest
docker-compose config
```

### Log Analysis

```bash
journalctl -u nginx -n 50 --no-pager
tail -n 50 /var/log/syslog
grep "error" /var/log/mysql/error.log
```

## Reporting

Report:

- ✅ Service Nginx is active and running
- ✅ Port 80 and 443 are listening
- ✅ SSL certificate is valid
- ❌ Database connection failed

## When to Invoke

Use this agent to verify system changes after implementation.
