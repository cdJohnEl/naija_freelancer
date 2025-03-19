import requests
from bs4 import BeautifulSoup
import json
import firebase_admin
from firebase_admin import credentials, firestore
import uuid
from datetime import datetime
import time
import random
import os
import logging
import schedule
from job_generator import generate_job_listings, save_generated_jobs

# Set up logging
logging.basicConfig(
  level=logging.INFO,
  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
  handlers=[
      logging.FileHandler("job_scraper.log"),
      logging.StreamHandler()
  ]
)
logger = logging.getLogger("job_scraper")

# Initialize Firebase (if available)
try:
  cred = credentials.Certificate("firebase-key.json")
  firebase_admin.initialize_app(cred)
  db = firestore.client()
  logger.info("Firebase initialized successfully")
  use_firebase = True
except Exception as e:
  logger.warning(f"Firebase initialization failed: {e}")
  logger.info("Using local JSON storage instead")
  use_firebase = False

# Make sure the data directory exists
os.makedirs('static/data', exist_ok=True)

# Job sources configuration - using more reliable sources
JOB_SOURCES = [
  {
      "name": "LinkedIn Jobs API",
      "enabled": False,  # Disabled until API keys are set up
      "url_template": "https://api.linkedin.com/v2/jobSearch?keywords={query}&location=Nigeria",
      "queries": ["web developer", "software engineer", "designer", "marketing", "content writer"]
  },
  {
      "name": "GitHub Jobs",
      "enabled": False,  # GitHub Jobs API is deprecated
      "url_template": "https://jobs.github.com/positions.json?description={query}&location=Nigeria",
      "queries": ["developer", "designer", "marketing", "writer", "project manager"]
  },
  {
      "name": "Remotive API",
      "enabled": True,
      "url_template": "https://remotive.com/api/remote-jobs?search={query}",
      "queries": ["developer", "designer", "marketing", "writer", "project manager"]
  }
]

# User agent list to rotate and avoid being blocked
USER_AGENTS = [
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
  "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
]

def get_random_user_agent():
  """Return a random user agent from the list"""
  return random.choice(USER_AGENTS)

def scrape_remotive_api(query):
  """Fetch job listings from Remotive API"""
  jobs = []
  url = JOB_SOURCES[2]["url_template"].format(query=query.replace(" ", "+"))
  
  headers = {
      "User-Agent": get_random_user_agent(),
      "Accept": "application/json",
  }
  
  try:
      response = requests.get(url, headers=headers)
      response.raise_for_status()
      
      data = response.json()
      job_listings = data.get('jobs', [])
      
      for job_data in job_listings[:5]:  # Limit to 5 jobs per query
          try:
              title = job_data.get('title', '')
              company = job_data.get('company_name', '')
              location = job_data.get('candidate_required_location', 'Remote')
              
              # Make it Nigeria-focused
              if "worldwide" in location.lower() or "anywhere" in location.lower():
                  location = "Remote (Nigeria)"
              
              # Extract job description
              description = job_data.get('description', '')
              # Clean up HTML from description
              soup = BeautifulSoup(description, 'html.parser')
              description = soup.get_text()[:200] + "..."  # Truncate for brevity
              
              # Determine job level based on title
              level = "Entry level"
              if "senior" in title.lower() or "lead" in title.lower() or "manager" in title.lower():
                  level = "Senior level"
              elif "mid" in title.lower() or "intermediate" in title.lower():
                  level = "Mid level"
              
              # Generate tags based on job title and query
              tags = [query]
              if "developer" in title.lower() or "engineer" in title.lower():
                  tags.append("Development")
              if "design" in title.lower():
                  tags.append("Design")
              if "market" in title.lower():
                  tags.append("Marketing")
              if "content" in title.lower() or "writer" in title.lower():
                  tags.append("Content")
              
              # Generate a random salary range based on job level
              if level == "Senior level":
                  salary = "₦500,000 - ₦800,000"
              elif level == "Mid level":
                  salary = "₦300,000 - ₦500,000"
              else:
                  salary = "₦150,000 - ₦300,000"
              
              # Get the application URL
              apply_url = job_data.get('url', '')
              
              job = {
                  "id": str(uuid.uuid4()),
                  "title": title,
                  "company": company,
                  "company_logo": company[0].upper(),
                  "location": location,
                  "description": description,
                  "requirements": f"Experience with {query} required.",
                  "salary": salary,
                  "type": "Full-time",  # Default to full-time
                  "level": level,
                  "tags": tags,
                  "posted_at": datetime.now().isoformat(),
                  "remote": True,  # Remotive is for remote jobs
                  "source": "Remotive",
                  "source_url": apply_url,
                  "apply_url": apply_url  # Add the application URL
              }
              
              jobs.append(job)
              
          except Exception as e:
              logger.error(f"Error parsing Remotive job: {e}")
              continue
              
      logger.info(f"Scraped {len(jobs)} jobs from Remotive for query '{query}'")
      
  except Exception as e:
      logger.error(f"Error fetching from Remotive API: {e}")
  
  # Add a delay to avoid rate limiting
  time.sleep(random.uniform(1, 3))
  
  return jobs

def save_jobs_to_firebase(jobs):
  """Save job listings to Firebase"""
  if not use_firebase:
      logger.warning("Firebase not available, skipping Firebase save")
      return
  
  try:
      # Get existing jobs to avoid duplicates
      existing_jobs = {}
      jobs_ref = db.collection('jobs')
      for doc in jobs_ref.stream():
          job_data = doc.to_dict()
          if 'title' in job_data and 'company' in job_data:
              key = f"{job_data['title']}_{job_data['company']}"
              existing_jobs[key] = job_data
      
      # Add new jobs
      added_count = 0
      for job in jobs:
          key = f"{job['title']}_{job['company']}"
          if key not in existing_jobs:
              db.collection('jobs').add(job)
              added_count += 1
      
      logger.info(f"Added {added_count} new jobs to Firebase")
      
  except Exception as e:
      logger.error(f"Error saving to Firebase: {e}")

def save_jobs_to_json(jobs):
  """Save job listings to local JSON file"""
  try:
      # Load existing jobs
      existing_jobs = []
      if os.path.exists('static/data/mock-jobs.json'):
          with open('static/data/mock-jobs.json', 'r') as f:
              existing_jobs = json.load(f)
      
      # Create a dictionary of existing jobs to check for duplicates
      existing_dict = {}
      for job in existing_jobs:
          if 'title' in job and 'company' in job:
              key = f"{job['title']}_{job['company']}"
              existing_dict[key] = True
      
      # Add new jobs
      added_count = 0
      for job in jobs:
          key = f"{job['title']}_{job['company']}"
          if key not in existing_dict:
              existing_jobs.append(job)
              existing_dict[key] = True
              added_count += 1
      
      # Save back to file
      with open('static/data/mock-jobs.json', 'w') as f:
          json.dump(existing_jobs, f, indent=2)
      
      logger.info(f"Added {added_count} new jobs to JSON file")
      
  except Exception as e:
      logger.error(f"Error saving to JSON: {e}")

def run_scraper():
  """Run the job scraper for all configured sources and queries"""
  logger.info("Starting job scraper run")
  all_jobs = []
  
  # Scrape Remotive API
  if JOB_SOURCES[2]["enabled"]:
      for query in JOB_SOURCES[2]["queries"]:
          jobs = scrape_remotive_api(query)
          all_jobs.extend(jobs)
  
  # If we didn't get any jobs from scraping, generate some
  if len(all_jobs) == 0:
      logger.info("No jobs found from scraping. Generating mock jobs instead.")
      all_jobs = generate_job_listings(20)
  
  # Save jobs to Firebase if available
  if use_firebase:
      save_jobs_to_firebase(all_jobs)
  
  # Always save to JSON as a backup
  save_jobs_to_json(all_jobs)
  
  logger.info(f"Completed job scraper run, processed {len(all_jobs)} jobs")

def schedule_scraper():
  """Set up scheduled runs of the scraper"""
  # Run once at startup
  run_scraper()
  
  # Schedule to run every 6 hours
  schedule.every(6).hours.do(run_scraper)
  
  logger.info("Job scraper scheduled to run every 6 hours")
  
  # Keep the script running
  while True:
      schedule.run_pending()
      time.sleep(60)

if __name__ == "__main__":
  schedule_scraper()

