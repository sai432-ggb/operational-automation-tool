"""
Main entry point for the Operational Automation Tool.
"""

import argparse
import sys
import uuid
from datetime import datetime
from pathlib import Path
import logging

from config.settings import get_settings
from config.logging_config import setup_logging, get_logger
from automation.data_cleaner import DataCleaner
from automation.report_generator import ReportGenerator
from automation.system_health_checker import SystemHealthChecker
from models.data_models import AutomationReport
from utils.email_notifier import EmailNotifier


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Operational Efficiency Automation Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all modules
  python main.py

  # Run specific module
  python main.py --module data_cleaner

  # Clean specific directory
  python main.py --module data_cleaner --input data/raw --output data/processed

  # Generate report with specific format
  python main.py --module report_generator --format pdf

  # Monitor system health continuously
  python main.py --module health_check --monitor-duration 3600
        """
    )
    
    parser.add_argument(
        '--module',
        choices=['all', 'data_cleaner', 'report_generator', 'health_check'],
        default='all',
        help='Module to execute (default: all)'
    )
    
    parser.add_argument(
        '--input',
        type=str,
        help='Input directory for data cleaning'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        help='Output directory for results'
    )
    
    parser.add_argument(
        '--format',
        choices=['html', 'pdf', 'excel', 'json'],
        default='html',
        help='Report output format (default: html)'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='config/config.yaml',
        help='Path to configuration file'
    )
    
    parser.add_argument(
        '--monitor-duration',
        type=int,
        default=300,
        help='Duration for continuous health monitoring in seconds (default: 300)'
    )
    
    parser.add_argument(
        '--monitor-interval',
        type=int,
        default=60,
        help='Interval between health checks in seconds (default: 60)'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='INFO',
        help='Logging level (default: INFO)'
    )
    
    parser.add_argument(
        '--no-email',
        action='store_true',
        help='Disable email notifications'
    )
    
    return parser.parse_args()


def run_data_cleaner(args, logger):
    """Run the data cleaning module."""
    logger.info("=" * 80)
    logger.info("RUNNING DATA CLEANER MODULE")
    logger.info("=" * 80)
    
    try:
        cleaner = DataCleaner()
        
        if args.input and args.output:
            reports = cleaner.clean_directory(args.input, args.output)
        else:
            reports = cleaner.clean_directory()
        
        if reports:
            summary = cleaner.get_summary_report()
            logger.info(f"Data cleaning completed: {summary}")
            return reports, summary
        else:
            logger.warning("No files were processed")
            return [], {}
            
    except Exception as e:
        logger.error(f"Data cleaning failed: {str(e)}", exc_info=True)
        raise


def run_report_generator(args, logger, data_reports=None):
    """Run the report generation module."""
    logger.info("=" * 80)
    logger.info("RUNNING REPORT GENERATOR MODULE")
    logger.info("=" * 80)
    
    try:
        generator = ReportGenerator()
        
        if data_reports:
            report_path = generator.generate_data_quality_report(
                data_reports,
                output_format=args.format
            )
            logger.info(f"Data quality report generated: {report_path}")
            return report_path
        else:
            logger.info("No data reports available to generate report from")
            return None
            
    except Exception as e:
        logger.error(f"Report generation failed: {str(e)}", exc_info=True)
        raise


def run_health_checker(args, logger):
    """Run the system health checker module."""
    logger.info("=" * 80)
    logger.info("RUNNING SYSTEM HEALTH CHECKER MODULE")
    logger.info("=" * 80)
    
    try:
        checker = SystemHealthChecker()
        
        # Get detailed system info
        detailed_info = checker.get_detailed_info()
        logger.info("System Information:")
        for category, info in detailed_info.items():
            logger.info(f"  {category.upper()}: {info}")
        
        # Single health check
        health_report = checker.check_health()
        logger.info(f"System Status: {health_report.status}")
        
        if health_report.alerts:
            logger.warning("ALERTS:")
            for alert in health_report.alerts:
                logger.warning(f"  - {alert}")
        
        if health_report.warnings:
            logger.warning("WARNINGS:")
            for warning in health_report.warnings:
                logger.warning(f"  - {warning}")
        
        if health_report.recommendations:
            logger.info("RECOMMENDATIONS:")
            for rec in health_report.recommendations:
                logger.info(f"  - {rec}")
        
        return health_report
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}", exc_info=True)
        raise


def send_notifications(automation_report, args, logger):
    """Send email notifications if enabled."""
    if args.no_email:
        logger.info("Email notifications disabled")
        return
    
    try:
        notifier = EmailNotifier()
        
        if not automation_report.success:
            # Send error notification
            error_msg = "\n".join(automation_report.errors)
            notifier.send_error_notification(error_msg, "Automation Tool")
        else:
            # Send completion notification
            summary = f"""
            Execution ID: {automation_report.execution_id}
            Duration: {automation_report.duration_seconds:.2f} seconds
            Modules: {', '.join(automation_report.modules_executed)}
            Status: SUCCESS
            """
            notifier.send_completion_notification(
                "Automation Tool",
                summary
            )
        
    except Exception as e:
        logger.error(f"Failed to send notifications: {str(e)}")


def main():
    """Main execution function."""
    # Parse arguments
    args = parse_arguments()
    
    # Setup logging
    setup_logging(log_level=args.log_level)
    logger = get_logger(__name__)
    
    logger.info("=" * 80)
    logger.info("OPERATIONAL AUTOMATION TOOL - STARTING")
    logger.info("=" * 80)
    
    # Load settings
    settings = get_settings(args.config)
    logger.info(f"Configuration loaded from: {args.config}")
    logger.info(f"Environment: {settings.environment}")
    
    # Initialize automation report
    execution_id = str(uuid.uuid4())[:8]
    start_time = datetime.now()
    
    automation_report = AutomationReport(
        execution_id=execution_id,
        start_time=start_time,
    )
    
    data_reports = []
    report_path = None
    health_report = None
    
    try:
        # Execute modules based on selection
        if args.module in ['all', 'data_cleaner']:
            try:
                data_reports, summary = run_data_cleaner(args, logger)
                automation_report.modules_executed.append('data_cleaner')
                automation_report.summary['data_cleaner'] = summary
            except Exception as e:
                automation_report.errors.append(f"Data cleaner error: {str(e)}")
                automation_report.success = False
        
        if args.module in ['all', 'report_generator']:
            try:
                report_path = run_report_generator(args, logger, data_reports)
                automation_report.modules_executed.append('report_generator')
                if report_path:
                    automation_report.summary['report_path'] = report_path
            except Exception as e:
                automation_report.errors.append(f"Report generator error: {str(e)}")
                automation_report.success = False
        
        if args.module in ['all', 'health_check']:
            try:
                health_report = run_health_checker(args, logger)
                automation_report.modules_executed.append('health_check')
                automation_report.system_health_report = health_report
            except Exception as e:
                automation_report.errors.append(f"Health checker error: {str(e)}")
                automation_report.success = False
        
    except KeyboardInterrupt:
        logger.warning("Execution interrupted by user")
        automation_report.success = False
        automation_report.errors.append("Interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        automation_report.success = False
        automation_report.errors.append(f"Unexpected error: {str(e)}")
    
    # Finalize report
    automation_report.end_time = datetime.now()
    automation_report.duration_seconds = (
        automation_report.end_time - automation_report.start_time
    ).total_seconds()
    
    # Log summary
    logger.info("=" * 80)
    logger.info("EXECUTION SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Execution ID: {execution_id}")
    logger.info(f"Duration: {automation_report.duration_seconds:.2f} seconds")
    logger.info(f"Modules Executed: {', '.join(automation_report.modules_executed)}")
    logger.info(f"Status: {'SUCCESS' if automation_report.success else 'FAILED'}")
    
    if automation_report.errors:
        logger.error("ERRORS:")
        for error in automation_report.errors:
            logger.error(f"  - {error}")
    
    # Send notifications
    send_notifications(automation_report, args, logger)
    
    # Generate final automation report
    if automation_report.success and report_path is None:
        try:
            generator = ReportGenerator()
            final_report = generator.generate_automation_report(
                automation_report,
                output_format='json'
            )
            logger.info(f"Final automation report: {final_report}")
        except Exception as e:
            logger.error(f"Failed to generate final report: {str(e)}")
    
    logger.info("=" * 80)
    logger.info("OPERATIONAL AUTOMATION TOOL - COMPLETED")
    logger.info("=" * 80)
    
    # Exit with appropriate code
    sys.exit(0 if automation_report.success else 1)


if __name__ == "__main__":
    main(