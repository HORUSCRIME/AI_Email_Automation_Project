import re
from typing import List, Tuple
from email_validator import validate_email, EmailNotValidError

class EmailValidator:
    @staticmethod
    def validate_email_format(email: str) -> Tuple[bool, str]:
        """Validate email format"""
        try:
            # Use email-validator library for comprehensive validation
            valid = validate_email(email)
            return True, valid.email
        except EmailNotValidError as e:
            return False, str(e)
    
    @staticmethod
    def validate_domain(domain: str) -> bool:
        """Validate domain format"""
        # Corrected: Use triple quotes for the multiline string
        domain_pattern = re.compile(
            r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?"
        )
        return bool(domain_pattern.match(domain))
    
    @staticmethod
    def clean_email_list(emails: List[str]) -> List[str]:
        """Clean and validate list of emails"""
        cleaned_emails = []
        
        for email in emails:
            email = email.strip().lower()
            if email:
                is_valid, validated_email = EmailValidator.validate_email_format(email)
                if is_valid:
                    cleaned_emails.append(validated_email)
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(cleaned_emails))

