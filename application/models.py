import os
import sys
from PIL import Image
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


def update_entry_status(id, status, user):
    mongo.db.jobs.update_one(
        {
            '_id': ObjectId(id)
        },
        {
            '$set': {'status': status, 'last_modified': datetime.datetime.utcnow(),
                     'modified_by': user}
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
    mongo.db.jobs.update_many({"modified_by": {"$exists": False}}, {
                              "$set": {"modified_by": ""}})

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
            "last_modified": job["last_modified"],
            'modified_by': job['modified_by']
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


def get_users():
    users = []
    for user in mongo.db.users.find(
        {
            "_id": {"$exists": True}
        }
    ):
        entry = {
            "_id": user["_id"],
            "email": user["email"],
            "name": user["name"],
            "profile_image_name": user["profile_image_name"]
        }

        users.append(entry)
    return users


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


def test_pill(image):
    im = Image.open(image)
    return im.format, im.size, im.mode


def crop_image(infile):
    with Image.open(infile) as im:
        (left, upper, right, lower) = (20, 20, 100, 100)
        im_crop = im.crop((left, upper, right, lower))
        return im_crop


def convert_file_to_webp(infile):
    for infile in sys.argv[1:]:
        f, e = os.path.splitext(infile)
        outfile = f + ".webp"
        if infile != outfile:
            try:
                with Image.open(infile) as im:
                    im.save(outfile, "webp")
            except OSError:
                print("cannot convert", infile)
