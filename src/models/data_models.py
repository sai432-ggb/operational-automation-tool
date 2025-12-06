"""
Data models and schemas for the automation tool.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CleaningAction(str, Enum):
    """Enumeration of data cleaning actions."""
    REMOVE_DUPLICATES = "remove_duplicates"
    FILL_MISSING = "fill_missing"
    DROP_MISSING = "drop_missing"
    REMOVE_OUTLIERS = "remove_outliers"
    STANDARDIZE_FORMAT = "standardize_format"
    VALIDATE_TYPE = "validate_type"


class DataIssueType(str, Enum):
    """Types of data quality issues."""
    DUPLICATE = "duplicate"
    MISSING_VALUE = "missing_value"
    OUTLIER = "outlier"
    INVALID_TYPE = "invalid_type"
    INVALID_FORMAT = "invalid_format"
    INCONSISTENT_DATA = "inconsistent_data"


class HealthStatus(str, Enum):
    """System health status levels."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class CleaningRule:
    """Data cleaning rule configuration."""
    name: str
    action: CleaningAction
    column: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    priority: int = 0
    
    def __post_init__(self):
        """Validate the rule after initialization."""
        if isinstance(self.action, str):
            self.action = CleaningAction(self.action)


@dataclass
class DataIssue:
    """Represents a data quality issue."""
    issue_type: DataIssueType
    column: str
    row_index: Optional[int] = None
    description: str = ""
    severity: str = "medium"
    value: Optional[Any] = None
    
    def __post_init__(self):
        """Validate issue after initialization."""
        if isinstance(self.issue_type, str):
            self.issue_type = DataIssueType(self.issue_type)


class ValidationResult(BaseModel):
    """Result of data validation."""
    is_valid: bool = Field(default=True)
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)


class DataQualityReport(BaseModel):
    """Comprehensive data quality report."""
    file_name: str
    total_rows: int
    total_columns: int
    issues_found: List[Dict[str, Any]] = Field(default_factory=list)
    duplicates_removed: int = 0
    missing_values_handled: int = 0
    outliers_detected: int = 0
    data_types_validated: int = 0
    processing_time: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.now)
    status: str = "completed"
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SystemMetrics(BaseModel):
    """System resource metrics."""
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    process_count: int
    uptime_seconds: float
    timestamp: datetime = Field(default_factory=datetime.now)


class SystemHealthReport(BaseModel):
    """System health monitoring report."""
    status: HealthStatus
    metrics: SystemMetrics
    alerts: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    monitored_processes: Dict[str, bool] = Field(default_factory=dict)
    recommendations: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True


class AutomationReport(BaseModel):
    """Overall automation execution report."""
    execution_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0
    modules_executed: List[str] = Field(default_factory=list)
    success: bool = True
    errors: List[str] = Field(default_factory=list)
    data_quality_reports: List[DataQualityReport] = Field(default_factory=list)
    system_health_report: Optional[SystemHealthReport] = None
    summary: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }