"""
# User Guide

## Installation

See README.md for installation instructions.

## Quick Start

### Basic Usage

```bash
# Run all modules
python src/main.py

# Run specific module
python src/main.py --module data_cleaner
```

### Configuration

Edit `config/config.yaml` to customize:
- Data cleaning rules
- Report formats
- Health check thresholds
- Email notifications

### Data Cleaning

```bash
# Clean files in default directory
python src/main.py --module data_cleaner

# Clean specific directory
python src/main.py --module data_cleaner --input data/raw --output data/clean
```

### Report Generation

```bash
# Generate HTML report
python src/main.py --module report_generator --format html

# Generate Excel report
python src/main.py --module report_generator --format excel
```

### System Health Monitoring

```bash
# Single health check
python src/main.py --module health_check

# Continuous monitoring
python src/main.py --module health_check --monitor-duration 3600
```

## Advanced Usage

### Custom Configuration

Create custom config files:

```yaml
# config/production.yaml
application:
  name: "Production Automation"
  environment: "production"

data_cleaner:
  enabled: true
  outlier_method: "zscore"
```

Use custom config:

```bash
python src/main.py --config config/production.yaml
```

### Email Notifications

Configure in `.env`:

```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### Docker Deployment

```bash
# Build image
docker build -t automation-tool .

# Run container
docker run -v $(pwd)/data:/app/data automation-tool
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure virtual environment is activated
2. **Permission Errors**: Check file permissions
3. **Configuration Errors**: Validate YAML syntax
4. **Email Failures**: Verify SMTP settings

### Getting Help

- Check logs in `data/logs/app.log`
- Review documentation
- Open GitHub issue
"""