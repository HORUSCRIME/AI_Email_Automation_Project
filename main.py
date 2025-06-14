from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from typing import List, Dict, Optional
import json
import asyncio
from datetime import datetime
import uuid
import pandas as pd
import io
import traceback

from .models.schemas import EmailRecord, EmailJob, EmailUpload
from .services.email_processor import EmailProcessor
from .services.web_scraper import WebScraper
from .services.llm_service import LLMService
from .services.email_generator import EmailGenerator
from .services.email_sender import EmailSender
from .utils.validators import EmailValidator
from .utils.helpers import Helpers

# Initialize FastAPI app
app = FastAPI(
    title="AI Email Automation System",
    description="Intelligent email automation with personalized content generation",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
email_processor = EmailProcessor()
web_scraper = WebScraper()
llm_service = LLMService()
email_generator = EmailGenerator()
email_sender = EmailSender()

# Create necessary directories
Helpers.create_directories()

# Store active jobs
active_jobs: Dict[str, EmailJob] = {}

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    print("🚀 AI Email Automation System Starting Up...")
    Helpers.log_activity("system_startup", {"message": "Application started"})

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main upload interface"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Email Automation System</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #333;
            }
            .container {
                background: white;
                padding: 40px;
                border-radius: 15px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            }
            .header {
                text-align: center;
                margin-bottom: 40px;
            }
            .logo {
                font-size: 36px;
                font-weight: bold;
                background: linear-gradient(45deg, #667eea, #764ba2);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 10px;
            }
            .subtitle {
                color: #666;
                font-size: 18px;
            }
            .upload-section {
                border: 3px dashed #667eea;
                border-radius: 10px;
                padding: 40px;
                text-align: center;
                margin: 30px 0;
                transition: all 0.3s ease;
            }
            .upload-section:hover {
                border-color: #764ba2;
                background-color: #f8f9ff;
            }
            .upload-btn {
                background: linear-gradient(45deg, #667eea, #764ba2);
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 25px;
                font-size: 16px;
                cursor: pointer;
                transition: transform 0.3s ease;
            }
            .upload-btn:hover {
                transform: translateY(-2px);
            }
            .features {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin: 40px 0;
            }
            .feature-card {
                padding: 20px;
                border-radius: 10px;
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                color: white;
                text-align: center;
            }
            .feature-icon {
                font-size: 30px;
                margin-bottom: 10px;
            }
            .progress-section {
                display: none;
                margin: 30px 0;
            }
            .progress-bar {
                width: 100%;
                height: 20px;
                background: #f0f0f0;
                border-radius: 10px;
                overflow: hidden;
            }
            .progress-fill {
                height: 100%;
                background: linear-gradient(45deg, #667eea, #764ba2);
                width: 0%;
                transition: width 0.3s ease;
            }
            .results-section {
                display: none;
                margin: 30px 0;
            }
            .result-card {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 10px;
                margin: 10px 0;
            }
            .status-processing { color: #ffa500; }
            .status-completed { color: #28a745; }
            .status-failed { color: #dc3545; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">AI Email Automation</div>
                <div class="subtitle">Intelligent, Personalized Email Campaigns</div>
            </div>
            
            <div class="upload-section">
                <h3>📧 Upload Your Email List</h3>
                <p>Support for CSV, Excel, and text files</p>
                <input type="file" id="emailFile" accept=".csv,.xlsx,.txt" style="display: none;">
                <button class="upload-btn" onclick="document.getElementById('emailFile').click()">
                    Choose File
                </button>
                <div id="fileName" style="margin-top: 10px; font-style: italic;"></div>
                <button id="processBtn" class="upload-btn" onclick="processEmails()" style="display: none; margin-top: 20px;">
                    🚀 Start Processing
                </button>
            </div>
            
            <div class="features">
                <div class="feature-card">
                    <div class="feature-icon">🤖</div>
                    <h4>AI-Powered Analysis</h4>
                    <p>Advanced website analysis using LLM models</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🎯</div>
                    <h4>Personalized Content</h4>
                    <p>Custom emails tailored to each business</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">📊</div>
                    <h4>Performance Tracking</h4>
                    <p>Detailed analytics and delivery reports</p>
                </div>
            </div>
            
            <div class="progress-section" id="progressSection">
                <h4>Processing Status</h4>
                <div class="progress-bar">
                    <div class="progress-fill" id="progressFill"></div>
                </div>
                <div id="progressText">Initializing...</div>
                <div id="currentEmail" style="margin-top: 10px; font-size: 14px; color: #666;"></div>
            </div>
            
            <div class="results-section" id="resultsSection">
                <h4>📊 Processing Results</h4>
                <div id="resultsContainer">
                    <!-- Results will be populated here -->
                </div>
            </div>
        </div>
        
        <script>
            let selectedFile = null;
            let currentJobId = null;
            
            document.getElementById('emailFile').addEventListener('change', function(e) {
                selectedFile = e.target.files[0];
                if (selectedFile) {
                    document.getElementById('fileName').textContent = `Selected: ${selectedFile.name}`;
                    document.getElementById('processBtn').style.display = 'inline-block';
                }
            });
            
            async function processEmails() {
                if (!selectedFile) {
                    alert('Please select a file first');
                    return;
                }
                
                const formData = new FormData();
                formData.append('file', selectedFile);
                
                // Show progress section
                document.getElementById('progressSection').style.display = 'block';
                document.getElementById('progressText').textContent = 'Uploading file...';
                
                try {
                    const response = await fetch('/upload-emails', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const result = await response.json();
                    
                    if (result.job_id) {
                        currentJobId = result.job_id;
                        pollJobStatus(currentJobId);
                    } else {
                        throw new Error(result.detail || 'Upload failed');
                    }
                } catch (error) {
                    alert('Error: ' + error.message);
                    console.error('Error:', error);
                }
            }
            
            async function pollJobStatus(jobId) {
                const pollInterval = setInterval(async () => {
                    try {
                        const response = await fetch(`/job-status/${jobId}`);
                        const job = await response.json();
                        
                        updateProgress(job);
                        
                        if (job.status === 'completed' || job.status === 'failed') {
                            clearInterval(pollInterval);
                            showResults(job);
                        }
                    } catch (error) {
                        console.error('Error polling job status:', error);
                        clearInterval(pollInterval);
                    }
                }, 2000); // Poll every 2 seconds
            }
            
            function updateProgress(job) {
                const progressFill = document.getElementById('progressFill');
                const progressText = document.getElementById('progressText');
                const currentEmail = document.getElementById('currentEmail');
                
                let progress = 0;
                let statusText = 'Processing...';
                
                if (job.progress) {
                    progress = job.progress.percentage || 0;
                    statusText = job.progress.current_step || 'Processing...';
                    
                    if (job.progress.current_email) {
                        currentEmail.textContent = `Processing: ${job.progress.current_email}`;
                    }
                }
                
                switch (job.status) {
                    case 'pending':
                        progress = 10;
                        statusText = 'Queued for processing...';
                        break;
                    case 'processing':
                        // Progress updated from job.progress above
                        break;
                    case 'completed':
                        progress = 100;
                        statusText = 'Completed successfully!';
                        break;
                    case 'failed':
                        progress = 100;
                        statusText = 'Processing failed';
                        break;
                }
                
                progressFill.style.width = progress + '%';
                progressText.textContent = statusText;
            }
            
            function showResults(job) {
                const resultsSection = document.getElementById('resultsSection');
                const resultsContainer = document.getElementById('resultsContainer');
                
                resultsSection.style.display = 'block';
                
                if (job.status === 'completed' && job.results) {
                    resultsContainer.innerHTML = `
                        <div class="result-card">
                            <h5>✅ Processing Complete</h5>
                            <p><strong>Total Emails:</strong> ${job.results.total_emails || 0}</p>
                            <p><strong>Successfully Processed:</strong> ${job.results.emails_processed || 0}</p>
                            <p><strong>Successfully Sent:</strong> ${job.results.emails_sent || 0}</p>
                            <p><strong>Failed:</strong> ${job.results.emails_failed || 0}</p>
                            <p><strong>Success Rate:</strong> ${job.results.success_rate || 0}%</p>
                            <p><strong>Processing Time:</strong> ${job.results.processing_time || 'N/A'}</p>
                        </div>
                        <div class="result-card">
                            <h5>📊 Detailed Report</h5>
                            <button class="upload-btn" onclick="downloadReport('${job.id}')">
                                Download Full Report
                            </button>
                            <button class="upload-btn" onclick="viewJobLogs('${job.id}')" style="margin-left: 10px;">
                                View Logs
                            </button>
                        </div>
                    `;
                } else {
                    resultsContainer.innerHTML = `
                        <div class="result-card">
                            <h5>❌ Processing Failed</h5>
                            <p>Error: ${job.error_message || 'Unknown error occurred'}</p>
                            <button class="upload-btn" onclick="viewJobLogs('${job.id}')">
                                View Error Logs
                            </button>
                        </div>
                    `;
                }
            }
            
            async function downloadReport(jobId) {
                try {
                    const response = await fetch(`/download-report/${jobId}`);
                    const blob = await response.blob();
                    
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.style.display = 'none';
                    a.href = url;
                    a.download = `email_report_${jobId}.json`;
                    
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                } catch (error) {
                    alert('Error downloading report: ' + error.message);
                }
            }
            
            async function viewJobLogs(jobId) {
                try {
                    const response = await fetch(`/job-logs/${jobId}`);
                    const logs = await response.json();
                    
                    // Create a simple modal to display logs
                    const logWindow = window.open('', '_blank', 'width=800,height=600');
                    logWindow.document.write(`
                        <html>
                            <head><title>Job Logs - ${jobId}</title></head>
                            <body style="font-family: monospace; padding: 20px;">
                                <h2>Job Logs - ${jobId}</h2>
                                <pre>${JSON.stringify(logs, null, 2)}</pre>
                            </body>
                        </html>
                    `);
                } catch (error) {
                    alert('Error viewing logs: ' + error.message);
                }
            }
        </script>
    </body>
    </html>
    """
    return html_content

@app.post("/upload-emails")
async def upload_emails(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """Upload and process email list"""
    
    # Validate file type
    if not file.filename.endswith(('.csv', '.xlsx', '.txt')):
        raise HTTPException(status_code=400, detail="Unsupported file type. Please upload CSV, Excel, or text files.")
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Parse emails from file
        emails = []
        if file.filename.endswith('.csv'):
            # Parse CSV file
            df = pd.read_csv(io.StringIO(file_content.decode('utf-8')))
            # Look for email column (flexible column names)
            email_column = None
            for col in df.columns:
                if 'email' in col.lower() or 'mail' in col.lower():
                    email_column = col
                    break
            
            if email_column:
                emails = df[email_column].dropna().tolist()
            else:
                # If no email column found, assume first column contains emails
                emails = df.iloc[:, 0].dropna().tolist()
                
        elif file.filename.endswith('.xlsx'):
            # Parse Excel file
            df = pd.read_excel(io.BytesIO(file_content))
            email_column = None
            for col in df.columns:
                if 'email' in col.lower() or 'mail' in col.lower():
                    email_column = col
                    break
            
            if email_column:
                emails = df[email_column].dropna().tolist()
            else:
                emails = df.iloc[:, 0].dropna().tolist()
                
        elif file.filename.endswith('.txt'):
            # Parse text file (one email per line)
            emails = file_content.decode('utf-8').strip().split('\n')
            emails = [email.strip() for email in emails if email.strip()]
        
        # Validate emails
        valid_emails = []
        for email in emails:
            if EmailValidator.is_valid_email(email):
                valid_emails.append(email)
        
        if not valid_emails:
            raise HTTPException(status_code=400, detail="No valid email addresses found in the file.")
        
        # Create job
        job_id = str(uuid.uuid4())
        job = EmailJob(
            id=job_id,
            status="pending",
            created_at=datetime.now(),
            total_emails=len(valid_emails),
            emails=valid_emails
        )
        
        active_jobs[job_id] = job
        
        # Start background processing
        background_tasks.add_task(process_email_job, job_id, valid_emails)
        
        Helpers.log_activity("email_upload", {
            "job_id": job_id,
            "filename": file.filename,
            "total_emails": len(valid_emails)
        })
        
        return JSONResponse({
            "job_id": job_id,
            "message": f"Successfully uploaded {len(valid_emails)} valid email addresses",
            "total_emails": len(valid_emails)
        })
        
    except Exception as e:
        Helpers.log_activity("upload_error", {"filename": file.filename, "error": str(e)})
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

async def process_email_job(job_id: str, emails: List[str]):
    """Background task to process email job"""
    job = active_jobs.get(job_id)
    if not job:
        return
    
    try:
        job.status = "processing"
        job.started_at = datetime.now()
        
        results = []
        processed_count = 0
        sent_count = 0
        failed_count = 0
        
        for i, email in enumerate(emails):
            try:
                # Update progress
                progress_percentage = int((i / len(emails)) * 100)
                job.progress = {
                    "percentage": progress_percentage,
                    "current_step": f"Processing email {i+1} of {len(emails)}",
                    "current_email": email
                }
                
                # Process single email
                email_record = await email_processor.process_email(email)
                
                if email_record:
                    # Scrape website
                    website_data = await web_scraper.scrape_website(email_record.domain)
                    
                    if website_data:
                        # Generate LLM analysis
                        llm_analysis = await llm_service.analyze_website(
                            email_record.company_name or email_record.domain,
                            website_data
                        )
                        
                        # Generate personalized email
                        email_content = await email_generator.generate_email(
                            email_record, llm_analysis
                        )
                        
                        # Send email
                        email_sent = await email_sender.send_email(
                            email_record.email,
                            email_content
                        )
                        
                        if email_sent:
                            sent_count += 1
                        else:
                            failed_count += 1
                        
                        results.append({
                            "email": email,
                            "status": "sent" if email_sent else "failed",
                            "first_name": email_record.first_name,
                            "company": email_record.company_name or email_record.domain,
                            "analysis": llm_analysis
                        })
                    else:
                        failed_count += 1
                        results.append({
                            "email": email,
                            "status": "failed",
                            "error": "Website scraping failed"
                        })
                else:
                    failed_count += 1
                    results.append({
                        "email": email,
                        "status": "failed",
                        "error": "Email processing failed"
                    })
                
                processed_count += 1
                
                # Small delay to avoid overwhelming servers
                await asyncio.sleep(0.5)
                
            except Exception as e:
                failed_count += 1
                results.append({
                    "email": email,
                    "status": "failed",
                    "error": str(e)
                })
                
                Helpers.log_activity("email_processing_error", {
                    "job_id": job_id,
                    "email": email,
                    "error": str(e)
                })
        
        # Calculate results
        success_rate = (sent_count / len(emails)) * 100 if emails else 0
        processing_time = str(datetime.now() - job.started_at) if job.started_at else "N/A"
        
        job.status = "completed"
        job.completed_at = datetime.now()
        job.results = {
            "total_emails": len(emails),
            "emails_processed": processed_count,
            "emails_sent": sent_count,
            "emails_failed": failed_count,
            "success_rate": round(success_rate, 2),
            "processing_time": processing_time,
            "detailed_results": results
        }
        
        # Save results to file
        results_file = f"data/results/job_{job_id}_results.json"
        os.makedirs(os.path.dirname(results_file), exist_ok=True)
        with open(results_file, 'w') as f:
            json.dump(job.results, f, indent=2, default=str)
        
        Helpers.log_activity("job_completed", {
            "job_id": job_id,
            "total_emails": len(emails),
            "success_rate": success_rate,
            "processing_time": processing_time
        })
        
    except Exception as e:
        job.status = "failed"
        job.error_message = str(e)
        job.completed_at = datetime.now()
        
        Helpers.log_activity("job_failed", {
            "job_id": job_id,
            "error": str(e),
            "traceback": traceback.format_exc()
        })

@app.get("/job-status/{job_id}")
async def get_job_status(job_id: str):
    """Get the status of a processing job"""
    job = active_jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job

@app.get("/download-report/{job_id}")
async def download_report(job_id: str):
    """Download detailed report for a job"""
    job = active_jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    results_file = f"data/results/job_{job_id}_results.json"
    if os.path.exists(results_file):
        return FileResponse(
            results_file,
            media_type="application/json",
            filename=f"email_report_{job_id}.json"
        )
    else:
        # Return job results directly if file doesn't exist
        return JSONResponse(job.results or {})

@app.get("/job-logs/{job_id}")
async def get_job_logs(job_id: str):
    """Get logs for a specific job"""
    job = active_jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Read activity logs related to this job
    logs = Helpers.get_job_logs(job_id)
    return logs

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_jobs": len(active_jobs),
        "services": {
            "email_processor": "active",
            "web_scraper": "active", 
            "llm_service": "active",
            "email_generator": "active",
            "email_sender": "active"
        }
    }

@app.get("/jobs")
async def list_jobs():
    """List all jobs"""
    jobs_summary = []
    for job_id, job in active_jobs.items():
        jobs_summary.append({
            "id": job_id,
            "status": job.status,
            "created_at": job.created_at,
            "total_emails": job.total_emails,
            "progress": job.progress
        })
    
    return {"jobs": jobs_summary}

@app.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    """Delete a job from memory"""
    if job_id in active_jobs:
        del active_jobs[job_id]
        return {"message": f"Job {job_id} deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Job not found")

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    Helpers.log_activity("http_error", {
        "status_code": exc.status_code,
        "detail": exc.detail,
        "url": str(request.url)
    })
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    Helpers.log_activity("general_error", {
        "error": str(exc),
        "url": str(request.url),
        "traceback": traceback.format_exc()
    })
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    # Ensure data directories exist
    os.makedirs("data/logs", exist_ok=True)
    os.makedirs("data/results", exist_ok=True)
    os.makedirs("data/emails", exist_ok=True)
    
    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )