"""
One-time script to update existing mock jobs with application URLs
Run this to update existing mock jobs with application URLs
"""

import json
import os
import uuid

def update_mock_jobs_with_apply_urls():
  """Update existing mock jobs with application URLs"""
  try:
      # Ensure the directory exists
      os.makedirs('static/data', exist_ok=True)
      
      # Check if mock jobs file exists
      if not os.path.exists('static/data/mock-jobs.json'):
          print("Mock jobs file not found. Please run job_generator.py first.")
          return
      
      # Load existing jobs
      with open('static/data/mock-jobs.json', 'r') as f:
          jobs = json.load(f)
      
      # Count jobs that need updating
      jobs_to_update = [job for job in jobs if 'apply_url' not in job]
      print(f"Found {len(jobs_to_update)} jobs that need application URLs added.")
      
      # Update jobs without apply_url
      for job in jobs:
          if 'apply_url' not in job:
              # For generated jobs, create a mock URL
              if job.get('generated', False) or job.get('source') == 'NaijaFreelance':
                  company_slug = job['company'].lower().replace(" ", "")
                  job_id = job['id']
                  job['apply_url'] = f"https://careers.{company_slug}.com/jobs/{job_id}"
              # For scraped jobs from Remotive, use the source_url if available
              elif job.get('source') == 'Remotive' and 'source_url' in job:
                  job['apply_url'] = job['source_url']
              # Otherwise, create a generic application URL
              else:
                  job['apply_url'] = f"https://naijafreelance.com/apply/{job['id']}"
      
      # Save updated jobs back to file
      with open('static/data/mock-jobs.json', 'w') as f:
          json.dump(jobs, f, indent=2)
      
      print(f"Successfully updated {len(jobs_to_update)} jobs with application URLs.")
      
  except Exception as e:
      print(f"Error updating mock jobs: {e}")

if __name__ == "__main__":
  update_mock_jobs_with_apply_urls()
  print("Done! All mock jobs now have application URLs.")

