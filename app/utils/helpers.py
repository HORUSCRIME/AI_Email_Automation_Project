import uuid
import hashlib
import json
import os
from datetime import datetime
from typing import Dict, Any

class Helpers:
    @staticmethod
    def generate_job_id() -> str:
        """Generate unique job ID"""
        return str(uuid.uuid4())
    
    @staticmethod
    def hash_email(email: str) -> str:
        """Hash email for privacy"""
        return hashlib.sha256(email.encode()).hexdigest()[:16]
    
    @staticmethod
    def save_job_data(job_id: str, data: Dict[str, Any]):
        """Save job data to file"""
        os.makedirs("data/jobs", exist_ok=True)
        
        filename = f"data/jobs/{job_id}.json"
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    @staticmethod
    def load_job_data(job_id: str) -> Dict[str, Any]:
        """Load job data from file"""
        filename = f"data/jobs/{job_id}.json"
        
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return json.load(f)
        
        return {}
    
    @staticmethod
    def create_directories():
        """Create necessary directories"""
        directories = [
            "data",
            "data/jobs",
            "data/logs",
            "data/processed_emails"
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    @staticmethod
    def log_activity(activity: str, details: Dict[str, Any] = None):
        """Log application activity"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "activity": activity,
            "details": details or {}
        }
        
        os.makedirs("data/logs", exist_ok=True)
        
        log_file = f"data/logs/{datetime.now().strftime('%Y-%m-%d')}.json"
        
        # Load existing logs
        logs = []
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                logs = json.load(f)
        
        # Add new log entry
        logs.append(log_entry)
        
        # Save logs
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)