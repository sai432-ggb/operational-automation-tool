"""
System health monitoring and reporting module.
"""

import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import psutil

from ..config.settings import get_settings
from ..models.data_models import (
    SystemHealthReport,
    SystemMetrics,
    HealthStatus
)

logger = logging.getLogger(__name__)


class SystemHealthChecker:
    """
    Monitor system health and resource usage.
    
    Features:
    - CPU usage monitoring
    - Memory usage tracking
    - Disk space monitoring
    - Process monitoring
    - Alert generation
    """
    
    def __init__(self):
        """Initialize the system health checker."""
        self.settings = get_settings()
        self.config = self.settings.system_health
        self.boot_time = datetime.fromtimestamp(psutil.boot_time())
        self.reports: List[SystemHealthReport] = []
    
    def check_health(self) -> SystemHealthReport:
        """
        Perform comprehensive system health check.
        
        Returns:
            SystemHealthReport with current system status
        """
        logger.info("Starting system health check")
        
        # Gather metrics
        metrics = self._gather_metrics()
        
        # Determine overall health status
        status, alerts, warnings = self._evaluate_health(metrics)
        
        # Check monitored processes
        process_status = self._check_processes()
        
        # Generate recommendations
        recommendations = self._generate_recommendations(metrics, alerts)
        
        # Create report
        report = SystemHealthReport(
            status=status,
            metrics=metrics,
            alerts=alerts,
            warnings=warnings,
            monitored_processes=process_status,
            recommendations=recommendations,
        )
        
        self.reports.append(report)
        
        logger.info(f"Health check completed - Status: {status}")
        if alerts:
            logger.warning(f"Alerts generated: {len(alerts)}")
        
        return report
    
    def _gather_metrics(self) -> SystemMetrics:
        """Gather current system metrics."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            # Process count
            process_count = len(psutil.pids())
            
            # System uptime
            uptime_seconds = (datetime.now() - self.boot_time).total_seconds()
            
            metrics = SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                disk_percent=disk_percent,
                process_count=process_count,
                uptime_seconds=uptime_seconds,
            )
            
            logger.debug(
                f"Metrics - CPU: {cpu_percent}%, Memory: {memory_percent}%, "
                f"Disk: {disk_percent}%, Processes: {process_count}"
            )
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error gathering metrics: {str(e)}")
            raise
    
    def _evaluate_health(
        self,
        metrics: SystemMetrics
    ) -> Tuple[HealthStatus, List[str], List[str]]:
        """
        Evaluate system health based on metrics.
        
        Returns:
            Tuple of (status, alerts, warnings)
        """
        alerts = []
        warnings = []
        
        # Check CPU usage
        if metrics.cpu_percent >= self.config.cpu_threshold:
            alerts.append(
                f"CPU usage critical: {metrics.cpu_percent:.1f}% "
                f"(threshold: {self.config.cpu_threshold}%)"
            )
        elif metrics.cpu_percent >= self.config.cpu_threshold * 0.8:
            warnings.append(
                f"CPU usage high: {metrics.cpu_percent:.1f}%"
            )
        
        # Check memory usage
        if metrics.memory_percent >= self.config.memory_threshold:
            alerts.append(
                f"Memory usage critical: {metrics.memory_percent:.1f}% "
                f"(threshold: {self.config.memory_threshold}%)"
            )
        elif metrics.memory_percent >= self.config.memory_threshold * 0.8:
            warnings.append(
                f"Memory usage high: {metrics.memory_percent:.1f}%"
            )
        
        # Check disk usage
        if metrics.disk_percent >= self.config.disk_threshold:
            alerts.append(
                f"Disk usage critical: {metrics.disk_percent:.1f}% "
                f"(threshold: {self.config.disk_threshold}%)"
            )
        elif metrics.disk_percent >= self.config.disk_threshold * 0.8:
            warnings.append(
                f"Disk usage high: {metrics.disk_percent:.1f}%"
            )
        
        # Determine overall status
        if alerts:
            status = HealthStatus.CRITICAL
        elif warnings:
            status = HealthStatus.WARNING
        else:
            status = HealthStatus.HEALTHY
        
        return status, alerts, warnings
    
    def _check_processes(self) -> Dict[str, bool]:
        """
        Check if monitored processes are running.
        
        Returns:
            Dictionary mapping process names to running status
        """
        process_status = {}
        
        try:
            # Get all running processes
            running_processes = {
                p.name().lower() for p in psutil.process_iter(['name'])
            }
            
            # Check each monitored process
            for process_name in self.config.monitored_processes:
                is_running = any(
                    process_name.lower() in proc_name
                    for proc_name in running_processes
                )
                process_status[process_name] = is_running
                
                if not is_running:
                    logger.warning(f"Monitored process not running: {process_name}")
            
        except Exception as e:
            logger.error(f"Error checking processes: {str(e)}")
        
        return process_status
    
    def _generate_recommendations(
        self,
        metrics: SystemMetrics,
        alerts: List[str]
    ) -> List[str]:
        """Generate recommendations based on system state."""
        recommendations = []
        
        if metrics.cpu_percent > 70:
            recommendations.append(
                "Consider closing unnecessary applications or processes to reduce CPU load"
            )
        
        if metrics.memory_percent > 70:
            recommendations.append(
                "Memory usage is high. Consider restarting some applications or "
                "increasing available RAM"
            )
        
        if metrics.disk_percent > 80:
            recommendations.append(
                "Disk space is running low. Consider cleaning up old files or "
                "archiving data to external storage"
            )
        
        if not alerts and not recommendations:
            recommendations.append("System is operating normally. No action required.")
        
        return recommendations
    
    def get_detailed_info(self) -> Dict:
        """
        Get detailed system information.
        
        Returns:
            Dictionary with comprehensive system details
        """
        try:
            info = {
                "cpu": {
                    "physical_cores": psutil.cpu_count(logical=False),
                    "logical_cores": psutil.cpu_count(logical=True),
                    "current_usage": psutil.cpu_percent(interval=1),
                    "per_core_usage": psutil.cpu_percent(interval=1, percpu=True),
                },
                "memory": {
                    "total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
                    "available_gb": round(psutil.virtual_memory().available / (1024**3), 2),
                    "used_gb": round(psutil.virtual_memory().used / (1024**3), 2),
                    "percent": psutil.virtual_memory().percent,
                },
                "disk": {
                    "total_gb": round(psutil.disk_usage('/').total / (1024**3), 2),
                    "used_gb": round(psutil.disk_usage('/').used / (1024**3), 2),
                    "free_gb": round(psutil.disk_usage('/').free / (1024**3), 2),
                    "percent": psutil.disk_usage('/').percent,
                },
                "system": {
                    "boot_time": self.boot_time.isoformat(),
                    "uptime_hours": round(
                        (datetime.now() - self.boot_time).total_seconds() / 3600, 2
                    ),
                },
                "processes": {
                    "total": len(psutil.pids()),
                    "monitored": self._check_processes(),
                }
            }
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting detailed info: {str(e)}")
            return {}
    
    def monitor_continuously(
        self,
        duration: int = 300,
        interval: int = 60,
        callback: Optional[callable] = None
    ) -> List[SystemHealthReport]:
        """
        Monitor system health continuously for a specified duration.
        
        Args:
            duration: Total monitoring duration in seconds
            interval: Check interval in seconds
            callback: Optional callback function called after each check
        
        Returns:
            List of SystemHealthReport objects
        """
        logger.info(
            f"Starting continuous monitoring for {duration}s at {interval}s intervals"
        )
        
        reports = []
        start_time = time.time()
        
        while time.time() - start_time < duration:
            try:
                report = self.check_health()
                reports.append(report)
                
                if callback:
                    callback(report)
                
                # Alert if critical
                if report.status == HealthStatus.CRITICAL and self.config.alert_on_failure:
                    logger.critical(f"CRITICAL SYSTEM STATE: {report.alerts}")
                
                time.sleep(interval)
                
            except KeyboardInterrupt:
                logger.info("Monitoring interrupted by user")
                break
            except Exception as e:
                logger.error(f"Error during monitoring: {str(e)}")
                time.sleep(interval)
        
        logger.info(f"Monitoring completed. Generated {len(reports)} reports")
        return reports
    
    def get_summary(self) -> Dict:
        """
        Get summary of all health checks performed.
        
        Returns:
            Dictionary with summary statistics
        """
        if not self.reports:
            return {"message": "No health checks performed yet"}
        
        total_checks = len(self.reports)
        healthy_count = sum(1 for r in self.reports if r.status == HealthStatus.HEALTHY)
        warning_count = sum(1 for r in self.reports if r.status == HealthStatus.WARNING)
        critical_count = sum(1 for r in self.reports if r.status == HealthStatus.CRITICAL)
        
        avg_cpu = sum(r.metrics.cpu_percent for r in self.reports) / total_checks
        avg_memory = sum(r.metrics.memory_percent for r in self.reports) / total_checks
        avg_disk = sum(r.metrics.disk_percent for r in self.reports) / total_checks
        
        return {
            "total_checks": total_checks,
            "healthy": healthy_count,
            "warnings": warning_count,
            "critical": critical_count,
            "average_metrics": {
                "cpu_percent": round(avg_cpu, 2),
                "memory_percent": round(avg_memory, 2),
                "disk_percent": round(avg_disk, 2),
            },
            "latest_status": self.reports[-1].status if self.reports else None,
        }