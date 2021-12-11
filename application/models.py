from .database import client
from bson.objectid import ObjectId
import datetime
from datetime import timedelta
from werkzeug.security import generate_password_hash


def find_bookmark_job_counter():
    return client.startupjobs.test_bookmark.find_one(
        {
            "number_of_clicks": {"$exists": True}
        }
    )


def increase_bookmark_job_counter(number_of_clicks):
    client.startupjobs.test_bookmark.update_one(
        {
            "number_of_clicks": {"$exists": True}
        },
        {
            '$set': {'number_of_clicks': number_of_clicks+1}
        }
    )


def post_job(title, company, category, location, link, email, status):
    client.startupjobs.jobs.insert(
        {
            "title": title,
            "company": company,
            "category": category.lower(),
            "location": location,
            "url": link,
            "email": email,
            "status": status,
            'created_on': datetime.datetime.utcnow(),
            "last_modified": datetime.datetime.utcnow()
        }
    )


def save_email(email):
    client.startupjobs.subscribers.insert(
        {
            "email": email,
            'created_on': datetime.datetime.utcnow()
        }
    )


def save_email_test_startups(email, feedback):
    client.startupjobs.test_startups.insert(
        {
            "email": email,
            "feedback": feedback,
            'created_on': datetime.datetime.utcnow()
        }
    )


def update_entry_status(id, status):
    client.startupjobs.jobs.update_one(
        {
            '_id': ObjectId(id)
        },
        {
            '$set': {'status': status, 'last_modified': datetime.datetime.utcnow()}
        }
    )


def check_entry_timelimit():
    time_limit = datetime.datetime.utcnow() - timedelta(days=30)
    client.startupjobs.jobs.update_many(
        {
            'status': 'active', 'created_on': {'$lt': time_limit}
        },
        {
            '$set': {'status': 'expired', 'last_modified': datetime.datetime.utcnow()}
        }
    )


def get_active_jobs():
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


def get_recent_jobs():
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
    return sorted(jobs, key=lambda entry: entry["timestamp"], reverse=True)[:5]


def get_active_dev_jobs():
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
                "status": "active",
                "category": "development"
            }
        )
    ]
    return jobs


def get_active_design_jobs():
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
                "status": "active",
                "category": "design"
            }
        )
    ]
    return jobs


def get_active_marketing_jobs():
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
                "status": "active",
                "category": "marketing"
            }
        )
    ]
    return jobs


def get_active_bizdev_jobs():
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
                "status": "active",
                "category": "business development"
            }
        )
    ]
    return jobs


def get_active_other_jobs():
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
                "status": "active",
                "category": "other"
            }
        )
    ]
    return jobs


def get_jobs():
    jobs = []
    for job in client.startupjobs.jobs.find(
        {
            "_id": {"$exists": True}
        }
    ):
        entry = {
            "_id": job["_id"],
            "title": job["title"],
            "company": job["company"],
            "status": job["status"],
            "category": job["category"],
            "location": job["location"],
            "url": job["url"],
            "email": job["email"],
            "timestamp": job["_id"].generation_time,
            "created_on": job["created_on"],
            "last_modified": job["last_modified"]
        }

        jobs.append(entry)
    return sorted(jobs, key=lambda entry: entry["created_on"], reverse=True)

# Authentication


def create_user(email_address, name, password):
    hashed_pass = generate_password_hash(
        password)
    client.startupjobs.users.insert(
        {
            "email": email_address,
            "name": name,
            "password": hashed_pass
        }
    )


def find_user_by_email(email):
    return client.startupjobs.users.find_one(
        {
            "email": email
        }
    )
