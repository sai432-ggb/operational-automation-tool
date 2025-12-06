"""
Unit tests for DataCleaner module.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path

from src.automation.data_cleaner import DataCleaner
from src.models.data_models import DataQualityReport


@pytest.fixture
def sample_dataframe():
    """Create sample DataFrame for testing."""
    return pd.DataFrame({
        'id': [1, 2, 2, 3, 4, 5],  # Has duplicate
        'name': ['Alice', 'Bob', 'Bob', np.nan, 'David', 'Eve'],  # Has missing
        'age': [25, 30, 30, 35, 40, 1000],  # Has outlier
        'score': [85.5, 90.0, 90.0, 75.5, 88.0, 92.0]
    })


@pytest.fixture
def cleaner():
    """Create DataCleaner instance."""
    return DataCleaner()


class TestDataCleaner:
    """Test cases for DataCleaner."""
    
    def test_initialization(self, cleaner):
        """Test DataCleaner initialization."""
        assert cleaner is not None
        assert cleaner.config is not None
        assert cleaner.file_handler is not None
    
    def test_remove_duplicates(self, cleaner, sample_dataframe):
        """Test duplicate removal."""
        df_clean, dup_count = cleaner._remove_duplicates(sample_dataframe)
        assert dup_count == 1
        assert len(df_clean) == 5
    
    def test_handle_missing_values_drop(self, cleaner, sample_dataframe):
        """Test missing value handling with drop method."""
        cleaner.config.handle_missing_values = "drop"
        df_clean, missing_count = cleaner._handle_missing_values(sample_dataframe)
        assert missing_count == 1
        assert len(df_clean) == 5  # One row dropped
    
    def test_handle_missing_values_fill(self, cleaner, sample_dataframe):
        """Test missing value handling with fill method."""
        cleaner.config.handle_missing_values = "fill"
        df_clean, missing_count = cleaner._handle_missing_values(sample_dataframe)
        assert missing_count == 1
        assert df_clean['name'].isna().sum() == 0
    
    def test_detect_outliers(self, cleaner, sample_dataframe):
        """Test outlier detection."""
        df_clean, outlier_count = cleaner._detect_and_handle_outliers(sample_dataframe)
        assert outlier_count > 0  # Should detect the 1000 in age column
    
    def test_standardize_data(self, cleaner):
        """Test data standardization."""
        df = pd.DataFrame({
            'First Name': ['  Alice  ', 'Bob'],
            'Last Name': ['Smith  ', '  Jones']
        })
        df_clean = cleaner._standardize_data(df)
        
        # Check column names are standardized
        assert 'first_name' in df_clean.columns
        assert 'last_name' in df_clean.columns
        
        # Check whitespace is trimmed
        assert df_clean['first_name'].iloc[0] == 'Alice'
    
    def test_get_summary_report_empty(self, cleaner):
        """Test summary report with no operations."""
        summary = cleaner.get_summary_report()
        assert "No cleaning operations" in summary["message"]
    
    @pytest.mark.integration
    def test_clean_file_integration(self, cleaner, tmp_path, sample_dataframe):
        """Integration test for cleaning a file."""
        # Create temporary input file
        input_file = tmp_path / "test_input.csv"
        sample_dataframe.to_csv(input_file, index=False)
        
        # Clean the file
        output_file = tmp_path / "test_output.csv"
        report = cleaner.clean_file(str(input_file), str(output_file))
        
        # Verify report
        assert isinstance(report, DataQualityReport)
        assert report.status == "completed"
        assert report.duplicates_removed >= 0
        
        # Verify output file exists
        assert output_file.exists()
        
        # Verify cleaned data
        df_cleaned = pd.read_csv(output_file)
        assert len(df_cleaned) <= len(sample_dataframe)