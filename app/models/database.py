import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from contextlib import contextmanager

class DatabaseManager:
    def __init__(self, db_path: str = "data/email_automation.db"):
        self.db_path = db_path
        self.ensure_data_directory()
        self.init_database()
    
    def ensure_data_directory(self):
        """Ensure data directory exists"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        try:
            yield conn
        finally:
            conn.close()
    
    def init_database(self):
        """Initialize database with all required tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create contacts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS contacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email_address TEXT UNIQUE NOT NULL,
                    first_name TEXT,
                    last_name TEXT,
                    full_name TEXT,
                    domain TEXT,
                    company_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create website_analysis table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS website_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contact_id INTEGER,
                    domain TEXT NOT NULL,
                    company_description TEXT,
                    business_focus TEXT,
                    company_compliment TEXT,
                    issues TEXT,
                    solutions TEXT,
                    fomo_text TEXT,
                    scrape_status TEXT DEFAULT 'pending',
                    scrape_date TIMESTAMP,
                    raw_html TEXT,
                    FOREIGN KEY (contact_id) REFERENCES contacts(id)
                )
            """)
            
            # Create email_campaigns table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS email_campaigns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    subject_template TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create email_sends table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS email_sends (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contact_id INTEGER,
                    campaign_id INTEGER,
                    email_subject TEXT,
                    email_body TEXT,
                    send_status TEXT DEFAULT 'pending',
                    sent_at TIMESTAMP,
                    delivery_status TEXT,
                    sendgrid_message_id TEXT,
                    bounce_reason TEXT,
                    open_count INTEGER DEFAULT 0,
                    click_count INTEGER DEFAULT 0,
                    last_opened TIMESTAMP,
                    last_clicked TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (contact_id) REFERENCES contacts(id),
                    FOREIGN KEY (campaign_id) REFERENCES email_campaigns(id)
                )
            """)
            
            # Create processing_logs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS processing_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contact_id INTEGER,
                    process_type TEXT,
                    status TEXT,
                    message TEXT,
                    details TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (contact_id) REFERENCES contacts(id)
                )
            """)
            
            # Create app_settings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS app_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_contacts_email ON contacts(email_address)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_contacts_domain ON contacts(domain)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_website_analysis_domain ON website_analysis(domain)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_email_sends_status ON email_sends(send_status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_email_sends_contact ON email_sends(contact_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_processing_logs_contact ON processing_logs(contact_id)")
            
            # Insert default campaign if not exists
            cursor.execute("SELECT COUNT(*) FROM email_campaigns")
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    INSERT INTO email_campaigns (name, subject_template) 
                    VALUES (?, ?)
                """, ("NetWit Outreach", "Quick question about {{ company_name }}'s website"))
            
            # Insert default settings if not exists
            default_settings = [
                ('sendgrid_api_key', ''),
                ('sender_email', 'noreply@expanzagroup.com'),
                ('reply_to_email', 'dave@netwit.ca'),
                ('together_ai_api_key', ''),
                ('max_emails_per_hour', '50'),
                ('scraping_delay_seconds', '2')
            ]
            
            cursor.execute("SELECT COUNT(*) FROM app_settings")
            if cursor.fetchone()[0] == 0:
                cursor.executemany("""
                    INSERT INTO app_settings (key, value) VALUES (?, ?)
                """, default_settings)
            
            conn.commit()
    
    # CONTACT METHODS
    def add_contact(self, email_address: str, first_name: str = None, 
                   last_name: str = None, full_name: str = None, 
                   domain: str = None, company_name: str = None) -> int:
        """Add a new contact and return contact ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO contacts 
                (email_address, first_name, last_name, full_name, domain, company_name, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (email_address, first_name, last_name, full_name, domain, company_name, datetime.now()))
            conn.commit()
            return cursor.lastrowid
    
    def get_contact_by_email(self, email_address: str) -> Optional[Dict]:
        """Get contact by email address"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE email_address = ?", (email_address,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_all_contacts(self) -> List[Dict]:
        """Get all contacts"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts ORDER BY created_at DESC")
            return [dict(row) for row in cursor.fetchall()]
    
    def get_contacts_without_analysis(self) -> List[Dict]:
        """Get contacts that haven't been analyzed yet"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.* FROM contacts c
                LEFT JOIN website_analysis w ON c.id = w.contact_id
                WHERE w.id IS NULL OR w.scrape_status = 'failed'
                ORDER BY c.created_at
            """)
            return [dict(row) for row in cursor.fetchall()]
    
    # WEBSITE ANALYSIS METHODS
    def save_website_analysis(self, contact_id: int, domain: str, 
                            company_description: str = None,
                            business_focus: str = None,
                            company_compliment: str = None,
                            issues: List[str] = None,
                            solutions: List[str] = None,
                            fomo_text: str = None,
                            raw_html: str = None) -> int:
        """Save website analysis results"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO website_analysis 
                (contact_id, domain, company_description, business_focus, 
                 company_compliment, issues, solutions, fomo_text, 
                 scrape_status, scrape_date, raw_html)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                contact_id, domain, company_description, business_focus,
                company_compliment, 
                json.dumps(issues) if issues else None,
                json.dumps(solutions) if solutions else None,
                fomo_text, 'completed', datetime.now(), raw_html
            ))
            conn.commit()
            return cursor.lastrowid
    
    def get_website_analysis(self, contact_id: int) -> Optional[Dict]:
        """Get website analysis for contact"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM website_analysis WHERE contact_id = ? 
                ORDER BY scrape_date DESC LIMIT 1
            """, (contact_id,))
            row = cursor.fetchone()
            if row:
                result = dict(row)
                # Parse JSON fields
                if result['issues']:
                    result['issues'] = json.loads(result['issues'])
                if result['solutions']:
                    result['solutions'] = json.loads(result['solutions'])
                return result
            return None
    
    def mark_scraping_failed(self, contact_id: int, error_message: str):
        """Mark website scraping as failed"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO website_analysis 
                (contact_id, domain, scrape_status, scrape_date)
                SELECT ?, domain, 'failed', ? FROM contacts WHERE id = ?
            """, (contact_id, datetime.now(), contact_id))
            conn.commit()
    
    # EMAIL SENDING METHODS
    def save_email_send(self, contact_id: int, campaign_id: int, 
                       email_subject: str, email_body: str,
                       sendgrid_message_id: str = None) -> int:
        """Save email send record"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO email_sends 
                (contact_id, campaign_id, email_subject, email_body, 
                 send_status, sent_at, sendgrid_message_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (contact_id, campaign_id, email_subject, email_body,
                  'sent', datetime.now(), sendgrid_message_id))
            conn.commit()
            return cursor.lastrowid
    
    def update_email_status(self, email_send_id: int, status: str, 
                           delivery_status: str = None, bounce_reason: str = None):
        """Update email delivery status"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE email_sends 
                SET send_status = ?, delivery_status = ?, bounce_reason = ?
                WHERE id = ?
            """, (status, delivery_status, bounce_reason, email_send_id))
            conn.commit()
    
    def get_pending_emails(self) -> List[Dict]:
        """Get emails that need to be sent"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT es.*, c.email_address, c.first_name, c.company_name
                FROM email_sends es
                JOIN contacts c ON es.contact_id = c.id
                WHERE es.send_status = 'pending'
                ORDER BY es.created_at
            """)
            return [dict(row) for row in cursor.fetchall()]
    
    # LOGGING METHODS
    def log_processing(self, contact_id: int, process_type: str, 
                      status: str, message: str, details: Dict = None):
        """Log processing events"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO processing_logs 
                (contact_id, process_type, status, message, details)
                VALUES (?, ?, ?, ?, ?)
            """, (contact_id, process_type, status, message, 
                  json.dumps(details) if details else None))
            conn.commit()
    
    def get_processing_logs(self, contact_id: int = None, 
                           process_type: str = None) -> List[Dict]:
        """Get processing logs with optional filters"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM processing_logs WHERE 1=1"
            params = []
            
            if contact_id:
                query += " AND contact_id = ?"
                params.append(contact_id)
            
            if process_type:
                query += " AND process_type = ?"
                params.append(process_type)
            
            query += " ORDER BY created_at DESC"
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    # SETTINGS METHODS
    def get_setting(self, key: str) -> Optional[str]:
        """Get application setting"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM app_settings WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row[0] if row else None
    
    def set_setting(self, key: str, value: str):
        """Set application setting"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO app_settings (key, value, updated_at)
                VALUES (?, ?, ?)
            """, (key, value, datetime.now()))
            conn.commit()
    
    # ANALYTICS METHODS
    def get_email_stats(self) -> Dict:
        """Get email sending statistics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Total emails sent
            cursor.execute("SELECT COUNT(*) FROM email_sends WHERE send_status = 'sent'")
            sent_count = cursor.fetchone()[0]
            
            # Pending emails
            cursor.execute("SELECT COUNT(*) FROM email_sends WHERE send_status = 'pending'")
            pending_count = cursor.fetchone()[0]
            
            # Failed emails
            cursor.execute("SELECT COUNT(*) FROM email_sends WHERE send_status = 'failed'")
            failed_count = cursor.fetchone()[0]
            
            # Opened emails
            cursor.execute("SELECT COUNT(*) FROM email_sends WHERE open_count > 0")
            opened_count = cursor.fetchone()[0]
            
            # Clicked emails
            cursor.execute("SELECT COUNT(*) FROM email_sends WHERE click_count > 0")
            clicked_count = cursor.fetchone()[0]
            
            return {
                'sent': sent_count,
                'pending': pending_count,
                'failed': failed_count,
                'opened': opened_count,
                'clicked': clicked_count,
                'open_rate': (opened_count / sent_count * 100) if sent_count > 0 else 0,
                'click_rate': (clicked_count / sent_count * 100) if sent_count > 0 else 0
            }
    
    def get_contact_with_analysis(self, contact_id: int) -> Optional[Dict]:
        """Get contact with their website analysis"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.*, w.company_description, w.business_focus, 
                       w.company_compliment, w.issues, w.solutions, w.fomo_text
                FROM contacts c
                LEFT JOIN website_analysis w ON c.id = w.contact_id
                WHERE c.id = ?
            """, (contact_id,))
            row = cursor.fetchone()
            if row:
                result = dict(row)
                # Parse JSON fields
                if result.get('issues'):
                    result['issues'] = json.loads(result['issues'])
                if result.get('solutions'):
                    result['solutions'] = json.loads(result['solutions'])
                return result
            return None


# Initialize database instance
db = DatabaseManager()