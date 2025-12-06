"""
Automated report generation module.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import json

import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns

from ..config.settings import get_settings
from ..models.data_models import DataQualityReport, AutomationReport
from ..utils.file_handler import FileHandler

logger = logging.getLogger(__name__)

# Set style for better-looking plots
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)


class ReportGenerator:
    """
    Generate comprehensive automation reports with visualizations.
    
    Features:
    - Data quality summaries
    - Statistical analysis
    - Visualizations
    - PDF/HTML/Excel export
    """
    
    def __init__(self):
        """Initialize the report generator."""
        self.settings = get_settings()
        self.config = self.settings.report_generator
        self.file_handler = FileHandler()
        
        # Create output directory
        self.output_dir = Path(self.config.output_path)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_data_quality_report(
        self,
        data_reports: List[DataQualityReport],
        output_format: str = "html"
    ) -> str:
        """
        Generate data quality report from cleaning results.
        
        Args:
            data_reports: List of DataQualityReport objects
            output_format: Output format (html, pdf, excel)
        
        Returns:
            Path to generated report
        """
        logger.info("Generating data quality report")
        
        if not data_reports:
            logger.warning("No data reports provided")
            return ""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_name = f"data_quality_report_{timestamp}"
        
        # Create report content
        report_data = self._compile_data_quality_stats(data_reports)
        
        # Generate visualizations
        viz_paths = self._create_visualizations(report_data, report_name)
        
        # Generate report based on format
        if output_format.lower() == "html":
            report_path = self._generate_html_report(report_data, viz_paths, report_name)
        elif output_format.lower() == "pdf":
            report_path = self._generate_pdf_report(report_data, viz_paths, report_name)
        elif output_format.lower() == "excel":
            report_path = self._generate_excel_report(report_data, report_name)
        else:
            logger.warning(f"Unknown format {output_format}, defaulting to HTML")
            report_path = self._generate_html_report(report_data, viz_paths, report_name)
        
        logger.info(f"Report generated: {report_path}")
        return str(report_path)
    
    def generate_automation_report(
        self,
        automation_report: AutomationReport,
        output_format: str = "html"
    ) -> str:
        """
        Generate comprehensive automation execution report.
        
        Args:
            automation_report: AutomationReport object
            output_format: Output format
        
        Returns:
            Path to generated report
        """
        logger.info("Generating automation execution report")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_name = f"automation_report_{timestamp}"
        
        # Compile report content
        report_content = self._compile_automation_content(automation_report)
        
        # Generate based on format
        if output_format.lower() == "html":
            report_path = self._generate_automation_html(report_content, report_name)
        elif output_format.lower() == "json":
            report_path = self._generate_json_report(automation_report, report_name)
        else:
            report_path = self._generate_automation_html(report_content, report_name)
        
        logger.info(f"Automation report generated: {report_path}")
        return str(report_path)
    
    def _compile_data_quality_stats(
        self,
        reports: List[DataQualityReport]
    ) -> Dict[str, Any]:
        """Compile statistics from multiple data quality reports."""
        stats = {
            "total_files": len(reports),
            "total_rows_processed": sum(r.total_rows for r in reports),
            "total_duplicates_removed": sum(r.duplicates_removed for r in reports),
            "total_missing_handled": sum(r.missing_values_handled for r in reports),
            "total_outliers_detected": sum(r.outliers_detected for r in reports),
            "total_processing_time": sum(r.processing_time for r in reports),
            "avg_processing_time": sum(r.processing_time for r in reports) / len(reports),
            "files_by_status": {},
            "reports": reports,
        }
        
        # Count by status
        for report in reports:
            status = report.status
            stats["files_by_status"][status] = stats["files_by_status"].get(status, 0) + 1
        
        return stats
    
    def _create_visualizations(
        self,
        report_data: Dict[str, Any],
        report_name: str
    ) -> Dict[str, str]:
        """Create visualization charts for the report."""
        viz_dir = self.output_dir / "visualizations"
        viz_dir.mkdir(parents=True, exist_ok=True)
        
        viz_paths = {}
        
        try:
            # 1. Processing time by file
            fig, ax = plt.subplots(figsize=(12, 6))
            reports = report_data["reports"]
            file_names = [r.file_name for r in reports]
            times = [r.processing_time for r in reports]
            
            ax.barh(file_names, times, color='steelblue')
            ax.set_xlabel('Processing Time (seconds)')
            ax.set_title('Processing Time by File')
            ax.grid(axis='x', alpha=0.3)
            plt.tight_layout()
            
            path = viz_dir / f"{report_name}_processing_time.png"
            plt.savefig(path, dpi=300, bbox_inches='tight')
            viz_paths["processing_time"] = str(path)
            plt.close()
            
            # 2. Data quality metrics
            fig, axes = plt.subplots(2, 2, figsize=(14, 10))
            
            # Duplicates
            duplicates = [r.duplicates_removed for r in reports]
            axes[0, 0].bar(file_names, duplicates, color='coral')
            axes[0, 0].set_title('Duplicates Removed')
            axes[0, 0].tick_params(axis='x', rotation=45)
            
            # Missing values
            missing = [r.missing_values_handled for r in reports]
            axes[0, 1].bar(file_names, missing, color='lightgreen')
            axes[0, 1].set_title('Missing Values Handled')
            axes[0, 1].tick_params(axis='x', rotation=45)
            
            # Outliers
            outliers = [r.outliers_detected for r in reports]
            axes[1, 0].bar(file_names, outliers, color='gold')
            axes[1, 0].set_title('Outliers Detected')
            axes[1, 0].tick_params(axis='x', rotation=45)
            
            # Summary pie chart
            summary_data = [
                report_data["total_duplicates_removed"],
                report_data["total_missing_handled"],
                report_data["total_outliers_detected"]
            ]
            summary_labels = ['Duplicates', 'Missing Values', 'Outliers']
            axes[1, 1].pie(summary_data, labels=summary_labels, autopct='%1.1f%%',
                          colors=['coral', 'lightgreen', 'gold'])
            axes[1, 1].set_title('Overall Data Quality Issues')
            
            plt.tight_layout()
            path = viz_dir / f"{report_name}_quality_metrics.png"
            plt.savefig(path, dpi=300, bbox_inches='tight')
            viz_paths["quality_metrics"] = str(path)
            plt.close()
            
        except Exception as e:
            logger.error(f"Error creating visualizations: {str(e)}")
        
        return viz_paths
    
    def _generate_html_report(
        self,
        report_data: Dict[str, Any],
        viz_paths: Dict[str, str],
        report_name: str
    ) -> Path:
        """Generate HTML report."""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Data Quality Report</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 40px;
                    background-color: #f5f5f5;
                }}
                .container {{
                    background-color: white;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                h1 {{
                    color: #2c3e50;
                    border-bottom: 3px solid #3498db;
                    padding-bottom: 10px;
                }}
                h2 {{
                    color: #34495e;
                    margin-top: 30px;
                }}
                .stats-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 20px;
                    margin: 20px 0;
                }}
                .stat-card {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 20px;
                    border-radius: 8px;
                    text-align: center;
                }}
                .stat-value {{
                    font-size: 2.5em;
                    font-weight: bold;
                    margin: 10px 0;
                }}
                .stat-label {{
                    font-size: 0.9em;
                    opacity: 0.9;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }}
                th, td {{
                    padding: 12px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }}
                th {{
                    background-color: #3498db;
                    color: white;
                }}
                tr:hover {{
                    background-color: #f5f5f5;
                }}
                .visualization {{
                    margin: 30px 0;
                    text-align: center;
                }}
                .visualization img {{
                    max-width: 100%;
                    border-radius: 8px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                }}
                .timestamp {{
                    color: #7f8c8d;
                    font-style: italic;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Data Quality Report</h1>
                <p class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                
                <h2>Executive Summary</h2>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-label">Files Processed</div>
                        <div class="stat-value">{report_data['total_files']}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Total Rows</div>
                        <div class="stat-value">{report_data['total_rows_processed']:,}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Duplicates Removed</div>
                        <div class="stat-value">{report_data['total_duplicates_removed']}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Missing Values Handled</div>
                        <div class="stat-value">{report_data['total_missing_handled']}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Outliers Detected</div>
                        <div class="stat-value">{report_data['total_outliers_detected']}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Avg Processing Time</div>
                        <div class="stat-value">{report_data['avg_processing_time']:.2f}s</div>
                    </div>
                </div>
                
                <h2>Detailed Results</h2>
                <table>
                    <thead>
                        <tr>
                            <th>File Name</th>
                            <th>Rows</th>
                            <th>Duplicates</th>
                            <th>Missing</th>
                            <th>Outliers</th>
                            <th>Time (s)</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        for report in report_data["reports"]:
            html_content += f"""
                        <tr>
                            <td>{report.file_name}</td>
                            <td>{report.total_rows:,}</td>
                            <td>{report.duplicates_removed}</td>
                            <td>{report.missing_values_handled}</td>
                            <td>{report.outliers_detected}</td>
                            <td>{report.processing_time:.2f}</td>
                            <td>{report.status}</td>
                        </tr>
            """
        
        html_content += """
                    </tbody>
                </table>
                
                <h2>Visualizations</h2>
        """
        
        for viz_name, viz_path in viz_paths.items():
            html_content += f"""
                <div class="visualization">
                    <h3>{viz_name.replace('_', ' ').title()}</h3>
                    <img src="{Path(viz_path).name}" alt="{viz_name}">
                </div>
            """
        
        html_content += """
            </div>
        </body>
        </html>
        """
        
        # Save HTML report
        report_path = self.output_dir / f"{report_name}.html"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return report_path
    
    def _generate_excel_report(
        self,
        report_data: Dict[str, Any],
        report_name: str
    ) -> Path:
        """Generate Excel report."""
        report_path = self.output_dir / f"{report_name}.xlsx"
        
        with pd.ExcelWriter(report_path, engine='openpyxl') as writer:
            # Summary sheet
            summary_df = pd.DataFrame([{
                'Total Files': report_data['total_files'],
                'Total Rows': report_data['total_rows_processed'],
                'Duplicates Removed': report_data['total_duplicates_removed'],
                'Missing Handled': report_data['total_missing_handled'],
                'Outliers Detected': report_data['total_outliers_detected'],
                'Total Time (s)': report_data['total_processing_time'],
                'Avg Time (s)': report_data['avg_processing_time'],
            }])
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Detailed results
            details = []
            for report in report_data['reports']:
                details.append({
                    'File Name': report.file_name,
                    'Total Rows': report.total_rows,
                    'Total Columns': report.total_columns,
                    'Duplicates Removed': report.duplicates_removed,
                    'Missing Handled': report.missing_values_handled,
                    'Outliers Detected': report.outliers_detected,
                    'Processing Time (s)': report.processing_time,
                    'Status': report.status,
                })
            
            details_df = pd.DataFrame(details)
            details_df.to_excel(writer, sheet_name='Detailed Results', index=False)
        
        return report_path
    
    def _generate_pdf_report(
        self,
        report_data: Dict[str, Any],
        viz_paths: Dict[str, str],
        report_name: str
    ) -> Path:
        """Generate PDF report (placeholder - requires reportlab)."""
        logger.warning("PDF generation requires reportlab library")
        # Fallback to HTML
        return self._generate_html_report(report_data, viz_paths, report_name)
    
    def _compile_automation_content(self, report: AutomationReport) -> Dict:
        """Compile automation report content."""
        return {
            "execution_id": report.execution_id,
            "start_time": report.start_time,
            "end_time": report.end_time,
            "duration": report.duration_seconds,
            "modules": report.modules_executed,
            "success": report.success,
            "errors": report.errors,
            "summary": report.summary,
        }
    
    def _generate_automation_html(
        self,
        content: Dict,
        report_name: str
    ) -> Path:
        """Generate HTML automation report."""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Automation Execution Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ background: #3498db; color: white; padding: 20px; }}
                .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; }}
                .success {{ color: green; }}
                .error {{ color: red; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Automation Execution Report</h1>
                <p>Execution ID: {content['execution_id']}</p>
            </div>
            
            <div class="section">
                <h2>Summary</h2>
                <p><strong>Start Time:</strong> {content['start_time']}</p>
                <p><strong>End Time:</strong> {content['end_time']}</p>
                <p><strong>Duration:</strong> {content['duration']:.2f} seconds</p>
                <p><strong>Status:</strong> <span class="{'success' if content['success'] else 'error'}">
                    {'SUCCESS' if content['success'] else 'FAILED'}</span></p>
            </div>
            
            <div class="section">
                <h2>Modules Executed</h2>
                <ul>
                    {''.join(f'<li>{module}</li>' for module in content['modules'])}
                </ul>
            </div>
        </body>
        </html>
        """
        
        report_path = self.output_dir / f"{report_name}.html"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return report_path
    
    def _generate_json_report(
        self,
        report: AutomationReport,
        report_name: str
    ) -> Path:
        """Generate JSON report."""
        report_path = self.output_dir / f"{report_name}.json"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report.dict(), f, indent=2, default=str)
        
        return report_path