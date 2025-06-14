# # from pydantic import BaseModel, EmailStr, validator
# # from typing import List, Optional, Dict
# # from datetime import datetime

# # class EmailRecord(BaseModel):
# #     email: EmailStr
# #     first_name: Optional[str] = None
# #     last_name: Optional[str] = None
# #     full_name: Optional[str] = None
# #     domain: Optional[str] = None
# #     company_name: Optional[str] = None

# # class CompanyInfo(BaseModel):
# #     domain: str
# #     company_description: str
# #     business_type: str
# #     issues_found: List[str]
# #     recommendations: List[str]
# #     seo_score: Optional[int] = None
# #     mobile_friendly: Optional[bool] = None
# #     loading_speed: Optional[float] = None

# # class EmailContent(BaseModel):
# #     subject: str
# #     html_body: str
# #     text_body: str
# #     personalization_tokens: Dict[str, str]

# # class EmailJob(BaseModel):
# #     id: str
# #     emails: List[EmailRecord]
# #     status: str = "pending"  # pending, processing, completed, failed
# #     created_at: datetime
# #     completed_at: Optional[datetime] = None
# #     results: Optional[Dict] = None

# # class EmailUpload(BaseModel):
# #     file_content: str
# #     file_type: str  # csv, xlsx, txt


# from pydantic import BaseModel, EmailStr, validator
# from typing import List, Optional, Dict, Any
# from datetime import datetime
# from enum import Enum

# class ProcessStatus(str, Enum):
#     PENDING = "pending"
#     COMPLETED = "completed"
#     FAILED = "failed"

# class SendStatus(str, Enum):
#     PENDING = "pending"
#     SENT = "sent"
#     FAILED = "failed"
#     BOUNCED = "bounced"

# class DeliveryStatus(str, Enum):
#     DELIVERED = "delivered"
#     OPENED = "opened"
#     CLICKED = "clicked"
#     REPLIED = "replied"

# class ProcessType(str, Enum):
#     SCRAPING = "scraping"
#     EMAIL_GENERATION = "email_generation"
#     EMAIL_SENDING = "email_sending"
#     NAME_EXTRACTION = "name_extraction"

# class LogStatus(str, Enum):
#     SUCCESS = "success"
#     ERROR = "error"
#     WARNING = "warning"

# # Contact Models
# class ContactBase(BaseModel):
#     email_address: EmailStr
#     first_name: Optional[str] = None
#     last_name: Optional[str] = None
#     full_name: Optional[str] = None
#     domain: Optional[str] = None
#     company_name: Optional[str] = None

# class ContactCreate(ContactBase):
#     pass

# class ContactUpdate(BaseModel):
#     first_name: Optional[str] = None
#     last_name: Optional[str] = None
#     full_name: Optional[str] = None
#     domain: Optional[str] = None
#     company_name: Optional[str] = None

# class Contact(ContactBase):
#     id: int
#     created_at: datetime
#     updated_at: datetime
    
#     class Config:
#         from_attributes = True

# # Website Analysis Models
# class WebsiteAnalysisBase(BaseModel):
#     domain: str
#     company_description: Optional[str] = None
#     business_focus: Optional[str] = None
#     company_compliment: Optional[str] = None
#     issues: Optional[List[str]] = []
#     solutions: Optional[List[str]] = []
#     fomo_text: Optional[str] = None

# class WebsiteAnalysisCreate(WebsiteAnalysisBase):
#     contact_id: int
#     raw_html: Optional[str] = None

# class WebsiteAnalysis(WebsiteAnalysisBase):
#     id: int
#     contact_id: int
#     scrape_status: ProcessStatus = ProcessStatus.PENDING
#     scrape_date: Optional[datetime] = None
#     raw_html: Optional[str] = None
    
#     class Config:
#         from_attributes = True

# # Email Campaign Models
# class EmailCampaignBase(BaseModel):
#     name: str
#     subject_template: str

# class EmailCampaignCreate(EmailCampaignBase):
#     pass

# class EmailCampaign(EmailCampaignBase):
#     id: int
#     created_at: datetime
    
#     class Config:
#         from_attributes = True

# # Email Send Models
# class EmailSendBase(BaseModel):
#     email_subject: str
#     email_body: str

# class EmailSendCreate(EmailSendBase):
#     contact_id: int
#     campaign_id: int
#     sendgrid_message_id: Optional[str] = None

# class EmailSend(EmailSendBase):
#     id: int
#     contact_id: int
#     campaign_id: int
#     send_status: SendStatus = SendStatus.PENDING
#     sent_at: Optional[datetime] = None
#     delivery_status: Optional[DeliveryStatus] = None
#     sendgrid_message_id: Optional[str] = None
#     bounce_reason: Optional[str] = None
#     open_count: int = 0
#     click_count: int = 0
#     last_opened: Optional[datetime] = None
#     last_clicked: Optional[datetime] = None
#     created_at: datetime
    
