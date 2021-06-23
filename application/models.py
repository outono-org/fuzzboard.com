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
            "_id": job["_id"],
            "title": job["title"],
            "company": job["company"],
            "category": job["category"],
            "location": job["location"],
            "url": job["url"],
            "email": job["email"],
            "timestamp": job["_id"].generation_time
        }
        for job in client.startupjobs.jobs.find(
            {
                "status": "active"
            }
        )
    ]
    return jobs


def get_jobs2():
    jobs = []
    for job in client.startupjobs.jobs.find(
        {
            "status": "active"
        }
    ):
        joblist = {
            "_id": job["_id"],
            "title": job["title"],
            "company": job["company"],
            "category": job["category"],
            "location": job["location"],
            "url": job["url"],
            "email": job["email"],
            "timestamp": job["_id"].generation_time
        }
        jobs.append(joblist)
    return jobs
