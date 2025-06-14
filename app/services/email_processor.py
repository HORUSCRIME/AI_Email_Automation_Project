# # import re
# # import pandas as pd
# # from typing import List, Tuple
# # from ..models.schemas import EmailRecord
# # import nltk
# # from nltk.corpus import names

# # class EmailProcessor:
# #     def __init__(self):
# #         # Download required NLTK data
# #         try:
# #             nltk.data.find('corpora/names')
# #         except LookupError:
# #             nltk.download('names')
        
# #         self.common_names = set(names.words())
    
# #     def parse_emails_from_csv(self, file_content: str) -> List[EmailRecord]:
# #         """Parse emails from CSV content"""
# #         try:
# #             # Handle different CSV formats
# #             lines = file_content.strip().split('\n')
# #             emails = []
            
# #             for line in lines:
# #                 # Try to extract email from each line
# #                 email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', line)
# #                 if email_match:
# #                     email = email_match.group().lower()
# #                     record = self.process_single_email(email)
# #                     if record:
# #                         emails.append(record)
            
# #             return emails
# #         except Exception as e:
# #             raise ValueError(f"Error parsing CSV: {str(e)}")
    
# #     def parse_emails_from_excel(self, file_content: bytes) -> List[EmailRecord]:
# #         """Parse emails from Excel file"""
# #         try:
# #             df = pd.read_excel(file_content)
# #             emails = []
            
# #             # Look for email column
# #             email_columns = [col for col in df.columns if 'email' in col.lower()]
# #             if email_columns:
# #                 email_col = email_columns[0]
# #                 for email in df[email_col].dropna():
# #                     record = self.process_single_email(str(email).lower())
# #                     if record:
# #                         emails.append(record)
# #             else:
# #                 # Try to find emails in all columns
# #                 for col in df.columns:
# #                     for value in df[col].dropna():
# #                         email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', str(value))
# #                         if email_match:
# #                             email = email_match.group().lower()
# #                             record = self.process_single_email(email)
# #                             if record:
# #                                 emails.append(record)
            
# #             return emails
# #         except Exception as e:
# #             raise ValueError(f"Error parsing Excel: {str(e)}")
    
# #     def process_single_email(self, email: str) -> Optional[EmailRecord]:
# #         """Process a single email address"""
# #         try:
# #             # Validate email format
# #             if not re.match(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$', email):
# #                 return None
            
# #             local_part, domain = email.split('@')
            
# #             # Extract names from local part
# #             first_name, last_name, full_name = self.extract_names_from_local(local_part)
            
# #             # Extract company name from domain
# #             company_name = self.extract_company_name(domain)
            
# #             return EmailRecord(
# #                 email=email,
# #                 first_name=first_name,
# #                 last_name=last_name,
# #                 full_name=full_name,
# #                 domain=domain,
# #                 company_name=company_name
# #             )
# #         except Exception:
# #             return None
    
# #     def extract_names_from_local(self, local_part: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
# #         """Extract first name, last name, and full name from email local part"""
# #         # Remove numbers and special characters except dots and underscores
# #         clean_local = re.sub(r'[0-9]', '', local_part)
        
# #         # Split by common separators
# #         parts = re.split(r'[._-]', clean_local)
# #         parts = [part.strip() for part in parts if part.strip()]
        
# #         if not parts:
# #             return None, None, None
        
# #         first_name = None
# #         last_name = None
        
# #         # Try to identify first name
# #         for part in parts:
# #             if len(part) > 1 and part.lower() in [name.lower() for name in self.common_names]:
# #                 first_name = part.capitalize()
# #                 break
        
# #         # If no common name found, use first part
# #         if not first_name and parts:
# #             first_name = parts[0].capitalize()
        
# #         # Try to get last name
# #         if len(parts) > 1:
# #             if first_name and first_name.lower() == parts[0].lower():
# #                 last_name = parts[1].capitalize()
# #             else:
# #                 last_name = parts[-1].capitalize()
        
# #         # Create full name
# #         full_name = None
# #         if first_name and last_name:
# #             full_name = f"{first_name} {last_name}"
# #         elif first_name:
# #             full_name = first_name
        
# #         return first_name, last_name, full_name
    
# #     def extract_company_name(self, domain: str) -> str:
# #         """Extract company name from domain"""
# #         # Remove common TLDs and subdomains
# #         domain_parts = domain.split('.')
# #         if len(domain_parts) > 2:
# #             # Remove www if present
# #             if domain_parts[0] == 'www':
# #                 domain_parts = domain_parts[1:]
        
