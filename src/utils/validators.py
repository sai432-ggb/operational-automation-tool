"""
Data validation utilities.
"""

import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Union
import pandas as pd
import numpy as np

from ..models.data_models import ValidationResult, DataIssue, DataIssueType

logger = logging.getLogger(__name__)


class DataValidator:
    """Validate data quality and integrity."""
    
    # Common data type mappings
    TYPE_MAPPINGS = {
        "int": [np.int8, np.int16, np.int32, np.int64, int],
        "float": [np.float16, np.float32, np.float64, float],
        "string": [str, object],
        "datetime": [np.datetime64, "datetime64[ns]"],
        "bool": [bool, np.bool_],
    }
    
    def __init__(self):
        """Initialize the validator."""
        self.issues: List[DataIssue] = []
    
    def validate_dataframe(
        self,
        df: pd.DataFrame,
        schema: Optional[Dict[str, str]] = None,
        required_columns: Optional[List[str]] = None,
    ) -> ValidationResult:
        """
        Validate entire DataFrame.
        
        Args:
            df: DataFrame to validate
            schema: Expected column types {column_name: type}
            required_columns: List of required column names
        
        Returns:
            ValidationResult with validation status and issues
        """
        logger.info("Starting DataFrame validation")
        self.issues.clear()
        errors = []
        warnings = []
        
        # Check if DataFrame is empty
        if df.empty:
            errors.append("DataFrame is empty")
            return ValidationResult(
                is_valid=False,
                errors=errors,
                warnings=warnings,
                metadata={"total_rows": 0, "total_columns": 0}
            )
        
        # Validate required columns
        if required_columns:
            missing_cols = set(required_columns) - set(df.columns)
            if missing_cols:
                errors.append(f"Missing required columns: {missing_cols}")
        
        # Validate schema
        if schema:
            for col, expected_type in schema.items():
                if col not in df.columns:
                    warnings.append(f"Schema column '{col}' not found in DataFrame")
                    continue
                
                if not self._check_column_type(df[col], expected_type):
                    errors.append(
                        f"Column '{col}' has invalid type. Expected {expected_type}, "
                        f"got {df[col].dtype}"
                    )
        
        # Check for duplicates
        duplicate_count = df.duplicated().sum()
        if duplicate_count > 0:
            warnings.append(f"Found {duplicate_count} duplicate rows")
            self.issues.append(DataIssue(
                issue_type=DataIssueType.DUPLICATE,
                column="__all__",
                description=f"{duplicate_count} duplicate rows detected"
            ))
        
        # Check for missing values
        missing_summary = self._check_missing_values(df)
        if missing_summary:
            warnings.extend([
                f"Column '{col}' has {count} missing values"
                for col, count in missing_summary.items()
            ])
        
        is_valid = len(errors) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            metadata={
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "duplicate_rows": int(duplicate_count),
                "columns_with_missing": len(missing_summary),
            }
        )
    
    def _check_column_type(self, series: pd.Series, expected_type: str) -> bool:
        """
        Check if column matches expected type.
        
        Args:
            series: Pandas Series to check
            expected_type: Expected type as string
        
        Returns:
            True if type matches, False otherwise
        """
        expected_type = expected_type.lower()
        
        if expected_type not in self.TYPE_MAPPINGS:
            logger.warning(f"Unknown type: {expected_type}")
            return True
        
        dtype = series.dtype
        expected_dtypes = self.TYPE_MAPPINGS[expected_type]
        
        return any(
            dtype == expected or str(dtype) == str(expected)
            for expected in expected_dtypes
        )
    
    def _check_missing_values(self, df: pd.DataFrame) -> Dict[str, int]:
        """
        Check for missing values in DataFrame.
        
        Args:
            df: DataFrame to check
        
        Returns:
            Dictionary of column names and missing value counts
        """
        missing = df.isnull().sum()
        missing_cols = missing[missing > 0].to_dict()
        
        for col, count in missing_cols.items():
            self.issues.append(DataIssue(
                issue_type=DataIssueType.MISSING_VALUE,
                column=col,
                description=f"{count} missing values in column '{col}'"
            ))
        
        return missing_cols
    
    def validate_email(self, email: str) -> bool:
        """
        Validate email address format.
        
        Args:
            email: Email address to validate
        
        Returns:
            True if valid, False otherwise
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def validate_date_range(
        self,
        date_series: pd.Series,
        min_date: Optional[datetime] = None,
        max_date: Optional[datetime] = None,
    ) -> ValidationResult:
        """
        Validate date range in a Series.
        
        Args:
            date_series: Series containing dates
            min_date: Minimum allowed date
            max_date: Maximum allowed date
        
        Returns:
            ValidationResult
        """
        errors = []
        warnings = []
        
        try:
            dates = pd.to_datetime(date_series, errors='coerce')
            invalid_dates = dates.isna().sum()
            
            if invalid_dates > 0:
                errors.append(f"{invalid_dates} invalid date values found")
            
            if min_date:
                below_min = (dates < pd.Timestamp(min_date)).sum()
                if below_min > 0:
                    errors.append(f"{below_min} dates before minimum date {min_date}")
            
            if max_date:
                above_max = (dates > pd.Timestamp(max_date)).sum()
                if above_max > 0:
                    errors.append(f"{above_max} dates after maximum date {max_date}")
            
        except Exception as e:
            errors.append(f"Error validating dates: {str(e)}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def validate_numeric_range(
        self,
        series: pd.Series,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
    ) -> ValidationResult:
        """
        Validate numeric values are within range.
        
        Args:
            series: Series to validate
            min_value: Minimum allowed value
            max_value: Maximum allowed value
        
        Returns:
            ValidationResult
        """
        errors = []
        warnings = []
        
        if not pd.api.types.is_numeric_dtype(series):
            errors.append("Series is not numeric")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)
        
        if min_value is not None:
            below_min = (series < min_value).sum()
            if below_min > 0:
                errors.append(f"{below_min} values below minimum {min_value}")
        
        if max_value is not None:
            above_max = (series > max_value).sum()
            if above_max > 0:
                errors.append(f"{above_max} values above maximum {max_value}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def detect_outliers(
        self,
        series: pd.Series,
        method: str = "iqr",
        threshold: float = 1.5
    ) -> pd.Series:
        """
        Detect outliers in numeric series.
        
        Args:
            series: Numeric series to check
            method: Detection method ('iqr' or 'zscore')
            threshold: Threshold for outlier detection
        
        Returns:
            Boolean series marking outliers
        """
        if not pd.api.types.is_numeric_dtype(series):
            logger.warning(f"Cannot detect outliers in non-numeric series")
            return pd.Series([False] * len(series))
        
        if method == "iqr":
            Q1 = series.quantile(0.25)
            Q3 = series.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - threshold * IQR
            upper_bound = Q3 + threshold * IQR
            outliers = (series < lower_bound) | (series > upper_bound)
        
        elif method == "zscore":
            mean = series.mean()
            std = series.std()
            z_scores = np.abs((series - mean) / std)
            outliers = z_scores > threshold
        
        else:
            raise ValueError(f"Unknown outlier detection method: {method}")
        
        outlier_count = outliers.sum()
        if outlier_count > 0:
            logger.info(f"Detected {outlier_count} outliers using {method} method")
        
        return outliers
    
    def get_issues(self) -> List[DataIssue]:
        """Get list of all detected issues."""
        return self.issues