#     class Config:
#         from_attributes = True

# # Processing Log Models
# class ProcessingLogBase(BaseModel):
#     process_type: ProcessType
#     status: LogStatus
#     message: str
#     details: Optional[Dict[str, Any]] = None

# class ProcessingLogCreate(ProcessingLogBase):
#     contact_id: Optional[int] = None

# class ProcessingLog(ProcessingLogBase):
#     id: int
#     contact_id: Optional[int] = None
#     created_at: datetime
    
#     class Config:
#         from_attributes = True

# # App Settings Models
# class AppSettingBase(BaseModel):
#     key: str
#     value: str

# class AppSetting(AppSettingBase):
#     updated_at: datetime
    
#     class Config:
#         from_attributes = True

# # Email Template Data Model
# class EmailTemplateData(BaseModel):
#     first_name: str
#     email_address: EmailStr
#     company_name: str
#     subject_line: str = "Quick question about your website"
#     intro_text: str = "Hope you're having a great day!"
#     company_compliment: str = "your professional approach"
#     business_focus: str = "services"
#     issues: List[str] = []
#     solutions: List[str] = []
#     fomo_text: Optional[str] = None
#     cta_text: str = "Let's Chat - Book Your Free Consultation"
#     cta_link: str = "https://calendly.com/dave-netwit/consultation"
#     unsubscribe_link: str = "https://netwit.ca/unsubscribe"
#     tracking_pixel: Optional[str] = None

# # CSV Upload Models
# class EmailListUpload(BaseModel):
#     emails: List[EmailStr]
    
#     @validator('emails')
#     def validate_emails(cls, v):
#         if not v:
#             raise ValueError('Email list cannot be empty')
#         if len(v) > 1000:
#             raise ValueError('Maximum 1000 emails allowed per upload')
#         return v

# # Statistics Models
# class EmailStats(BaseModel):
#     sent: int
#     pending: int
#     failed: int
#     opened: int
#     clicked: int
#     open_rate: float
#     click_rate: float

# class ContactWithAnalysis(Contact):
#     company_description: Optional[str] = None
#     business_focus: Optional[str] = None
#     company_compliment: Optional[str] = None
#     issues: Optional[List[str]] = []
#     solutions: Optional[List[str]] = []
#     fomo_text: Optional[str] = None

# # Webhook Models (for SendGrid events)
# class SendGridEvent(BaseModel):
#     email: EmailStr
#     timestamp: int
#     event: str
#     sg_message_id: Optional[str] = None
#     reason: Optional[str] = None
#     status: Optional[str] = None
    
# class SendGridWebhookPayload(BaseModel):
#     events: List[SendGridEvent]

# # LLM Response Models
# class LLMCompanyAnalysis(BaseModel):
#     company_description: str
#     business_focus: str
#     company_compliment: str
#     issues: List[str]
#     solutions: List[str]
#     fomo_text: str

# # Name Extraction Models
# class ExtractedName(BaseModel):
#     first_name: Optional[str] = None
#     last_name: Optional[str] = None
#     full_name: Optional[str] = None
#     confidence: float = 0.0  # 0.0 to 1.0

# # Scraping Result Models
# class ScrapingResult(BaseModel):
#     success: bool
#     html_content: Optional[str] = None
#     error_message: Optional[str] = None
#     page_title: Optional[str] = None
#     meta_description: Optional[str] = None
#     has_ssl: bool = False
#     response_time: Optional[float] = None
#     status_code: Optional[int] = None

# # API Response Models
# class APIResponse(BaseModel):
#     success: bool
#     message: str
#     data: Optional[Any] = None
#     error: Optional[str] = None

# class ProcessingStatus(BaseModel):
#     total_contacts: int
#     processed: int
#     pending: int
#     failed: int
#     success_rate: float
#     current_status: str


from pydantic import BaseModel, EmailStr, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ProcessStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

class SendStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    BOUNCED = "bounced"

class DeliveryStatus(str, Enum):
    DELIVERED = "delivered"
    OPENED = "opened"
    CLICKED = "clicked"
    REPLIED = "replied"

class ProcessType(str, Enum):
    SCRAPING = "scraping"
    EMAIL_GENERATION = "email_generation"
    EMAIL_SENDING = "email_sending"
    NAME_EXTRACTION = "name_extraction"

class LogStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"

# Contact Models
class ContactBase(BaseModel):
    email_address: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    domain: Optional[str] = None
    company_name: Optional[str] = None

class ContactCreate(ContactBase):
    pass

class ContactUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    domain: Optional[str] = None
    company_name: Optional[str] = None