# #         # Take the main domain part
# #         company_part = domain_parts[0] if domain_parts else domain
        
# #         # Clean and format
# #         company_name = re.sub(r'[^a-zA-Z0-9]', ' ', company_part)
# #         company_name = ' '.join(word.capitalize() for word in company_name.split())
        
# #         return company_name

        


# import re
# import pandas as pd
# from typing import List, Tuple, Optional
# from ..models.schemas import EmailRecord
# import nltk
# from nltk.corpus import names

# class EmailProcessor:
#     def __init__(self):
#         # Download required NLTK data
#         try:
#             nltk.data.find('corpora/names')
#         except LookupError:
#             nltk.download('names')
        
#         self.common_names = set(names.words())
    
#     def parse_emails_from_csv(self, file_content: str) -> List[EmailRecord]:
#         """Parse emails from CSV content"""
#         try:
#             # Handle different CSV formats
#             lines = file_content.strip().split('\n')
#             emails = []
            
#             for line in lines:
#                 # Try to extract email from each line
#                 email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', line)
#                 if email_match:
#                     email = email_match.group().lower()
#                     record = self.process_single_email(email)
#                     if record:
#                         emails.append(record)
            
#             return emails
#         except Exception as e:
#             raise ValueError(f"Error parsing CSV: {str(e)}")
    
#     def parse_emails_from_excel(self, file_content: bytes) -> List[EmailRecord]:
#         """Parse emails from Excel file"""
#         try:
#             df = pd.read_excel(file_content)
#             emails = []
            
#             # Look for email column
#             email_columns = [col for col in df.columns if 'email' in col.lower()]
#             if email_columns:
#                 email_col = email_columns[0]
#                 for email in df[email_col].dropna():
#                     record = self.process_single_email(str(email).lower())
#                     if record:
#                         emails.append(record)
#             else:
#                 # Try to find emails in all columns
#                 for col in df.columns:
#                     for value in df[col].dropna():
#                         email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', str(value))
#                         if email_match:
#                             email = email_match.group().lower()
#                             record = self.process_single_email(email)
#                             if record:
#                                 emails.append(record)
            
#             return emails
#         except Exception as e:
#             raise ValueError(f"Error parsing Excel: {str(e)}")
    
#     def process_single_email(self, email: str) -> Optional[EmailRecord]:
#         """Process a single email address"""
#         try:
#             # Validate email format
#             if not re.match(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$', email):
#                 return None
            
#             local_part, domain = email.split('@')
            
#             # Extract names from local part
#             first_name, last_name, full_name = self.extract_names_from_local(local_part)
            
#             # Extract company name from domain
#             company_name = self.extract_company_name(domain)
            
#             return EmailRecord(
#                 email=email,
#                 first_name=first_name,
#                 last_name=last_name,
#                 full_name=full_name,
#                 domain=domain,
#                 company_name=company_name
#             )
#         except Exception:
#             return None
    
#     def extract_names_from_local(self, local_part: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
#         """Extract first name, last name, and full name from email local part"""
#         # Remove numbers and special characters except dots and underscores
#         clean_local = re.sub(r'[0-9]', '', local_part)
        
#         # Split by common separators
#         parts = re.split(r'[._-]', clean_local)
#         parts = [part.strip() for part in parts if part.strip()]
        
#         if not parts:
#             return None, None, None
        
#         first_name = None
#         last_name = None
        
#         # Try to identify first name
#         for part in parts:
#             if len(part) > 1 and part.lower() in [name.lower() for name in self.common_names]:
#                 first_name = part.capitalize()
#                 break
        
#         # If no common name found, use first part
#         if not first_name and parts:
#             first_name = parts[0].capitalize()
        
#         # Try to get last name
#         if len(parts) > 1:
#             if first_name and first_name.lower() == parts[0].lower():
#                 last_name = parts[1].capitalize()
#             else:
#                 last_name = parts[-1].capitalize()
        
#         # Create full name
#         full_name = None
#         if first_name and last_name:
#             full_name = f"{first_name} {last_name}"
#         elif first_name:
#             full_name = first_name
        
#         return first_name, last_name, full_name
    
#     def extract_company_name(self, domain: str) -> str:
#         """Extract company name from domain"""
#         # Remove common TLDs and subdomains
#         domain_parts = domain.split('.')
#         if len(domain_parts) > 2:
#             # Remove www if present
#             if domain_parts[0] == 'www':
#                 domain_parts = domain_parts[1:]
        
