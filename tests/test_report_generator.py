"""
Unit tests for ReportGenerator module.
"""

import pytest
from datetime import datetime
from pathlib import Path

from src.automation.report_generator import ReportGenerator
from src.models.data_models import DataQualityReport


@pytest.fixture
def report_generator():
    """Create ReportGenerator instance."""
    return ReportGenerator()


@pytest.fixture
def sample_quality_reports():
    """Create sample quality reports."""
    return [
        DataQualityReport(
            file_name="test1.csv",
            total_rows=100,
            total_columns=5,
            duplicates_removed=5,
            missing_values_handled=10,
            outliers_detected=3,
            processing_time=1.5,
        ),
        DataQualityReport(
            file_name="test2.csv",
            total_rows=200,
            total_columns=8,
            duplicates_removed=8,
            missing_values_handled=15,
            outliers_detected=6,
            processing_time=2.3,
        ),
    ]


class TestReportGenerator:
    """Test cases for ReportGenerator."""
    
    def test_initialization(self, report_generator):
        """Test ReportGenerator initialization."""
        assert report_generator is not None
        assert report_generator.config is not None
        assert report_generator.output_dir.exists()
    
    def test_compile_data_quality_stats(self, report_generator, sample_quality_reports):
        """Test compilation of quality statistics."""
        stats = report_generator._compile_data_quality_stats(sample_quality_reports)
        
        assert stats['total_files'] == 2
        assert stats['total_rows_processed'] == 300
        assert stats['total_duplicates_removed'] == 13
        assert stats['total_missing_handled'] == 25
        assert stats['total_outliers_detected'] == 9
    
    @pytest.mark.integration
    def test_generate_html_report(self, report_generator, sample_quality_reports, tmp_path):
        """Test HTML report generation."""
        report_generator.output_dir = tmp_path
        
        report_path = report_generator.generate_data_quality_report(
            sample_quality_reports,
            output_format="html"
        )
        
        assert report_path is not None
        assert Path(report_path).exists()
        assert Path(report_path).suffix == ".html"
    
    @pytest.mark.integration
    def test_generate_excel_report(self, report_generator, sample_quality_reports, tmp_path):
        """Test Excel report generation."""
        report_generator.output_dir = tmp_path
        
        report_path = report_generator.generate_data_quality_report(
            sample_quality_reports,
            output_format="excel"
        )
        
        assert report_path is not None
        assert Path(report_path).exists()
        assert Path(report_path).suffix == ".xlsx"