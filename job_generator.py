"""
Job Generator - Creates realistic job listings when scraping fails
This serves as a fallback to ensure the job board always has fresh content
"""

import json
import random
import uuid
from datetime import datetime, timedelta
import os

# Nigerian cities for more realistic job locations
NIGERIAN_CITIES = [
    "Lagos", "Abuja", "Port Harcourt", "Kano", "Ibadan", 
    "Kaduna", "Enugu", "Benin City", "Owerri", "Calabar",
    "Warri", "Uyo", "Jos", "Abeokuta", "Onitsha", "Maiduguri"
]

# Job titles by category
JOB_CATEGORIES = {
    "Development": [
        "Frontend Developer", "Backend Developer", "Full Stack Developer", 
        "Mobile App Developer", "WordPress Developer", "React Developer",
        "Python Developer", "JavaScript Developer", "PHP Developer",
        "Software Engineer", "DevOps Engineer", "Node.js Developer"
    ],
    "Design": [
        "UI/UX Designer", "Graphic Designer", "Product Designer",
        "Web Designer", "Logo Designer", "Brand Identity Designer",
        "Illustrator", "Motion Designer", "3D Designer"
    ],
    "Marketing": [
        "Digital Marketing Specialist", "Social Media Manager", "SEO Specialist",
        "Content Marketer", "Email Marketing Specialist", "Growth Hacker",
        "Marketing Analyst", "Brand Manager", "Marketing Coordinator"
    ],
    "Content": [
        "Content Writer", "Copywriter", "Technical Writer",
        "Blog Writer", "Ghostwriter", "Editor", "Proofreader",
        "Content Strategist", "Scriptwriter"
    ],
    "Management": [
        "Project Manager", "Product Manager", "Operations Manager",
        "Team Lead", "Scrum Master", "Account Manager",
        "Business Analyst", "Program Manager"
    ]
}

# Nigerian companies (mix of real and fictional)
COMPANIES = [
    {"name": "Flutterwave", "logo": "F", "industry": "FinTech"},
    {"name": "Paystack", "logo": "P", "industry": "FinTech"},
    {"name": "Andela", "logo": "A", "industry": "Technology"},
    {"name": "Kuda Bank", "logo": "K", "industry": "Banking"},
    {"name": "TechNaija", "logo": "T", "industry": "Technology"},
    {"name": "NaijaBiz", "logo": "N", "industry": "E-commerce"},
    {"name": "AfriLabs", "logo": "A", "industry": "Technology"},
    {"name": "Carbon", "logo": "C", "industry": "FinTech"},
    {"name": "Interswitch", "logo": "I", "industry": "FinTech"},
    {"name": "Jumia", "logo": "J", "industry": "E-commerce"},
    {"name": "Piggyvest", "logo": "P", "industry": "FinTech"},
    {"name": "Hotels.ng", "logo": "H", "industry": "Travel"},
    {"name": "BuyCoins", "logo": "B", "industry": "Cryptocurrency"},
    {"name": "Printivo", "logo": "P", "industry": "Printing"},
    {"name": "Farmcrowdy", "logo": "F", "industry": "Agriculture"},
    {"name": "Kobo360", "logo": "K", "industry": "Logistics"},
    {"name": "54gene", "logo": "5", "industry": "Healthcare"},
    {"name": "Helium Health", "logo": "H", "industry": "Healthcare"},
    {"name": "Autochek", "logo": "A", "industry": "Automotive"},
    {"name": "Mono", "logo": "M", "industry": "FinTech"}
]

