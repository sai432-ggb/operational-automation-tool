"""
Application settings and configuration management.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field, validator


# Load environment variables
load_dotenv()


class SMTPConfig(BaseModel):
    """SMTP configuration for email notifications."""
    host: str = Field(default="smtp.gmail.com")
    port: int = Field(default=587)
    use_tls: bool = Field(default=True)
    user: Optional[str] = None
    password: Optional[str] = None


class EmailConfig(BaseModel):
    """Email notification configuration."""
    enabled: bool = Field(default=False)
    smtp: SMTPConfig = Field(default_factory=SMTPConfig)
    recipients: List[str] = Field(default_factory=list)
    send_on: List[str] = Field(default_factory=lambda: ["error", "completion"])


class DataCleanerConfig(BaseModel):
    """Data cleaner module configuration."""
    enabled: bool = Field(default=True)
    input_path: str = Field(default="data/input")
    output_path: str = Field(default="data/output/cleaned")
    remove_duplicates: bool = Field(default=True)
    handle_missing_values: str = Field(default="drop")
    validate_data_types: bool = Field(default=True)
    outlier_detection: bool = Field(default=True)
    outlier_method: str = Field(default="iqr")
    file_patterns: List[str] = Field(default_factory=lambda: ["*.csv", "*.xlsx"])


class ReportGeneratorConfig(BaseModel):
    """Report generator configuration."""
    enabled: bool = Field(default=True)
    output_path: str = Field(default="data/output/reports")
    format: str = Field(default="pdf")
    template_path: str = Field(default="templates")
    include_sections: List[str] = Field(
        default_factory=lambda: ["summary", "detailed_analysis", "visualizations"]
    )


class SystemHealthConfig(BaseModel):
    """System health monitoring configuration."""
    enabled: bool = Field(default=True)
    check_interval: int = Field(default=300)
    cpu_threshold: int = Field(default=80)
    memory_threshold: int = Field(default=85)
    disk_threshold: int = Field(default=90)
    monitored_processes: List[str] = Field(default_factory=lambda: ["python"])
    alert_on_failure: bool = Field(default=True)


class LoggingConfig(BaseModel):
    """Logging configuration."""
    level: str = Field(default="INFO")
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_path: str = Field(default="data/logs/app.log")
    max_bytes: int = Field(default=10485760)  # 10MB
    backup_count: int = Field(default=5)


class Settings(BaseModel):
    """Main application settings."""
    app_name: str = Field(default="Operational Automation Tool")
    app_version: str = Field(default="1.0.0")
    environment: str = Field(default="development")
    
    # Module configurations
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    data_cleaner: DataCleanerConfig = Field(default_factory=DataCleanerConfig)
    report_generator: ReportGeneratorConfig = Field(default_factory=ReportGeneratorConfig)
    system_health: SystemHealthConfig = Field(default_factory=SystemHealthConfig)
    email_notifications: EmailConfig = Field(default_factory=EmailConfig)
    
    # Paths
    base_path: Path = Field(default_factory=lambda: Path.cwd())
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True
    
    @validator("environment")
    def validate_environment(cls, v: str) -> str:
        """Validate environment setting."""
        allowed = ["development", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"Environment must be one of {allowed}")
        return v
    
    def update_from_env(self) -> None:
        """Update settings from environment variables."""
        # Update email config from env
        smtp_host = os.getenv("SMTP_HOST")
        if smtp_host:
            self.email_notifications.smtp.host = smtp_host
        
        smtp_port = os.getenv("SMTP_PORT")
        if smtp_port:
            self.email_notifications.smtp.port = int(smtp_port)
        
        smtp_user = os.getenv("SMTP_USER")
        if smtp_user:
            self.email_notifications.smtp.user = smtp_user
        
        smtp_password = os.getenv("SMTP_PASSWORD")
        if smtp_password:
            self.email_notifications.smtp.password = smtp_password
        
        # Update paths from env
        input_path = os.getenv("INPUT_DATA_PATH")
        if input_path:
            self.data_cleaner.input_path = input_path
        
        output_path = os.getenv("OUTPUT_DATA_PATH")
        if output_path:
            self.data_cleaner.output_path = f"{output_path}/cleaned"
            self.report_generator.output_path = f"{output_path}/reports"
        
        # Update logging from env
        log_level = os.getenv("LOG_LEVEL")
        if log_level:
            self.logging.level = log_level
        
        log_file = os.getenv("LOG_FILE_PATH")
        if log_file:
            self.logging.file_path = log_file
    
    @classmethod
    def from_yaml(cls, yaml_path: str) -> "Settings":
        """Load settings from YAML file."""
        yaml_file = Path(yaml_path)
        if not yaml_file.exists():
            print(f"Config file not found: {yaml_path}, using defaults")
            settings = cls()
            settings.update_from_env()
            return settings
        
        with open(yaml_file, "r", encoding="utf-8") as f:
            config_data = yaml.safe_load(f)
        
        # Parse nested configuration
        settings_dict = {}
        
        if "application" in config_data:
            app_config = config_data["application"]
            settings_dict["app_name"] = app_config.get("name", "Operational Automation Tool")
            settings_dict["app_version"] = app_config.get("version", "1.0.0")
            settings_dict["environment"] = app_config.get("environment", "development")
        
        if "logging" in config_data:
            settings_dict["logging"] = LoggingConfig(**config_data["logging"])
        
        if "data_cleaner" in config_data:
            dc_config = config_data["data_cleaner"]
            rules = dc_config.get("rules", {})
            settings_dict["data_cleaner"] = DataCleanerConfig(
                enabled=dc_config.get("enabled", True),
                input_path=dc_config.get("input_path", "data/input"),
                output_path=dc_config.get("output_path", "data/output/cleaned"),
                remove_duplicates=rules.get("remove_duplicates", True),
                handle_missing_values=rules.get("handle_missing_values", "drop"),
                validate_data_types=rules.get("validate_data_types", True),
                outlier_detection=rules.get("outlier_detection", True),
                outlier_method=rules.get("outlier_method", "iqr"),
                file_patterns=dc_config.get("file_patterns", ["*.csv", "*.xlsx"]),
            )
        
        if "report_generator" in config_data:
            settings_dict["report_generator"] = ReportGeneratorConfig(
                **config_data["report_generator"]
            )
        
        if "system_health" in config_data:
            sh_config = config_data["system_health"]
            thresholds = sh_config.get("thresholds", {})
            settings_dict["system_health"] = SystemHealthConfig(
                enabled=sh_config.get("enabled", True),
                check_interval=sh_config.get("check_interval", 300),
                cpu_threshold=thresholds.get("cpu_percent", 80),
                memory_threshold=thresholds.get("memory_percent", 85),
                disk_threshold=thresholds.get("disk_percent", 90),
                monitored_processes=sh_config.get("monitored_processes", ["python"]),
                alert_on_failure=sh_config.get("alert_on_failure", True),
            )
        
        if "email_notifications" in config_data:
            email_config = config_data["email_notifications"]
            smtp_config = email_config.get("smtp", {})
            settings_dict["email_notifications"] = EmailConfig(
                enabled=email_config.get("enabled", False),
                smtp=SMTPConfig(**smtp_config) if smtp_config else SMTPConfig(),
                recipients=email_config.get("recipients", []),
                send_on=email_config.get("send_on", ["error", "completion"]),
            )
        
        settings = cls(**settings_dict)
        settings.update_from_env()
        return settings


# Global settings instance
_settings: Optional[Settings] = None


def get_settings(config_path: str = "config/config.yaml") -> Settings:
    """Get or create settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings.from_yaml(config_path)
    return _settings