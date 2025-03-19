from flask import Flask, render_template, request, jsonify, redirect, url_for
import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
from datetime import datetime, timedelta
import uuid
import threading
import time

app = Flask(__name__)

# Initialize Firebase
try:
    cred = credentials.Certificate("naijafreelance-802e2-firebase-adminsdk-fbsvc-756f27e951.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("Firebase initialized successfully")
    use_firebase = True
except Exception as e:
    print(f"Error initializing Firebase: {e}")
    # For development, we'll create a mock database
    db = None
    use_firebase = False

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/resume-builder')
def resume_builder():
    return render_template('resume-builder.html')

@app.route('/portfolio')
def portfolio():
    return render_template('portfolio.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/upload-job')
def upload_job():
    return render_template('upload-job.html')

@app.route('/about')
def about():
    return render_template('about.html')

# API Routes
@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    if use_firebase:
        try:
            jobs_ref = db.collection('jobs')
            jobs = [doc.to_dict() for doc in jobs_ref.stream()]
            return jsonify(jobs)
        except Exception as e:
            print(f"Firebase error: {e}")
            return jsonify({"error": str(e)}), 500
    else:
        # Mock data for development
        try:
            # Ensure the directory exists
            os.makedirs('static/data', exist_ok=True)
            
            # Create mock data if it doesn't exist
            if not os.path.exists('static/data/mock-jobs.json'):
                from job_generator import save_generated_jobs
                save_generated_jobs(20)
                
            # Read the mock data
            with open('static/data/mock-jobs.json', 'r') as f:
                jobs = json.load(f)
            return jsonify(jobs)
        except Exception as e:
            print(f"Mock data error: {e}")
            # If there's an error, create and return hardcoded mock data
            return jsonify(create_mock_jobs_hardcoded())

@app.route('/api/jobs', methods=['POST'])
def add_job():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    job_data = request.get_json()
    
    # Validate required fields
    required_fields = ['title', 'company', 'location', 'description', 'salary', 'type']
    for field in required_fields:
        if field not in job_data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    # Add timestamp and ID
    job_data['posted_at'] = datetime.now().isoformat()
    job_data['id'] = str(uuid.uuid4())
    
    if use_firebase:
        try:
            db.collection('jobs').add(job_data)
            return jsonify({"success": True, "message": "Job added successfully"}), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        # Save to JSON file
        try:
            # Load existing jobs
            existing_jobs = []
            if os.path.exists('static/data/mock-jobs.json'):
                with open('static/data/mock-jobs.json', 'r') as f:
                    existing_jobs = json.load(f)
            
            # Add new job
            existing_jobs.append(job_data)
            
            # Save back to file
            with open('static/data/mock-jobs.json', 'w') as f:
                json.dump(existing_jobs, f, indent=2)
                
            return jsonify({"success": True, "message": "Job added successfully"}), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@app.route('/api/jobs/<job_id>', methods=['GET'])
def get_job(job_id):
    if use_firebase:
        try:
            jobs_ref = db.collection('jobs')
            query = jobs_ref.where('id', '==', job_id).limit(1)
            jobs = [doc.to_dict() for doc in query.stream()]
            
            if not jobs:
                return jsonify({"error": "Job not found"}), 404
                
            return jsonify(jobs[0])
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        # Mock data for development
        try:
            with open('static/data/mock-jobs.json', 'r') as f:
                jobs = json.load(f)
            
            for job in jobs:
                if job['id'] == job_id:
                    return jsonify(job)
            
            return jsonify({"error": "Job not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@app.route('/api/contact', methods=['POST'])
def submit_contact():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    contact_data = request.get_json()
    
    # Validate required fields
    required_fields = ['name', 'email', 'message']
    for field in required_fields:
        if field not in contact_data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    if use_firebase:
        try:
            db.collection('contacts').add(contact_data)
            return jsonify({"success": True, "message": "Message sent successfully"}), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        # Mock response for development
        return jsonify({"success": True, "message": "Message sent successfully"}), 201

@app.route('/api/resumes', methods=['POST'])
def save_resume():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    resume_data = request.get_json()
    
    # Validate required fields
    required_fields = ['name', 'email', 'skills', 'experience']
    for field in required_fields:
        if field not in resume_data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    if use_firebase:
        try:
            db.collection('resumes').add(resume_data)
            return jsonify({"success": True, "message": "Resume saved successfully"}), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        # Mock response for development
        return jsonify({"success": True, "message": "Resume saved successfully"}), 201

# Add a function to create mock jobs data (fallback)
def create_mock_jobs_hardcoded():
    return [
        {
            "id": "1",
            "title": "UX Researcher",
            "company": "WebFlow",
            "company_logo": "W",
            "location": "California, CA",
            "description": "Join our team to conduct user research and improve our product experience.",
            "requirements": "3+ years of experience with user research methods.",
            "salary": "₦600,000 - ₦800,000",
            "type": "Full-time",
            "level": "Senior level",
            "tags": ["UX", "Research", "Design"],
            "posted_at": "2023-03-07T12:00:00",
            "remote": True
        },
        {
            "id": "2",
            "title": "Quality Assurance",
            "company": "Nation",
            "company_logo": "N",
            "location": "Idaho, ID",
            "description": "Ensure the quality of our products through rigorous testing.",
            "requirements": "Experience with QA methodologies and testing tools.",
            "salary": "₦450,000 - ₦550,000",
            "type": "Full-time",
            "level": "Senior level",
            "tags": ["QA", "Testing", "Quality"],
            "posted_at": "2023-03-06T10:30:00",
            "remote": True
        },
        {
            "id": "3",
            "title": "Senior Dev",
            "company": "Zapier",
            "company_logo": "Z",
            "location": "Oklahoma, OK",
            "description": "Lead development efforts for our automation platform.",
            "requirements": "5+ years of experience with web development.",
            "salary": "₦700,000 - ₦900,000",
            "type": "Full-time",
            "level": "Senior level",
            "tags": ["Development", "JavaScript", "Python"],
            "posted_at": "2023-03-01T09:15:00",
            "remote": True
        }
    ]

# Check if scraping is needed
def should_run_scraper():
    """Check if we need to run the scraper based on last run time"""
    try:
        if os.path.exists('static/data/last_scrape.txt'):
            with open('static/data/last_scrape.txt', 'r') as f:
                last_scrape_str = f.read().strip()
                last_scrape = datetime.fromisoformat(last_scrape_str)
                # Run if more than 6 hours have passed
                return datetime.now() - last_scrape > timedelta(hours=6)
        return True  # No record of last scrape, so run it
    except Exception:
        return True  # If there's any error, run the scraper

# Update the last scrape time
def update_last_scrape_time():
    """Update the last scrape time"""
    try:
        os.makedirs('static/data', exist_ok=True)
        with open('static/data/last_scrape.txt', 'w') as f:
            f.write(datetime.now().isoformat())
    except Exception as e:
        print(f"Error updating last scrape time: {e}")

# Run the job generator in a background thread
def run_background_job_generator():
    """Run the job generator in a background thread"""
    try:
        from job_generator import save_generated_jobs
        save_generated_jobs(20)
        update_last_scrape_time()
        print("Successfully generated mock jobs")
    except Exception as e:
        print(f"Error running job generator: {e}")

if __name__ == '__main__':
    # Create directory for mock data if it doesn't exist
    os.makedirs('static/data', exist_ok=True)
    
    # Create mock jobs data if it doesn't exist
    if not os.path.exists('static/data/mock-jobs.json'):
        print("No mock jobs found. Generating initial job data...")
        run_background_job_generator()
    
    # Check if we should refresh the job data
    if should_run_scraper():
        print("Starting background job generator...")
        # Run the generator in a background thread
        generator_thread = threading.Thread(target=run_background_job_generator)
        generator_thread.daemon = True  # This ensures the thread will exit when the main program exits
        generator_thread.start()
    
    app.run(debug=True)

