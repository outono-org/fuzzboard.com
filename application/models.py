import os
from .database import mongo
from bson.objectid import ObjectId
import datetime
from datetime import timedelta
from werkzeug.security import generate_password_hash
import string
import random
import gridfs


def increment_bookmark_value():
    return mongo.db.test_bookmark.find_one_and_update(
        {
            'number_of_clicks': {'$exists': True}
        },
        {
            '$inc': {'number_of_clicks': 1}
        }
    )['number_of_clicks']


def post_job(title, company, category, location, link, email, status):
    mongo.db.jobs.insert_one(
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
    mongo.db.subscribers.insert_one(
        {
            "email": email,
            'created_on': datetime.datetime.utcnow()
        }
    )


def save_email_test_startups(email, feedback):
    mongo.db.test_startups.insert_one(
        {
            "email": email,
            "feedback": feedback,
            'created_on': datetime.datetime.utcnow()
        }
    )


def update_entry_status(id, status):
    mongo.db.jobs.update_one(
        {
            '_id': ObjectId(id)
        },
        {
            '$set': {'status': status, 'last_modified': datetime.datetime.utcnow()}
        }
    )


def check_entry_timelimit():
    time_limit = datetime.datetime.utcnow() - timedelta(days=60)
    mongo.db.jobs.update_many(
        {
            'status': 'active', 'created_on': {'$lt': time_limit}
        },
        {
            '$set': {'status': 'expired', 'last_modified': datetime.datetime.utcnow()}
        }
    )


def get_active_jobs(category: str = "$any"):
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
        for job in mongo.db.jobs.find(
            {
                "status": "active",
                "category": category,
            }
        )
    ]
    return jobs


def get_active_jobs2():
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
        for job in mongo.db.jobs.find(
            {
                "status": "active",
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
        for job in mongo.db.jobs.find(
            {
                "status": "active"
            }
        )
    ]
    return sorted(jobs, key=lambda entry: entry["timestamp"], reverse=True)[:5]


def get_jobs():
    jobs = []
    for job in mongo.db.jobs.find(
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
    mongo.db.users.insert_one(
        {
            "email": email_address,
            "name": name,
            "password": hashed_pass,
            "profile_image_name": "default.png",
            "account_status": "inactive"
        }
    )


def find_user_by_email(email):
    return mongo.db.users.find_one(
        {
            "email": email
        }
    )


def image_id_generator(size=8, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def get_file_extension(filename):
    filename, file_extension = os.path.splitext(filename)
    return file_extension


def find_fs_file(filename):
    result = mongo.db.fs.files.find_one(
        {'filename': filename},
        {'_id'}
    )
    return result['_id']


def delete_file(files_id):
    fs = gridfs.GridFS(mongo.db)
    fs.delete(files_id)


def find_and_delete_file(filename):
    result = find_fs_file(filename)
    delete_file(result)


# Allowed extensions for image uploads.
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