#         # Take the main domain part
#         company_part = domain_parts[0] if domain_parts else domain
        
#         # Clean and format
#         company_name = re.sub(r'[^a-zA-Z0-9]', ' ', company_part)
#         company_name = ' '.join(word.capitalize() for word in company_name.split())
        
#         return company_name


import re
import pandas as pd
from typing import List, Tuple, Optional
from ..models.schemas import EmailRecord
import nltk
from nltk.corpus import names

class EmailProcessor:
    def __init__(self):
        # Download required NLTK data
        try:
            nltk.data.find('corpora/names')
        except LookupError:
            nltk.download('names')
        
        self.common_names = set(names.words())
    
    def parse_emails_from_csv(self, file_content: str) -> List[EmailRecord]:
        """Parse emails from CSV content"""
        try:
            # Handle different CSV formats
            lines = file_content.strip().split('\n')
            emails = []
            
            for line in lines:
                # Try to extract email from each line
                email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', line)
                if email_match:
                    email = email_match.group().lower()
                    record = self.process_single_email(email)
                    if record:
                        emails.append(record)
            
            return emails
        except Exception as e:
            raise ValueError(f"Error parsing CSV: {str(e)}")
    
    def parse_emails_from_excel(self, file_content: bytes) -> List[EmailRecord]:
        """Parse emails from Excel file"""
        try:
            df = pd.read_excel(file_content)
            emails = []
            
            # Look for email column
            email_columns = [col for col in df.columns if 'email' in col.lower()]
            if email_columns:
                email_col = email_columns[0]
                for email in df[email_col].dropna():
                    record = self.process_single_email(str(email).lower())
                    if record:
                        emails.append(record)
            else:
                # Try to find emails in all columns
                for col in df.columns:
                    for value in df[col].dropna():
                        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', str(value))
                        if email_match:
                            email = email_match.group().lower()
                            record = self.process_single_email(email)
                            if record:
                                emails.append(record)
            
            return emails
        except Exception as e:
            raise ValueError(f"Error parsing Excel: {str(e)}")
    
    def process_single_email(self, email: str) -> Optional[EmailRecord]:
        """Process a single email address"""
        try:
            # Validate email format
            if not re.match(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$', email):
                return None
            
            local_part, domain = email.split('@')
            
            # Extract names from local part
            first_name, last_name, full_name = self.extract_names_from_local(local_part)
            
            # Extract company name from domain
            company_name = self.extract_company_name(domain)
            
            return EmailRecord(
                email_address=email,
                first_name=first_name,
                last_name=last_name,
                full_name=full_name,
                domain=domain,
                company_name=company_name
            )
        except Exception:
            return None
    
    def extract_names_from_local(self, local_part: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Extract first name, last name, and full name from email local part"""
        # Remove numbers and special characters except dots and underscores
        clean_local = re.sub(r'[0-9]', '', local_part)
        
        # Split by common separators
        parts = re.split(r'[._-]', clean_local)
        parts = [part.strip() for part in parts if part.strip()]
        
        if not parts:
            return None, None, None
        
        first_name = None
        last_name = None
        
        # Try to identify first name
        for part in parts:
            if len(part) > 1 and part.lower() in [name.lower() for name in self.common_names]:
                first_name = part.capitalize()
                break
        
        # If no common name found, use first part
        if not first_name and parts:
            first_name = parts[0].capitalize()
        
        # Try to get last name
        if len(parts) > 1:
            if first_name and first_name.lower() == parts[0].lower():
                last_name = parts[1].capitalize()
            else:
                last_name = parts[-1].capitalize()
        
        # Create full name
        full_name = None
        if first_name and last_name:
            full_name = f"{first_name} {last_name}"
        elif first_name:
            full_name = first_name
        
        return first_name, last_name, full_name
    
    def extract_company_name(self, domain: str) -> str:
        """Extract company name from domain"""
        # Remove common TLDs and subdomains
        domain_parts = domain.split('.')
        if len(domain_parts) > 2:
            # Remove www if present
            if domain_parts[0] == 'www':
                domain_parts = domain_parts[1:]
        
        # Take the main domain part
        company_part = domain_parts[0] if domain_parts else domain
        
        # Clean and format
        company_name = re.sub(r'[^a-zA-Z0-9]', ' ', company_part)
        company_name = ' '.join(word.capitalize() for word in company_name.split())
        
        return company_name