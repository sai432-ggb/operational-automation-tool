"""
Unit tests for SystemHealthChecker module.
"""

import pytest
from src.automation.system_health_checker import SystemHealthChecker
from src.models.data_models import HealthStatus


@pytest.fixture
def health_checker():
    """Create SystemHealthChecker instance."""
    return SystemHealthChecker()


class TestSystemHealthChecker:
    """Test cases for SystemHealthChecker."""
    
    def test_initialization(self, health_checker):
        """Test SystemHealthChecker initialization."""
        assert health_checker is not None
        assert health_checker.config is not None
    
    def test_gather_metrics(self, health_checker):
        """Test metrics gathering."""
        metrics = health_checker._gather_metrics()
        
        assert metrics is not None
        assert 0 <= metrics.cpu_percent <= 100
        assert 0 <= metrics.memory_percent <= 100
        assert 0 <= metrics.disk_percent <= 100
        assert metrics.process_count > 0
    
    def test_check_health(self, health_checker):
        """Test health check execution."""
        report = health_checker.check_health()
        
        assert report is not None
        assert isinstance(report.status, HealthStatus)
        assert report.metrics is not None
    
    def test_get_detailed_info(self, health_checker):
        """Test detailed system info."""
        info = health_checker.get_detailed_info()
        
        assert 'cpu' in info
        assert 'memory' in info
        assert 'disk' in info
        assert 'system' in info
    
    def test_get_summary_empty(self, health_checker):
        """Test summary with no checks performed."""
        summary = health_checker.get_summary()
        assert "No health checks performed" in summary["message"]