# API Reference

Complete API documentation for the Operational Automation Tool.

## Table of Contents

- [Configuration](#configuration)
- [Data Cleaner](#data-cleaner)
- [Report Generator](#report-generator)
- [System Health Checker](#system-health-checker)
- [Utilities](#utilities)
- [Data Models](#data-models)

---

## Configuration

### Settings

**Module**: `src.config.settings`

#### `Settings`

Main application settings class using Pydantic.

```python
from src.config.settings import get_settings

settings = get_settings()
```

**Attributes**:
- `app_name` (str): Application name
- `app_version` (str): Version number
- `environment` (str): Environment (development/staging/production)
- `logging` (LoggingConfig): Logging configuration
- `data_cleaner` (DataCleanerConfig): Data cleaner settings
- `report_generator` (ReportGeneratorConfig): Report generator settings
- `system_health` (SystemHealthConfig): Health checker settings
- `email_notifications` (EmailConfig): Email notification settings

**Methods**:

##### `from_yaml(yaml_path: str) -> Settings`
Load settings from YAML file.

```python
settings = Settings.from_yaml('config/config.yaml')
```

##### `update_from_env() -> None`
Update settings from environment variables.

```python
settings.update_from_env()
```

#### `get_settings(config_path: str = 'config/config.yaml') -> Settings`

Get or create global settings instance.

```python
settings = get_settings()
```

### Logging

**Module**: `src.config.logging_config`

#### `setup_logging(log_level: str = None, log_file: str = None, log_format: str = None) -> None`

Setup application-wide logging.

```python
from src.config.logging_config import setup_logging

setup_logging(log_level='INFO', log_file='app.log')
```

**Parameters**:
- `log_level`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `log_file`: Path to log file
- `log_format`: Log message format string

#### `get_logger(name: str) -> logging.Logger`

Get a named logger instance.

```python
from src.config.logging_config import get_logger

logger = get_logger(__name__)
logger.info('Starting process')
```

---

## Data Cleaner

**Module**: `src.automation.data_cleaner`

### `DataCleaner`

Automated data cleaning and quality improvement.

#### Initialization

```python
from src.automation.data_cleaner import DataCleaner

cleaner = DataCleaner()
```

#### Methods

##### `clean_file(file_path: str, output_path: str = None) -> DataQualityReport`

Clean a single data file.

```python
report = cleaner.clean_file('data/input/sales.csv', 'data/output/sales_clean.csv')
print(f"Duplicates removed: {report.duplicates_removed}")
```

**Parameters**:
- `file_path` (str): Path to input file
- `output_path` (str, optional): Path for cleaned output

**Returns**: `DataQualityReport` with cleaning results

**Raises**:
- `FileNotFoundError`: If input file doesn't exist
- `ValueError`: If file format is unsupported

##### `clean_directory(input_dir: str = None, output_dir: str = None) -> List[DataQualityReport]`

Clean all files in a directory.

```python
reports = cleaner.clean_directory('data/input', 'data/output')
print(f"Processed {len(reports)} files")
```

**Parameters**:
- `input_dir` (str, optional): Input directory path
- `output_dir` (str, optional): Output directory path

**Returns**: List of `DataQualityReport` for each file

##### `get_summary_report() -> Dict`

Get summary of all cleaning operations.

```python
summary = cleaner.get_summary_report()
print(f"Total files: {summary['total_files_processed']}")
print(f"Total duplicates: {summary['total_duplicates_removed']}")
```

**Returns**: Dictionary with summary statistics

**Example**:

```python
from src.automation.data_cleaner import DataCleaner

# Initialize cleaner
cleaner = DataCleaner()

# Clean single file
report = cleaner.clean_file('data/input/customers.csv')

# Print results
print(f"Status: {report.status}")
print(f"Rows processed: {report.total_rows}")
print(f"Duplicates removed: {report.duplicates_removed}")
print(f"Missing values handled: {report.missing_values_handled}")
print(f"Outliers detected: {report.outliers_detected}")
```

---

## Report Generator

**Module**: `src.automation.report_generator`

### `ReportGenerator`

Generate comprehensive reports with visualizations.

#### Initialization

```python
from src.automation.report_generator import ReportGenerator

generator = ReportGenerator()
```

#### Methods

##### `generate_data_quality_report(data_reports: List[DataQualityReport], output_format: str = 'html') -> str`

Generate data quality report from cleaning results.

```python
report_path = generator.generate_data_quality_report(
    data_reports=cleaning_reports,
    output_format='html'
)
print(f"Report saved to: {report_path}")
```

**Parameters**:
- `data_reports` (List[DataQualityReport]): List of quality reports
- `output_format` (str): Output format ('html', 'pdf', 'excel')

**Returns**: Path to generated report (str)

##### `generate_automation_report(automation_report: AutomationReport, output_format: str = 'html') -> str`

Generate comprehensive automation execution report.

```python
report_path = generator.generate_automation_report(
    automation_report=exec_report,
    output_format='json'
)
```

**Parameters**:
- `automation_report` (AutomationReport): Automation execution report
- `output_format` (str): Output format ('html', 'json')

**Returns**: Path to generated report (str)

**Example**:

```python
from src.automation.data_cleaner import DataCleaner
from src.automation.report_generator import ReportGenerator

# Clean data
cleaner = DataCleaner()
data_reports = cleaner.clean_directory('data/input')

# Generate report
generator = ReportGenerator()
report_path = generator.generate_data_quality_report(
    data_reports,
    output_format='html'
)

print(f"Report generated: {report_path}")
```

---

## System Health Checker

**Module**: `src.automation.system_health_checker`

### `SystemHealthChecker`

Monitor system health and resource usage.

#### Initialization

```python
from src.automation.system_health_checker import SystemHealthChecker

checker = SystemHealthChecker()
```

#### Methods

##### `check_health() -> SystemHealthReport`

Perform comprehensive system health check.

```python
report = checker.check_health()
print(f"Status: {report.status}")
print(f"CPU: {report.metrics.cpu_percent}%")
print(f"Memory: {report.metrics.memory_percent}%")
```

**Returns**: `SystemHealthReport` with current status

##### `get_detailed_info() -> Dict`

Get detailed system information.

```python
info = checker.get_detailed_info()
print(f"CPU cores: {info['cpu']['physical_cores']}")
print(f"Total memory: {info['memory']['total_gb']} GB")
```

**Returns**: Dictionary with comprehensive system details

##### `monitor_continuously(duration: int = 300, interval: int = 60, callback: callable = None) -> List[SystemHealthReport]`

Monitor system health continuously.

```python
def alert_callback(report):
    if report.status == 'critical':
        send_alert(report)

reports = checker.monitor_continuously(
    duration=3600,  # 1 hour
    interval=60,    # Every minute
    callback=alert_callback
)
```

**Parameters**:
- `duration` (int): Total monitoring duration in seconds
- `interval` (int): Check interval in seconds
- `callback` (callable, optional): Function called after each check

**Returns**: List of `SystemHealthReport` objects

##### `get_summary() -> Dict`

Get summary of all health checks performed.

```python
summary = checker.get_summary()
print(f"Total checks: {summary['total_checks']}")
print(f"Average CPU: {summary['average_metrics']['cpu_percent']}%")
```

**Returns**: Dictionary with summary statistics

**Example**:

```python
from src.automation.system_health_checker import SystemHealthChecker

# Initialize checker
checker = SystemHealthChecker()

# Single health check
report = checker.check_health()

# Display results
print(f"System Status: {report.status}")
print(f"\nMetrics:")
print(f"  CPU: {report.metrics.cpu_percent}%")
print(f"  Memory: {report.metrics.memory_percent}%")
print(f"  Disk: {report.metrics.disk_percent}%")

if report.alerts:
    print(f"\nAlerts:")
    for alert in report.alerts:
        print(f"  - {alert}")

if report.recommendations:
    print(f"\nRecommendations:")
    for rec in report.recommendations:
        print(f"  - {rec}")
```

---

## Utilities

### File Handler

**Module**: `src.utils.file_handler`

#### `FileHandler`

Handle file operations for various formats.

##### Initialization

```python
from src.utils.file_handler import FileHandler

handler = FileHandler(base_path='data')
```

##### Methods

###### `read_file(file_path: str, **kwargs) -> pd.DataFrame`

Read file into pandas DataFrame.

```python
df = handler.read_file('data/input/sales.csv')
```

**Supported formats**: CSV, Excel (.xlsx, .xls), JSON, Parquet

###### `write_file(data: pd.DataFrame, file_path: str, file_format: str = None, **kwargs) -> None`

Write DataFrame to file.

```python
handler.write_file(df, 'data/output/processed.csv')
```

###### `list_files(directory: str, pattern: str = '*', recursive: bool = False) -> List[Path]`

List files matching pattern.

```python
csv_files = handler.list_files('data/input', pattern='*.csv')
```

### Validators

**Module**: `src.utils.validators`

#### `DataValidator`

Validate data quality and integrity.

##### Initialization

```python
from src.utils.validators import DataValidator

validator = DataValidator()
```

##### Methods

###### `validate_dataframe(df: pd.DataFrame, schema: Dict = None, required_columns: List[str] = None) -> ValidationResult`

Validate entire DataFrame.

```python
result = validator.validate_dataframe(
    df,
    schema={'age': 'int', 'name': 'string'},
    required_columns=['id', 'name']
)

if result.is_valid:
    print("Data is valid!")
else:
    print(f"Errors: {result.errors}")
```

###### `validate_email(email: str) -> bool`

Validate email address format.

```python
is_valid = validator.validate_email('user@example.com')
```

###### `validate_date_range(date_series: pd.Series, min_date: datetime = None, max_date: datetime = None) -> ValidationResult`

Validate date range in a Series.

```python
result = validator.validate_date_range(
    df['order_date'],
    min_date=datetime(2020, 1, 1),
    max_date=datetime(2024, 12, 31)
)
```

###### `validate_numeric_range(series: pd.Series, min_value: float = None, max_value: float = None) -> ValidationResult`

Validate numeric values are within range.

```python
result = validator.validate_numeric_range(
    df['age'],
    min_value=0,
    max_value=120
)
```

###### `detect_outliers(series: pd.Series, method: str = 'iqr', threshold: float = 1.5) -> pd.Series`

Detect outliers in numeric series.

```python
outliers = validator.detect_outliers(
    df['price'],
    method='iqr',  # or 'zscore'
    threshold=1.5
)

print(f"Found {outliers.sum()} outliers")
```

### Email Notifier

**Module**: `src.utils.email_notifier`

#### `EmailNotifier`

Handle email notifications.

##### Initialization

```python
from src.utils.email_notifier import EmailNotifier

notifier = EmailNotifier()
```

##### Methods

###### `send_notification(subject: str, body: str, recipients: List[str] = None, attachments: List[str] = None, html: bool = False) -> bool`

Send email notification.

```python
success = notifier.send_notification(
    subject='Automation Complete',
    body='All tasks completed successfully',
    recipients=['admin@example.com'],
    attachments=['report.pdf'],
    html=True
)
```

###### `send_error_notification(error_message: str, module: str) -> bool`

Send error notification email.

```python
notifier.send_error_notification(
    error_message='Database connection failed',
    module='data_cleaner'
)
```

###### `send_completion_notification(module: str, summary: str, report_path: str = None) -> bool`

Send completion notification.

```python
notifier.send_completion_notification(
    module='data_cleaner',
    summary='Processed 100 files successfully',
    report_path='reports/summary.html'
)
```

---

## Data Models

**Module**: `src.models.data_models`

### `DataQualityReport`

Report of data quality metrics.

**Attributes**:
- `file_name` (str): Name of processed file
- `total_rows` (int): Total number of rows
- `total_columns` (int): Total number of columns
- `issues_found` (List[Dict]): List of data quality issues
- `duplicates_removed` (int): Number of duplicates removed
- `missing_values_handled` (int): Number of missing values handled
- `outliers_detected` (int): Number of outliers detected
- `data_types_validated` (int): Number of columns validated
- `processing_time` (float): Processing time in seconds
- `timestamp` (datetime): Report generation timestamp
- `status` (str): Processing status

### `SystemHealthReport`

System health monitoring report.

**Attributes**:
- `status` (HealthStatus): Overall health status
- `metrics` (SystemMetrics): Current system metrics
- `alerts` (List[str]): Critical alerts
- `warnings` (List[str]): Warning messages
- `monitored_processes` (Dict[str, bool]): Process status
- `recommendations` (List[str]): Recommendations
- `timestamp` (datetime): Check timestamp

### `SystemMetrics`

System resource metrics.

**Attributes**:
- `cpu_percent` (float): CPU usage percentage
- `memory_percent` (float): Memory usage percentage
- `disk_percent` (float): Disk usage percentage
- `process_count` (int): Number of processes
- `uptime_seconds` (float): System uptime in seconds
- `timestamp` (datetime): Metrics timestamp

### `AutomationReport`

Overall automation execution report.

**Attributes**:
- `execution_id` (str): Unique execution identifier
- `start_time` (datetime): Execution start time
- `end_time` (datetime): Execution end time
- `duration_seconds` (float): Total duration
- `modules_executed` (List[str]): List of executed modules
- `success` (bool): Overall success status
- `errors` (List[str]): List of errors
- `data_quality_reports` (List[DataQualityReport]): Quality reports
- `system_health_report` (SystemHealthReport): Health report
- `summary` (Dict): Execution summary

### `ValidationResult`

Result of data validation.

**Attributes**:
- `is_valid` (bool): Validation status
- `errors` (List[str]): Validation errors
- `warnings` (List[str]): Validation warnings
- `metadata` (Dict): Additional metadata
- `timestamp` (datetime): Validation timestamp

### Enums

#### `HealthStatus`

System health status levels.

```python
from src.models.data_models import HealthStatus

HealthStatus.HEALTHY    # System operating normally
HealthStatus.WARNING    # Minor issues detected
HealthStatus.CRITICAL   # Critical issues require attention
HealthStatus.UNKNOWN    # Status cannot be determined
```

#### `CleaningAction`

Data cleaning actions.

```python
from src.models.data_models import CleaningAction

CleaningAction.REMOVE_DUPLICATES    # Remove duplicate rows
CleaningAction.FILL_MISSING         # Fill missing values
CleaningAction.DROP_MISSING         # Drop rows with missing values
CleaningAction.REMOVE_OUTLIERS      # Remove outlier values
CleaningAction.STANDARDIZE_FORMAT   # Standardize data format
CleaningAction.VALIDATE_TYPE        # Validate data types
```

---

## Complete Example

```python
from src.config.logging_config import setup_logging
from src.automation.data_cleaner import DataCleaner
from src.automation.report_generator import ReportGenerator
from src.automation.system_health_checker import SystemHealthChecker
from src.utils.email_notifier import EmailNotifier

# Setup logging
setup_logging(log_level='INFO')

# Clean data
cleaner = DataCleaner()
data_reports = cleaner.clean_directory('data/input', 'data/output')

# Generate report
generator = ReportGenerator()
report_path = generator.generate_data_quality_report(
    data_reports,
    output_format='html'
)

# Check system health
checker = SystemHealthChecker()
health_report = checker.check_health()

# Send notification
notifier = EmailNotifier()
if health_report.status == 'healthy':
    notifier.send_completion_notification(
        module='automation',
        summary=f'Processed {len(data_reports)} files successfully',
        report_path=report_path
    )
else:
    notifier.send_error_notification(
        error_message=f'System status: {health_report.status}',
        module='health_check'
    )
```

---

## Error Handling

All modules raise standard Python exceptions:

- `FileNotFoundError`: File or directory not found
- `ValueError`: Invalid parameter or configuration
- `IOError`: File I/O operation failed
- `ConnectionError`: Network or SMTP connection failed
- `RuntimeError`: Runtime operation failed

**Best Practice**:

```python
from src.automation.data_cleaner import DataCleaner
import logging

logger = logging.getLogger(__name__)

try:
    cleaner = DataCleaner()
    report = cleaner.clean_file('data/input/sales.csv')
    logger.info(f"Cleaning completed: {report.status}")
except FileNotFoundError as e:
    logger.error(f"File not found: {e}")
except ValueError as e:
    logger.error(f"Invalid configuration: {e}")
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
```

---

## Version Information

**Current Version**: 1.0.0

**Python Compatibility**: 3.8+

**Dependencies**: See `requirements.txt`

---

For more information, see:
- [User Guide](user_guide.md)
- [Architecture Documentation](architecture.md)
- [Contributing Guidelines](../CONTRIBUTING.md)