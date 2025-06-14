import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import ssl
from typing import Dict, List, Optional
import os
from datetime import datetime
import json

class EmailSender:
    def __init__(self, smtp_server: str = "smtp.gmail.com", smtp_port: int = 587):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = "noreply@expanzagroup.com"
        self.reply_to = "dave@netwit.ca"
        self.sender_password = os.getenv("EMAIL_PASSWORD")
        self.delivery_log = []
    
    def send_email(self, recipient_email: str, subject: str, html_body: str, text_body: str) -> Dict:
        """Send individual email"""
        
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.sender_email
            message["To"] = recipient_email
            message["Reply-To"] = self.reply_to
            
            # Create text and HTML parts
            text_part = MIMEText(text_body, "plain")
            html_part = MIMEText(html_body, "html")
            
            # Add parts
            message.attach(text_part)
            message.attach(html_part)
            
            # Create secure connection and send email
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.sender_email, self.sender_password)
                
                text = message.as_string()
                server.sendmail(self.sender_email, recipient_email, text)
            
            # Log successful delivery
            delivery_result = {
                "email": recipient_email,
                "status": "sent",
                "timestamp": datetime.now().isoformat(),
                "subject": subject
            }
            
            self.delivery_log.append(delivery_result)
            return delivery_result
            
        except Exception as e:
            # Log failed delivery
            delivery_result = {
                "email": recipient_email,
                "status": "failed",
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "subject": subject
            }
            
            self.delivery_log.append(delivery_result)
            return delivery_result
    
    def send_bulk_emails(self, email_data: List[Dict]) -> Dict:
        """Send bulk emails"""
        
        results = {
            "total": len(email_data),
            "sent": 0,
            "failed": 0,
            "details": []
        }
        
        for email_info in email_data:
            result = self.send_email(
                recipient_email=email_info["recipient"],
                subject=email_info["subject"],
                html_body=email_info["html_body"],
                text_body=email_info["text_body"]
            )
            
            results["details"].append(result)
            
            if result["status"] == "sent":
                results["sent"] += 1
            else:
                results["failed"] += 1
        
        return results
    
    def get_delivery_stats(self) -> Dict:
        """Get delivery statistics"""
        total_emails = len(self.delivery_log)
        sent_emails = len([log for log in self.delivery_log if log["status"] == "sent"])
        failed_emails = total_emails - sent_emails
        
        return {
            "total_emails": total_emails,
            "sent_emails": sent_emails,
            "failed_emails": failed_emails,
            "success_rate": (sent_emails / total_emails * 100) if total_emails > 0 else 0,
            "recent_deliveries": self.delivery_log[-10:]  # Last 10 deliveries
        }
    
    def save_delivery_log(self, filename: str = "data/delivery_log.json"):
        """Save delivery log to file"""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w') as f:
            json.dump(self.delivery_log, f, indent=2)