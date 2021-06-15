from .database import client


def post_job(title, company, category, location, link, email):
    client.startupjobs.jobs.insert(
        {
            "title": title,
            "company": company,
            "category": category.lower(),
            "location": location,
            "url": link,
            "email": email,
            "status": "pending"
        }
    )


def get_jobs():
    jobs = [
        {
            "title": job["title"],
            "company": job["company"],
            "category": job["category"],
            "location": job["location"],
            "url": job["url"],
            "email": job["email"]
        }
        for job in client.startupjobs.jobs.find(
            {
                "status": "active"
            }
        )
    ]
    return jobs
