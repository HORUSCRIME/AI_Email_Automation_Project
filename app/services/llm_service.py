from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import torch
from typing import Dict, List
import json
import re

class LLMService:
    def __init__(self, model_name: str = "microsoft/DialoGPT-medium"):
        """Initialize LLM service with Hugging Face model"""
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Use a lightweight model for text generation
        try:
            self.generator = pipeline(
                "text-generation",
                model="gpt2",  # Lightweight and good for email generation
                device=0 if torch.cuda.is_available() else -1,
                max_length=512,
                do_sample=True,
                temperature=0.7,
                pad_token_id=50256
            )
        except Exception as e:
            print(f"Failed to load GPU model, using CPU: {e}")
            self.generator = pipeline(
                "text-generation",
                model="gpt2",
                device=-1,
                max_length=512,
                do_sample=True,
                temperature=0.7,
                pad_token_id=50256
            )
    
    def analyze_company_business(self, website_content: str, domain: str) -> Dict:
        """Analyze what the company does based on website content"""
        
        prompt = f"""Based on the following website content for {domain}, provide a brief analysis:

Website Content: {website_content[:1000]}

Analysis:
Business Type: """
        
        try:
            response = self.generator(prompt, max_length=len(prompt.split()) + 100, num_return_sequences=1)
            generated_text = response[0]['generated_text']
            
            # Extract the analysis part
            analysis_start = generated_text.find("Analysis:")
            if analysis_start != -1:
                analysis = generated_text[analysis_start + len("Analysis:"):].strip()
            else:
                analysis = generated_text[len(prompt):].strip()
            
            # Parse the analysis (basic extraction)
            business_type = self.extract_business_type(website_content, domain)
            description = self.extract_business_description(website_content)
            
            return {
                "business_type": business_type,
                "description": description,
                "industry": self.determine_industry(website_content),
                "services": self.extract_services(website_content)
            }
        except Exception as e:
            # Fallback to rule-based analysis
            return self.fallback_business_analysis(website_content, domain)
    
    def generate_personalized_email(self, email_record, company_info: Dict, website_issues: List[str]) -> Dict:
        """Generate personalized email content"""
        
        first_name = email_record.first_name or "there"
        company_name = email_record.company_name or company_info.get("business_type", "your company")
        
        # Create the email structure using templates and some AI assistance
        subject = self.generate_subject_line(first_name, company_name, website_issues)
        
        # Generate email body sections
        intro = self.generate_intro_section(first_name, company_name, company_info)
        issues_section = self.generate_issues_section(website_issues)
        solution_section = self.generate_solution_section(company_info)
        cta_section = self.generate_cta_section(first_name)
        
        email_content = {
            "subject": subject,
            "intro": intro,
            "issues": issues_section,
            "solution": solution_section,
            "cta": cta_section,
            "personalization_tokens": {
                "first_name": first_name,
                "company_name": company_name,
                "domain": email_record.domain
            }
        }
        
        return email_content
    
    def extract_business_type(self, content: str, domain: str) -> str:
        """Extract business type from content"""
        content_lower = content.lower()
        
        # Define business type keywords
        business_types = {
            "restaurant": ["restaurant", "food", "dining", "menu", "cafe", "bistro"],
            "automotive": ["auto", "car", "repair", "mechanic", "vehicle", "automotive"],
            "medical": ["doctor", "medical", "clinic", "health", "hospital", "dental"],
            "legal": ["law", "lawyer", "attorney", "legal", "firm"],
            "retail": ["shop", "store", "retail", "shopping", "buy", "sell"],
            "technology": ["tech", "software", "IT", "computer", "development", "digital"],
            "real estate": ["real estate", "property", "homes", "realtor", "housing"],
            "fitness": ["gym", "fitness", "workout", "exercise", "personal trainer"],
            "beauty": ["beauty", "salon", "spa", "hair", "cosmetic", "skincare"],
            "education": ["school", "education", "learning", "training", "academy"]
        }
        
        for business_type, keywords in business_types.items():
            if any(keyword in content_lower for keyword in keywords):
                return business_type.title()
        
        # Extract from domain if no keywords found
        domain_words = re.findall(r'[a-zA-Z]+', domain.split('.')[0])
        if domain_words:
            return ' '.join(word.capitalize() for word in domain_words)
        
        return "Business"
    
    def extract_business_description(self, content: str) -> str:
        """Extract business description from content"""
        sentences = content.split('.')[:5]  # First 5 sentences
        description = '. '.join(sentences).strip()
        
        if len(description) > 200:
            description = description[:200] + "..."
        
        return description
    
    def determine_industry(self, content: str) -> str:
        """Determine industry from content"""
        return self.extract_business_type(content, "").lower()
    
    def extract_services(self, content: str) -> List[str]:
        """Extract services from content"""
        # Look for service-related keywords
        service_patterns = [
            r'we offer ([^.]+)',
            r'our services include ([^.]+)',
            r'services: ([^.]+)',
            r'we provide ([^.]+)'
        ]
        
        services = []
        content_lower = content.lower()
        
        for pattern in service_patterns:
            matches = re.findall(pattern, content_lower)
            for match in matches:
                services.extend([s.strip() for s in match.split(',') if s.strip()])
        
        return services[:5]  # Limit to 5 services
    
    def generate_subject_line(self, first_name: str, company_name: str, issues: List[str]) -> str:
        """Generate email subject line"""
        if len(issues) > 2:
            return f"{first_name}, {len(issues)} issues found on {company_name}'s website"
        elif issues:
            return f"{first_name}, improve {company_name}'s website performance"
        else:
            return f"{first_name}, let's enhance {company_name}'s online presence"
    
    def generate_intro_section(self, first_name: str, company_name: str, company_info: Dict) -> str:
        """Generate personalized intro section"""
        business_type = company_info.get("business_type", "business")
        
        intros = [
            f"Hi {first_name},\n\nI came across {company_name} and was impressed by your {business_type.lower()} offerings. Your dedication to serving customers really shows through your online presence.",
            f"Hello {first_name},\n\nI've been researching local {business_type.lower()} companies and {company_name} caught my attention. You're clearly doing great work in your industry.",
            f"Hi {first_name},\n\n{company_name} has a solid reputation in the {business_type.lower()} space. I noticed a few opportunities that could help you reach even more customers online."
        ]
        
        return intros[hash(first_name) % len(intros)]
    
    def generate_issues_section(self, issues: List[str]) -> str:
        """Generate issues section"""
        if not issues:
            return "While your website looks good, there are always opportunities for improvement in today's competitive digital landscape."
        
        formatted_issues = []
        for issue in issues[:5]:  # Limit to 5 issues
            formatted_issues.append(f"• {issue}")
        
        return "I noticed a few areas where your website could be optimized:\n\n" + "\n".join(formatted_issues)
    
    def generate_solution_section(self, company_info: Dict) -> str:
        """Generate solution section"""
        return """At NetWit, we specialize in helping businesses like yours maximize their online potential. Our comprehensive web optimization services include:

• SEO improvements to boost search engine rankings
• Performance optimization for faster loading times
• Mobile responsiveness enhancements
• Security upgrades and SSL implementation
• User experience improvements to increase conversions

We've helped hundreds of businesses increase their online visibility and customer engagement by up to 300%."""
    
    def generate_cta_section(self, first_name: str) -> str:
        """Generate call-to-action section"""
        return f"""Don't let these issues cost you potential customers, {first_name}. Every day you wait, competitors are gaining ground.

I'd love to show you exactly how we can transform your website's performance. Are you available for a quick 15-minute call this week to discuss your specific needs?

Click here to schedule a free consultation: [Schedule Call]

Best regards,
Dave Chatpar
NetWit Digital Solutions
dave@netwit.ca
(555) 123-4567"""
    
    def fallback_business_analysis(self, content: str, domain: str) -> Dict:
        """Fallback business analysis when AI fails"""
        return {
            "business_type": self.extract_business_type(content, domain),
            "description": self.extract_business_description(content),
            "industry": "general",
            "services": self.extract_services(content)
        }
