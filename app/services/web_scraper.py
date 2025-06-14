import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse
import ssl
import socket

class WebScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def scrape_website(self, domain: str) -> Dict:
        """Scrape website and analyze for issues"""
        url = f"https://{domain}"
        
        try:
            # Try HTTPS first, then HTTP
            response = self.session.get(url, timeout=10, verify=True)
        except:
            try:
                url = f"http://{domain}"
                response = self.session.get(url, timeout=10)
            except Exception as e:
                return {"error": f"Failed to access website: {str(e)}"}
        
        if response.status_code != 200:
            return {"error": f"Website returned status code: {response.status_code}"}
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract website information
        website_info = {
            "url": url,
            "title": self.extract_title(soup),
            "description": self.extract_description(soup),
            "headings": self.extract_headings(soup),
            "content": self.extract_content(soup),
            "issues": self.analyze_issues(soup, response, url),
            "loading_time": response.elapsed.total_seconds(),
            "ssl_enabled": url.startswith('https://'),
            "mobile_friendly": self.check_mobile_friendly(soup),
            "seo_score": self.calculate_seo_score(soup, response)
        }
        
        return website_info
    
    def extract_title(self, soup: BeautifulSoup) -> str:
        title_tag = soup.find('title')
        return title_tag.get_text().strip() if title_tag else ""
    
    def extract_description(self, soup: BeautifulSoup) -> str:
        # Try meta description first
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc['content'].strip()
        
        # Try Open Graph description
        og_desc = soup.find('meta', attrs={'property': 'og:description'})
        if og_desc and og_desc.get('content'):
            return og_desc['content'].strip()
        
        # Try first paragraph
        first_p = soup.find('p')
        if first_p:
            return first_p.get_text().strip()[:200]
        
        return ""
    
    def extract_headings(self, soup: BeautifulSoup) -> Dict[str, List[str]]:
        headings = {}
        for i in range(1, 7):
            h_tags = soup.find_all(f'h{i}')
            if h_tags:
                headings[f'h{i}'] = [tag.get_text().strip() for tag in h_tags]
        return headings
    
    def extract_content(self, soup: BeautifulSoup) -> str:
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text content
        text = soup.get_text()
        
        # Clean up text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text[:2000]  # Limit content length
    
    def analyze_issues(self, soup: BeautifulSoup, response: requests.Response, url: str) -> List[str]:
        issues = []
        
        # SEO Issues
        if not soup.find('title') or len(soup.find('title').get_text()) < 30:
            issues.append("Missing or too short page title (SEO)")
        
        if not soup.find('meta', attrs={'name': 'description'}):
            issues.append("Missing meta description (SEO)")
        
        if not soup.find('h1'):
            issues.append("Missing H1 heading (SEO)")
        
        # Performance Issues
        if response.elapsed.total_seconds() > 3:
            issues.append("Slow loading speed (>3 seconds)")
        
        # Security Issues
        if not url.startswith('https://'):
            issues.append("No SSL certificate (Security)")
        
        # Accessibility Issues
        images = soup.find_all('img')
        images_without_alt = [img for img in images if not img.get('alt')]
        if images_without_alt:
            issues.append(f"{len(images_without_alt)} images missing alt text (Accessibility)")
        
        # Mobile Responsiveness
        if not self.check_mobile_friendly(soup):
            issues.append("Not mobile-friendly (Responsive Design)")
        
        # Content Issues
        if len(self.extract_content(soup)) < 300:
            issues.append("Insufficient content (Content Quality)")
        
        return issues
    
    def check_mobile_friendly(self, soup: BeautifulSoup) -> bool:
        # Check for viewport meta tag
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        if not viewport:
            return False
        
        # Check for responsive CSS classes or media queries (basic check)
        # This is a simplified check - in reality, you'd need more sophisticated analysis
        return True
    
    def calculate_seo_score(self, soup: BeautifulSoup, response: requests.Response) -> int:
        score = 100
        
        # Title check
        title = soup.find('title')
        if not title or len(title.get_text()) < 30:
            score -= 15
        
        # Meta description
        if not soup.find('meta', attrs={'name': 'description'}):
            score -= 15
        
        # H1 tag
        if not soup.find('h1'):
            score -= 10
        
        # Loading speed
        if response.elapsed.total_seconds() > 3:
            score -= 10
        
        # SSL
        if not response.url.startswith('https://'):
            score -= 10
        
        # Images alt text
        images = soup.find_all('img')
        if images:
            images_without_alt = [img for img in images if not img.get('alt')]
            score -= min(20, len(images_without_alt) * 2)
        
        return max(0, score)