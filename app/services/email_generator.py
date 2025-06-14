from jinja2 import Template
from typing import Dict
import os

class EmailGenerator:
    def __init__(self):
        self.template_dir = "app/templates/"
    
    def generate_html_email(self, email_content: Dict, email_record, company_info: Dict) -> str:
        """Generate HTML email from template"""
        
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ subject }}</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f4f4f4;
        }
        .email-container {
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 3px solid #007bff;
        }
        .logo {
            font-size: 28px;
            font-weight: bold;
            color: #007bff;
            margin-bottom: 10px;
        }
        .tagline {
            color: #666;
            font-style: italic;
        }
        .intro {
            margin-bottom: 25px;
            font-size: 16px;
        }
        .issues-section {
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 20px;
            margin: 25px 0;
            border-radius: 5px;
        }
        .issues-title {
            font-weight: bold;
            color: #856404;
            margin-bottom: 15px;
            font-size: 18px;
        }
        .issues-list {
            list-style: none;
            padding: 0;
        }
        .issues-list li {
            margin: 10px 0;
            padding-left: 25px;
            position: relative;
        }
        .issues-list li:before {
            content: "⚠️";
            position: absolute;
            left: 0;
        }
        .solution-section {
            background-color: #d4edda;
            border-left: 4px solid #28a745;
            padding: 20px;
            margin: 25px 0;
            border-radius: 5px;
        }
        .solution-title {
            font-weight: bold;
            color: #155724;
            margin-bottom: 15px;
            font-size: 18px;
        }
        .benefits-list {
            list-style: none;
            padding: 0;
        }
        .benefits-list li {
            margin: 10px 0;
            padding-left: 25px;
            position: relative;
        }
        .benefits-list li:before {
            content: "✅";
            position: absolute;
            left: 0;
        }
        .cta-section {
            text-align: center;
            margin: 30px 0;
            padding: 25px;
            background: linear-gradient(135deg, #007bff, #0056b3);
            border-radius: 10px;
            color: white;
        }
        .cta-button {
            display: inline-block;
            background-color: #ffc107;
            color: #000;
            padding: 15px 30px;
            text-decoration: none;
            border-radius: 25px;
            font-weight: bold;
            font-size: 18px;
            margin: 15px 0;
            transition: all 0.3s ease;
        }
        .cta-button:hover {
            background-color: #ffcd39;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }
        .urgency {
            background-color: #f8d7da;
            border-left: 4px solid #dc3545;
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
            color: #721c24;
        }
        .signature {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 2px solid #eee;
            text-align: center;
        }
        .signature img {
            max-width: 150px;
            margin-bottom: 15px;
        }
        .contact-info {
            color: #666;
            font-size: 14px;
        }
        .stats {
            display: flex;
            justify-content: space-around;
            margin: 20px 0;
            text-align: center;
        }
        .stat-item {
            flex: 1;
            padding: 15px;
            background-color: #f8f9fa;
            margin: 0 10px;
            border-radius: 8px;
        }
        .stat-number {
            font-size: 24px;
            font-weight: bold;
            color: #007bff;
        }
        .stat-label {
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
        }
        @media (max-width: 600px) {
            body {
                padding: 10px;
            }
            .email-container {
                padding: 20px;
            }
            .stats {
                flex-direction: column;
            }
            .stat-item {
                margin: 5px 0;
            }
        }
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <div class="logo">NetWit</div>
            <div class="tagline">Digital Solutions That Drive Results</div>
        </div>
        
        <div class="intro">
            {{ intro | safe }}
        </div>
        
        {% if issues %}
        <div class="issues-section">
            <div class="issues-title">🔍 Website Analysis Results</div>
            <div>{{ issues | safe }}</div>
        </div>
        {% endif %}
        
        <div class="stats">
            <div class="stat-item">
                <div class="stat-number">{{ seo_score | default(0) }}</div>
                <div class="stat-label">SEO Score</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{{ loading_time | default(0) }}s</div>
                <div class="stat-label">Load Time</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{{ issues_count | default(0) }}</div>
                <div class="stat-label">Issues Found</div>
            </div>
        </div>
        
        <div class="solution-section">
            <div class="solution-title">🚀 How We Can Help</div>
            <div>{{ solution | safe }}</div>
        </div>
        
        <div class="urgency">
            <strong>⏰ Don't Wait!</strong> Every day these issues remain unfixed, you're potentially losing customers to competitors. Studies show that a 1-second delay in page load time can reduce conversions by 7%.
        </div>
        
        <div class="cta-section">
            <h3>Ready to Transform Your Website?</h3>
            <p>Let's discuss how we can boost your online performance</p>
            <a href="https://calendly.com/netwit/consultation" class="cta-button">Schedule Free Consultation</a>
            <p style="font-size: 14px; margin-top: 15px;">
                Or reply to this email to get started immediately
            </p>
        </div>
        
        <div class="signature">
            <div style="font-weight: bold; font-size: 18px; color: #007bff;">Dave Chatpar</div>
            <div style="font-style: italic; margin: 5px 0;">Digital Marketing Specialist</div>
            <div class="contact-info">
                <div>NetWit Digital Solutions</div>
                <div>📧 dave@netwit.ca | 📞 (555) 123-4567</div>
                <div>🌐 www.netwit.ca</div>
            </div>
        </div>
    </div>
</body>
</html>
        """
        
        template = Template(html_template)
        
        # Process issues for display
        issues_html = ""
        if isinstance(email_content.get('issues'), str):
            # Convert bullet points to HTML list
            issues_lines = email_content['issues'].split('\n')
            issues_html = "<ul class='issues-list'>"
            for line in issues_lines:
                if line.strip().startswith('•'):
                    issues_html += f"<li>{line.strip()[1:].strip()}</li>"
                elif line.strip():
                    issues_html += f"<li>{line.strip()}</li>"
            issues_html += "</ul>"
        
        # Process solution for display
        solution_html = email_content.get('solution', '').replace('\n', '<br>')
        if '•' in solution_html:
            solution_lines = solution_html.split('\n')
            solution_html = ""
            in_list = False
            for line in solution_lines:
                if '•' in line:
                    if not in_list:
                        solution_html += "<ul class='benefits-list'>"
                        in_list = True
                    solution_html += f"<li>{line.replace('•', '').strip()}</li>"
                else:
                    if in_list:
                        solution_html += "</ul>"
                        in_list = False
                    if line.strip():
                        solution_html += f"<p>{line.strip()}</p>"
            if in_list:
                solution_html += "</ul>"
        
        # Render the template
        html_content = template.render(
            subject=email_content.get('subject', ''),
            intro=email_content.get('intro', ''),
            issues=issues_html,
            solution=solution_html,
            first_name=email_record.first_name or 'there',
            company_name=email_record.company_name or 'your company',
            seo_score=company_info.get('seo_score', 0),
            loading_time=round(company_info.get('loading_time', 0), 1),
            issues_count=len(company_info.get('issues', []))
        )
        
        return html_content
    
    def generate_text_email(self, email_content: Dict, email_record) -> str:
        """Generate plain text version of email"""
        
        text_parts = []
        
        # Subject (for reference)
        text_parts.append(f"Subject: {email_content.get('subject', '')}")
        text_parts.append("=" * 50)
        
        # Intro
        if email_content.get('intro'):
            text_parts.append(email_content['intro'])
        
        # Issues
        if email_content.get('issues'):
            text_parts.append("\n🔍 WEBSITE ANALYSIS RESULTS:")
            text_parts.append(email_content['issues'])
        
        # Solution
        if email_content.get('solution'):
            text_parts.append("\n🚀 HOW WE CAN HELP:")
            text_parts.append(email_content['solution'])
        
        # CTA
        if email_content.get('cta'):
            text_parts.append(email_content['cta'])
        else:
            text_parts.append(f"""
Don't let these issues cost you potential customers. Every day you wait, competitors are gaining ground.

I'd love to show you exactly how we can transform your website's performance. Are you available for a quick 15-minute call this week?

Schedule your free consultation: https://calendly.com/netwit/consultation

Best regards,
Dave Chatpar
NetWit Digital Solutions
dave@netwit.ca
(555) 123-4567
""")
        
        return "\n\n".join(text_parts)
