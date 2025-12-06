"""
Data cleaning and preparation module.
"""

import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np

from ..config.settings import get_settings
from ..models.data_models import (
    DataQualityReport,
    DataIssue,
    DataIssueType,
    CleaningAction
)
from ..utils.file_handler import FileHandler
from ..utils.validators import DataValidator

logger = logging.getLogger(__name__)


class DataCleaner:
    """
    Automated data cleaning and quality improvement.
    
    Features:
    - Remove duplicate rows
    - Handle missing values
    - Detect and handle outliers
    - Standardize data formats
    - Validate data types
    """
    
    def __init__(self):
        """Initialize the data cleaner."""
        self.settings = get_settings()
        self.config = self.settings.data_cleaner
        self.file_handler = FileHandler()
        self.validator = DataValidator()
        self.reports: List[DataQualityReport] = []
    
    def clean_file(self, file_path: str, output_path: Optional[str] = None) -> DataQualityReport:
        """
        Clean a single data file.
        
        Args:
            file_path: Path to input file
            output_path: Path for cleaned output file
        
        Returns:
            DataQualityReport with cleaning results
        """
        start_time = time.time()
        logger.info(f"Starting data cleaning for: {file_path}")
        
        # Read input file
        try:
            df = self.file_handler.read_file(file_path)
            original_rows = len(df)
            original_cols = len(df.columns)
            
            logger.info(f"Loaded {original_rows} rows and {original_cols} columns")
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {str(e)}")
            raise
        
        # Initialize report
        report = DataQualityReport(
            file_name=Path(file_path).name,
            total_rows=original_rows,
            total_columns=original_cols,
        )
        
        # Perform cleaning operations
        try:
            if self.config.remove_duplicates:
                df, dup_count = self._remove_duplicates(df)
                report.duplicates_removed = dup_count
            
            if self.config.validate_data_types:
                df, type_issues = self._validate_types(df)
                report.data_types_validated = len(type_issues)
                report.issues_found.extend(type_issues)
            
            if self.config.handle_missing_values:
                df, missing_count = self._handle_missing_values(df)
                report.missing_values_handled = missing_count
            
            if self.config.outlier_detection:
                df, outlier_count = self._detect_and_handle_outliers(df)
                report.outliers_detected = outlier_count
            
            # Additional standardization
            df = self._standardize_data(df)
            
        except Exception as e:
            logger.error(f"Error during cleaning: {str(e)}")
            report.status = "failed"
            raise
        
        # Save cleaned data
        if output_path is None:
            output_dir = Path(self.config.output_path)
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f"cleaned_{Path(file_path).name}"
        
        try:
            self.file_handler.write_file(df, str(output_path))
            logger.info(f"Cleaned data saved to: {output_path}")
        except Exception as e:
            logger.error(f"Failed to write output file: {str(e)}")
            raise
        
        # Finalize report
        processing_time = time.time() - start_time
        report.processing_time = processing_time
        report.status = "completed"
        
        self.reports.append(report)
        
        logger.info(
            f"Cleaning completed in {processing_time:.2f}s. "
            f"Rows: {original_rows} -> {len(df)}, "
            f"Duplicates removed: {report.duplicates_removed}, "
            f"Missing handled: {report.missing_values_handled}, "
            f"Outliers detected: {report.outliers_detected}"
        )
        
        return report
    
    def clean_directory(
        self,
        input_dir: Optional[str] = None,
        output_dir: Optional[str] = None
    ) -> List[DataQualityReport]:
        """
        Clean all files in a directory.
        
        Args:
            input_dir: Input directory path
            output_dir: Output directory path
        
        Returns:
            List of DataQualityReport for each file
        """
        input_path = input_dir or self.config.input_path
        output_path = output_dir or self.config.output_path
        
        logger.info(f"Cleaning files in directory: {input_path}")
        
        # Find all matching files
        files = []
        for pattern in self.config.file_patterns:
            files.extend(self.file_handler.list_files(input_path, pattern))
        
        if not files:
            logger.warning(f"No files found in {input_path}")
            return []
        
        logger.info(f"Found {len(files)} files to clean")
        
        # Clean each file
        reports = []
        for file_path in files:
            try:
                output_file = Path(output_path) / f"cleaned_{file_path.name}"
                report = self.clean_file(str(file_path), str(output_file))
                reports.append(report)
            except Exception as e:
                logger.error(f"Failed to clean {file_path}: {str(e)}")
                continue
        
        logger.info(f"Successfully cleaned {len(reports)} out of {len(files)} files")
        return reports
    
    def _remove_duplicates(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, int]:
        """Remove duplicate rows."""
        original_count = len(df)
        df_clean = df.drop_duplicates()
        duplicates_removed = original_count - len(df_clean)
        
        if duplicates_removed > 0:
            logger.info(f"Removed {duplicates_removed} duplicate rows")
        
        return df_clean, duplicates_removed
    
    def _validate_types(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[Dict]]:
        """Validate and fix data types."""
        issues = []
        
        for col in df.columns:
            # Try to infer better types
            if df[col].dtype == object:
                # Try numeric conversion
                try:
                    numeric_col = pd.to_numeric(df[col], errors='coerce')
                    if numeric_col.notna().sum() > len(df) * 0.8:  # 80% valid
                        df[col] = numeric_col
                        logger.debug(f"Converted {col} to numeric")
                except Exception:
                    pass
                
                # Try datetime conversion
                try:
                    datetime_col = pd.to_datetime(df[col], errors='coerce')
                    if datetime_col.notna().sum() > len(df) * 0.8:
                        df[col] = datetime_col
                        logger.debug(f"Converted {col} to datetime")
                except Exception:
                    pass
        
        return df, issues
    
    def _handle_missing_values(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, int]:
        """Handle missing values based on configuration."""
        missing_count = df.isnull().sum().sum()
        
        if missing_count == 0:
            return df, 0
        
        method = self.config.handle_missing_values.lower()
        
        if method == "drop":
            # Drop rows with any missing values
            df_clean = df.dropna()
            removed = len(df) - len(df_clean)
            logger.info(f"Dropped {removed} rows with missing values")
            return df_clean, missing_count
        
        elif method == "fill":
            # Fill with appropriate values
            df_clean = df.copy()
            for col in df_clean.columns:
                if df_clean[col].isnull().any():
                    if pd.api.types.is_numeric_dtype(df_clean[col]):
                        # Fill numeric with median
                        df_clean[col].fillna(df_clean[col].median(), inplace=True)
                    else:
                        # Fill categorical with mode
                        mode_val = df_clean[col].mode()
                        if len(mode_val) > 0:
                            df_clean[col].fillna(mode_val[0], inplace=True)
            
            logger.info(f"Filled {missing_count} missing values")
            return df_clean, missing_count
        
        elif method == "interpolate":
            # Interpolate numeric columns
            df_clean = df.copy()
            numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
            df_clean[numeric_cols] = df_clean[numeric_cols].interpolate(method='linear')
            
            # Fill remaining non-numeric
            df_clean = df_clean.fillna(method='ffill').fillna(method='bfill')
            
            logger.info(f"Interpolated {missing_count} missing values")
            return df_clean, missing_count
        
        else:
            logger.warning(f"Unknown missing value method: {method}")
            return df, 0
    
    def _detect_and_handle_outliers(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, int]:
        """Detect and handle outliers in numeric columns."""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        total_outliers = 0
        df_clean = df.copy()
        
        for col in numeric_cols:
            outliers = self.validator.detect_outliers(
                df_clean[col],
                method=self.config.outlier_method,
                threshold=1.5 if self.config.outlier_method == "iqr" else 3
            )
            
            outlier_count = outliers.sum()
            if outlier_count > 0:
                logger.info(f"Detected {outlier_count} outliers in column '{col}'")
                
                # Cap outliers at boundaries instead of removing
                if self.config.outlier_method == "iqr":
                    Q1 = df_clean[col].quantile(0.25)
                    Q3 = df_clean[col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    
                    df_clean.loc[outliers, col] = df_clean.loc[outliers, col].clip(
                        lower=lower_bound,
                        upper=upper_bound
                    )
                
                total_outliers += outlier_count
        
        return df_clean, total_outliers
    
    def _standardize_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize data formats."""
        df_clean = df.copy()
        
        # Trim whitespace from string columns
        string_cols = df_clean.select_dtypes(include=['object']).columns
        for col in string_cols:
            if df_clean[col].dtype == object:
                df_clean[col] = df_clean[col].astype(str).str.strip()
        
        # Standardize column names
        df_clean.columns = df_clean.columns.str.strip().str.lower().str.replace(' ', '_')
        
        logger.debug("Data standardization completed")
        return df_clean
    
    def get_summary_report(self) -> Dict:
        """
        Get summary of all cleaning operations.
        
        Returns:
            Dictionary with summary statistics
        """
        if not self.reports:
            return {"message": "No cleaning operations performed yet"}
        
        total_files = len(self.reports)
        total_duplicates = sum(r.duplicates_removed for r in self.reports)
        total_missing = sum(r.missing_values_handled for r in self.reports)
        total_outliers = sum(r.outliers_detected for r in self.reports)
        avg_processing_time = sum(r.processing_time for r in self.reports) / total_files
        
        return {
            "total_files_processed": total_files,
            "total_duplicates_removed": total_duplicates,
            "total_missing_values_handled": total_missing,
            "total_outliers_detected": total_outliers,
            "average_processing_time": round(avg_processing_time, 2),
            "successful_operations": sum(1 for r in self.reports if r.status == "completed"),
        }