# Job descriptions by category
JOB_DESCRIPTIONS = {
    "Development": [
        "Join our engineering team to build scalable and responsive web applications.",
        "We're looking for a talented developer to help us create innovative solutions.",
        "Help us build the next generation of our platform with cutting-edge technologies.",
        "Work on challenging problems and deliver high-quality code for our products.",
        "Collaborate with our team to develop robust and maintainable software solutions."
    ],
    "Design": [
        "Create beautiful and intuitive user interfaces for our digital products.",
        "Design engaging visual assets that align with our brand identity.",
        "Develop user-centered designs based on customer feedback and research.",
        "Craft compelling visual stories that connect with our target audience.",
        "Transform complex ideas into simple, accessible, and visually appealing designs."
    ],
    "Marketing": [
        "Drive growth through innovative digital marketing strategies.",
        "Develop and execute marketing campaigns to increase brand awareness.",
        "Analyze marketing data to optimize campaign performance and ROI.",
        "Create and implement strategies to expand our market reach.",
        "Build and maintain our brand presence across various digital channels."
    ],
    "Content": [
        "Create engaging and SEO-optimized content for our website and blog.",
        "Develop compelling copy that converts visitors into customers.",
        "Produce clear and concise technical documentation for our products.",
        "Craft storytelling content that resonates with our target audience.",
        "Write persuasive marketing materials that highlight our value proposition."
    ],
    "Management": [
        "Lead projects from conception to completion, ensuring timely delivery.",
        "Coordinate cross-functional teams to achieve business objectives.",
        "Develop and implement processes to improve operational efficiency.",
        "Manage resources effectively to deliver projects within budget.",
        "Drive strategic initiatives that align with company goals."
    ]
}

# Requirements by category
JOB_REQUIREMENTS = {
    "Development": [
        "Proficiency in HTML, CSS, and JavaScript.",
        "Experience with React, Vue.js, or Angular.",
        "Knowledge of backend technologies like Node.js, Python, or PHP.",
        "Understanding of RESTful APIs and database design.",
        "Familiarity with version control systems like Git."
    ],
    "Design": [
        "Proficiency in design tools like Figma, Adobe XD, or Sketch.",
        "Strong portfolio demonstrating UI/UX design skills.",
        "Understanding of design principles and user-centered design.",
        "Experience creating wireframes, prototypes, and user flows.",
        "Knowledge of responsive design and accessibility standards."
    ],
    "Marketing": [
        "Experience with digital marketing channels and strategies.",
        "Knowledge of SEO, SEM, and social media marketing.",
        "Familiarity with marketing analytics tools.",
        "Understanding of customer acquisition and retention strategies.",
        "Experience with content marketing and email campaigns."
    ],
    "Content": [
        "Excellent writing and editing skills.",
        "Experience creating content for digital platforms.",
        "Understanding of SEO principles and content optimization.",
        "Ability to adapt writing style for different audiences.",
        "Research skills and attention to detail."
    ],
    "Management": [
        "Experience managing projects using Agile or other methodologies.",
        "Strong leadership and team coordination skills.",
        "Ability to manage multiple priorities and deadlines.",
        "Experience with project management tools.",
        "Problem-solving skills and strategic thinking."
    ]
}

# Salary ranges by level
SALARY_RANGES = {
    "Entry level": {
        "min": 100000,
        "max": 250000
    },
    "Mid level": {
        "min": 250000,
        "max": 500000
    },
    "Senior level": {
        "min": 500000,
        "max": 1000000
    }
}

# Job application URLs - fictional but realistic
JOB_APPLY_DOMAINS = [
    "https://careers.{company}.com/jobs/{id}",
    "https://www.{company}.com/careers/{id}",
    "https://jobs.{company}.ng/apply/{id}",
    "https://www.linkedin.com/jobs/view/{id}",
    "https://www.indeed.com/viewjob?jk={id}",
    "https://www.glassdoor.com/job-listing/{id}"
]