class Contact(ContactBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Website Analysis Models
class WebsiteAnalysisBase(BaseModel):
    domain: str
    company_description: Optional[str] = None
    business_focus: Optional[str] = None
    company_compliment: Optional[str] = None
    issues: Optional[List[str]] = []
    solutions: Optional[List[str]] = []
    fomo_text: Optional[str] = None

class WebsiteAnalysisCreate(WebsiteAnalysisBase):
    contact_id: int
    raw_html: Optional[str] = None

class WebsiteAnalysis(WebsiteAnalysisBase):
    id: int
    contact_id: int
    scrape_status: ProcessStatus = ProcessStatus.PENDING
    scrape_date: Optional[datetime] = None
    raw_html: Optional[str] = None
    
    class Config:
        from_attributes = True

# Email Campaign Models
class EmailCampaignBase(BaseModel):
    name: str
    subject_template: str

class EmailCampaignCreate(EmailCampaignBase):
    pass

class EmailCampaign(EmailCampaignBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Email Send Models
class EmailSendBase(BaseModel):
    email_subject: str
    email_body: str

class EmailSendCreate(EmailSendBase):
    contact_id: int
    campaign_id: int
    sendgrid_message_id: Optional[str] = None

class EmailSend(EmailSendBase):
    id: int
    contact_id: int
    campaign_id: int
    send_status: SendStatus = SendStatus.PENDING
    sent_at: Optional[datetime] = None
    delivery_status: Optional[DeliveryStatus] = None
    sendgrid_message_id: Optional[str] = None
    bounce_reason: Optional[str] = None
    open_count: int = 0
    click_count: int = 0
    last_opened: Optional[datetime] = None
    last_clicked: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Processing Log Models
class ProcessingLogBase(BaseModel):
    process_type: ProcessType
    status: LogStatus
    message: str
    details: Optional[Dict[str, Any]] = None

class ProcessingLogCreate(ProcessingLogBase):
    contact_id: Optional[int] = None

class ProcessingLog(ProcessingLogBase):
    id: int
    contact_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# App Settings Models
class AppSettingBase(BaseModel):
    key: str
    value: str

class AppSetting(AppSettingBase):
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Email Template Data Model
class EmailTemplateData(BaseModel):
    first_name: str
    email_address: EmailStr
    company_name: str
    subject_line: str = "Quick question about your website"
    intro_text: str = "Hope you're having a great day!"
    company_compliment: str = "your professional approach"
    business_focus: str = "services"
    issues: List[str] = []
    solutions: List[str] = []
    fomo_text: Optional[str] = None
    cta_text: str = "Let's Chat - Book Your Free Consultation"
    cta_link: str = "https://calendly.com/dave-netwit/consultation"
    unsubscribe_link: str = "https://netwit.ca/unsubscribe"
    tracking_pixel: Optional[str] = None

# CSV Upload Models
class EmailListUpload(BaseModel):
    emails: List[EmailStr]
    
    @validator('emails')
    def validate_emails(cls, v):
        if not v:
            raise ValueError('Email list cannot be empty')
        if len(v) > 1000:
            raise ValueError('Maximum 1000 emails allowed per upload')
        return v

# Statistics Models
class EmailStats(BaseModel):
    sent: int
    pending: int
    failed: int
    opened: int
    clicked: int
    open_rate: float
    click_rate: float

class ContactWithAnalysis(Contact):
    company_description: Optional[str] = None
    business_focus: Optional[str] = None
    company_compliment: Optional[str] = None
    issues: Optional[List[str]] = []
    solutions: Optional[List[str]] = []
    fomo_text: Optional[str] = None

# Webhook Models (for SendGrid events)
class SendGridEvent(BaseModel):
    email: EmailStr
    timestamp: int
    event: str
    sg_message_id: Optional[str] = None
    reason: Optional[str] = None
    status: Optional[str] = None
    
class SendGridWebhookPayload(BaseModel):
    events: List[SendGridEvent]

# LLM Response Models
class LLMCompanyAnalysis(BaseModel):
    company_description: str
    business_focus: str
    company_compliment: str
    issues: List[str]
    solutions: List[str]
    fomo_text: str

# Name Extraction Models
class ExtractedName(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    confidence: float = 0.0  # 0.0 to 1.0

# Scraping Result Models
class ScrapingResult(BaseModel):
    success: bool
    html_content: Optional[str] = None
    error_message: Optional[str] = None
    page_title: Optional[str] = None
    meta_description: Optional[str] = None
    has_ssl: bool = False
    response_time: Optional[float] = None
    status_code: Optional[int] = None

# API Response Models
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    error: Optional[str] = None

class ProcessingStatus(BaseModel):
    total_contacts: int
    processed: int
    pending: int
    failed: int
    success_rate: float
    current_status: str

# Backward Compatibility Aliases
EmailRecord = Contact
EmailJob = EmailCampaign
EmailUpload = EmailListUpload