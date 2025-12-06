"""
Email notification utilities.
"""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from pathlib import Path
from typing import List, Optional, Union
from datetime import datetime

from ..config.settings import get_settings

logger = logging.getLogger(__name__)


class EmailNotifier:
    """Handle email notifications for automation events."""
    
    def __init__(self):
        """Initialize email notifier with settings."""
        self.settings = get_settings()
        self.email_config = self.settings.email_notifications
        self.smtp_config = self.email_config.smtp
        
    def send_notification(
        self,
        subject: str,
        body: str,
        recipients: Optional[List[str]] = None,
        attachments: Optional[List[str]] = None,
        html: bool = False,
    ) -> bool:
        """
        Send email notification.
        
        Args:
            subject: Email subject
            body: Email body
            recipients: List of recipient emails (uses config if not provided)
            attachments: List of file paths to attach
            html: Whether body is HTML
        
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.email_config.enabled:
            logger.info("Email notifications are disabled")
            return False
        
        recipients = recipients or self.email_config.recipients
        
        if not recipients:
            logger.warning("No recipients configured for email notification")
            return False
        
        try:
            msg = self._create_message(subject, body, recipients, html)
            
            if attachments:
                for attachment_path in attachments:
                    self._attach_file(msg, attachment_path)
            
            self._send_email(msg, recipients)
            logger.info(f"Email sent successfully to {recipients}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False
    
    def _create_message(
        self,
        subject: str,
        body: str,
        recipients: List[str],
        html: bool
    ) -> MIMEMultipart:
        """Create email message."""
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = self.smtp_config.user or "automation@example.com"
        msg['To'] = ', '.join(recipients)
        msg['Date'] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")
        
        # Add body
        content_type = 'html' if html else 'plain'
        msg.attach(MIMEText(body, content_type))
        
        return msg
    
    def _attach_file(self, msg: MIMEMultipart, file_path: str) -> None:
        """Attach file to email message."""
        path = Path(file_path)
        
        if not path.exists():
            logger.warning(f"Attachment not found: {file_path}")
            return
        
        try:
            with open(path, 'rb') as f:
                attachment = MIMEApplication(f.read(), Name=path.name)
            
            attachment['Content-Disposition'] = f'attachment; filename="{path.name}"'
            msg.attach(attachment)
            logger.debug(f"Attached file: {path.name}")
            
        except Exception as e:
            logger.error(f"Failed to attach file {file_path}: {str(e)}")
    
    def _send_email(self, msg: MIMEMultipart, recipients: List[str]) -> None:
        """Send email via SMTP."""
        try:
            with smtplib.SMTP(self.smtp_config.host, self.smtp_config.port) as server:
                if self.smtp_config.use_tls:
                    server.starttls()
                
                if self.smtp_config.user and self.smtp_config.password:
                    server.login(self.smtp_config.user, self.smtp_config.password)
                
                server.send_message(msg)
                
        except smtplib.SMTPAuthenticationError:
            logger.error("SMTP authentication failed. Check credentials.")
            raise
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error sending email: {str(e)}")
            raise
    
    def send_error_notification(self, error_message: str, module: str) -> bool:
        """
        Send error notification email.
        
        Args:
            error_message: Error description
            module: Module where error occurred
        
        Returns:
            True if sent successfully
        """
        if "error" not in self.email_config.send_on:
            return False
        
        subject = f"Automation Error in {module}"
        body = f"""
        <html>
        <body>
            <h2>Automation Error</h2>
            <p><strong>Module:</strong> {module}</p>
            <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Error:</strong></p>
            <pre>{error_message}</pre>
        </body>
        </html>
        """
        
        return self.send_notification(subject, body, html=True)
    
    def send_completion_notification(
        self,
        module: str,
        summary: str,
        report_path: Optional[str] = None
    ) -> bool:
        """
        Send completion notification.
        
        Args:
            module: Completed module name
            summary: Execution summary
            report_path: Path to report file to attach
        
        Returns:
            True if sent successfully
        """
        if "completion" not in self.email_config.send_on:
            return False
        
        subject = f"Automation Completed: {module}"
        body = f"""
        <html>
        <body>
            <h2>Automation Completed Successfully</h2>
            <p><strong>Module:</strong> {module}</p>
            <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Summary:</strong></p>
            <pre>{summary}</pre>
        </body>
        </html>
        """
        
        attachments = [report_path] if report_path else None
        return self.send_notification(subject, body, html=True, attachments=attachments)