def generate_job_listings(count=20):
    """Generate a specified number of realistic job listings"""
    jobs = []
    
    # Get current time for posted_at timestamps
    now = datetime.now()
    
    for _ in range(count):
        # Select random category and job title
        category = random.choice(list(JOB_CATEGORIES.keys()))
        job_title = random.choice(JOB_CATEGORIES[category])
        
        # Select random company
        company = random.choice(COMPANIES)
        
        # Determine job level based on title
        level = "Entry level"
        if "Senior" in job_title or "Lead" in job_title or "Manager" in job_title:
            level = "Senior level"
        elif "Mid" in job_title or job_title.startswith("Experienced"):
            level = "Mid level"
        else:
            # Randomly assign levels for other titles
            level = random.choices(
                ["Entry level", "Mid level", "Senior level"],
                weights=[0.4, 0.4, 0.2],
                k=1
            )[0]
        
        # Determine if remote
        remote = random.choice([True, False])
        
        # Generate location
        if remote:
            location = f"Remote ({random.choice(['Nigeria', 'Nationwide', 'Africa'])})"
        else:
            location = f"{random.choice(NIGERIAN_CITIES)}, Nigeria"
        
        # Generate job type
        job_type = random.choices(
            ["Full-time", "Part-time", "Contract", "Freelance"],
            weights=[0.7, 0.1, 0.1, 0.1],
            k=1
        )[0]
        
        # Generate salary range
        salary_range = SALARY_RANGES[level]
        min_salary = random.randint(salary_range["min"], (salary_range["min"] + salary_range["max"]) // 2)
        max_salary = random.randint(min_salary, salary_range["max"])
        
        # Round to nearest 10000
        min_salary = (min_salary // 10000) * 10000
        max_salary = (max_salary // 10000) * 10000
        
        salary = f"₦{min_salary:,} - ₦{max_salary:,}"
        
        # Generate description and requirements
        description = random.choice(JOB_DESCRIPTIONS[category])
        requirements = random.choice(JOB_REQUIREMENTS[category])
        
        # Generate tags
        tags = [category]
        if remote:
            tags.append("Remote")
        tags.append(job_type.replace("-", " "))
        
        # Add specific skills based on job title
        if "React" in job_title:
            tags.append("React")
        if "Python" in job_title:
            tags.append("Python")
        if "JavaScript" in job_title or "Frontend" in job_title:
            tags.append("JavaScript")
        if "UI/UX" in job_title or "Product Designer" in job_title:
            tags.append("UI/UX")
        if "WordPress" in job_title:
            tags.append("WordPress")
        
        # Generate random posted time in the last 7 days
        days_ago = random.randint(0, 7)
        hours_ago = random.randint(0, 23)
        minutes_ago = random.randint(0, 59)
        posted_at = now - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
        
        # Generate a unique ID
        job_id = str(uuid.uuid4())
        
        # Generate application URL
        apply_url_template = random.choice(JOB_APPLY_DOMAINS)
        company_slug = company["name"].lower().replace(" ", "")
        apply_url = apply_url_template.format(company=company_slug, id=job_id)
        
        # Create job listing
        job = {
            "id": job_id,
            "title": job_title,
            "company": company["name"],
            "company_logo": company["logo"],
            "location": location,
            "description": description,
            "requirements": requirements,
            "salary": salary,
            "type": job_type,
            "level": level,
            "tags": tags,
            "posted_at": posted_at.isoformat(),
            "remote": remote,
            "source": "NaijaFreelance",
            "generated": True,
            "apply_url": apply_url  # Add application URL
        }
        
        jobs.append(job)
    
    return jobs

def save_generated_jobs(count=20, output_file="static/data/mock-jobs.json"):
    """Generate job listings and save them to a JSON file"""
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Generate jobs
    jobs = generate_job_listings(count)
    
    # Check if file exists and load existing jobs
    existing_jobs = []
    if os.path.exists(output_file):
        try:
            with open(output_file, 'r') as f:
                existing_jobs = json.load(f)
        except Exception as e:
            print(f"Error loading existing jobs: {e}")
    
    # Filter out generated jobs to keep real scraped jobs
    real_jobs = [job for job in existing_jobs if not job.get('generated', False)]
    
    # Combine real jobs with new generated jobs
    combined_jobs = real_jobs + jobs
    
    # Save to file
    with open(output_file, 'w') as f:
        json.dump(combined_jobs, f, indent=2)
    
    print(f"Generated {len(jobs)} job listings and saved to {output_file}")
    print(f"Total jobs in file: {len(combined_jobs)}")
    
    return combined_jobs

if __name__ == "__main__":
    save_generated_jobs(30)

