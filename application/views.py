from crypt import methods
import io
import gridfs
import urllib.parse
from PIL import Image
import re
import os
from bson.objectid import ObjectId
import datetime
import mistune
from .database import mongo
from flask.wrappers import Response
from flask import request
from .models import post_job, get_active_jobs, save_email, id_generator, get_file_extension, find_and_delete_file, allowed_file, increment_value
from flask import render_template, Blueprint, redirect, url_for, session
from .forms import NewJobSubmission, NewsletterSubscribe, UploadPicture
from .decorators import login_required
from .emails import send_email
from flask_simplemde import SimpleMDE
from werkzeug.utils import secure_filename

bp = Blueprint('main', __name__)

simplemde = SimpleMDE()


@bp.route('/', methods=["GET", "POST"])
def home():

    recent_jobs = get_active_jobs()[:5]

    categories_list = [
        get_active_jobs(category="development")[:5],
        get_active_jobs(category="design")[:5],
        get_active_jobs(category="marketing")[:5],
        get_active_jobs(category="product management")[:5],
        get_active_jobs(category="business development")[:5],
        get_active_jobs(category="other")[:5]
    ]

    subscribe_form = NewsletterSubscribe()

    if subscribe_form.validate_on_submit():
        save_email(subscribe_form.MERGE0.data)
        return redirect(url_for('main.home'))

    return render_template('home.html',
                           subscribe_form=subscribe_form,
                           recent_jobs=recent_jobs,
                           categories_list=categories_list)


@bp.post('/newJob')
def newJob():
    form = NewJobSubmission()
    company = form.company.data
    job_title = form.title.data

    if form.validate_on_submit():

        post_job(title=form.title.data,
                 company=form.company.data,
                 category=form.category.data,
                 location=form.location.data,
                 description=form.description.data,
                 link=form.link.data,
                 email=form.email.data,
                 status="active",
                 visa_sponsor=form.visa_sponsor.data)
        # Notification sent to the person who submitted the job.
        send_email(subject='Your submission | Fuzzboard',
                   to=form.email.data,
                   template='mail/new_job',
                   job_title=job_title,
                   company=company)
        # Notification sent to myself.
        send_email(subject='New submission at Fuzzboard',
                   to=os.environ.get('MAIL_DEFAULT_RECEIVER'),
                   template='mail/submission_notification',
                   job_title=job_title,
                   company=company)

        return job_submitted()


@bp.get('/new/ukraine')
def new():
    """     form = NewJobSubmission()

    return render_template('new.html', form=form) """
    return redirect(url_for('main.new_ukraine'))


@bp.get('/new_job_form')
def new_job_form():
    form = NewJobSubmission()

    return render_template('fragments/new_job_form.html', form=form)


@bp.get('/get_jobs/<category>')
def htmx_get_jobs(category):
    jobs = get_active_jobs(category=category)
    subscribe_form = NewsletterSubscribe()

    return render_template('fragments/get_jobs.html', jobs=jobs, category=category, subscribe_form=subscribe_form)


@bp.get('/get_jobs/visa/<category>')
def htmx_get_jobs_visa(category):
    jobs = get_active_jobs(category=category, visa_sponsor=True)
    subscribe_form = NewsletterSubscribe()

    return render_template('fragments/get_jobs_visa.html', jobs=jobs, category=category, subscribe_form=subscribe_form)


@bp.post('/<id>/bookmark')
def bookmark(id):
    # Start of Session.
    if 'saved_jobs' not in session:
        session['saved_jobs'] = []

    # id = ObjectId(id)

    if id in session['saved_jobs']:
        return Response(status=400)

    session['saved_jobs'].append(id)
    session.modified = True

    return Response(status=200)


@bp.post('/<id>/remove_bookmark')
def remove_bookmark(id):

    session['saved_jobs'].remove(id)
    session.modified = True

    return Response(status=200)


@bp.get('/<category>')
def category(category):
    jobs = get_active_jobs(category=category)

    if len(jobs) == 0:
        return redirect(url_for('main.home'))

    return render_template('category_page.html', category=category, jobs=jobs)


# Ukraine CASAFARI page.
@bp.get('/visa')
def visa():

    return redirect(url_for('main.visa_ukraine'))


@bp.get('/ukraine')
def visa_ukraine():
    return redirect(url_for('main.home'))


@bp.get('/company/<company>')
def company(company):
    jobs = get_active_jobs(company=company)

    if len(jobs) == 0:
        return redirect(url_for('main.home'))

    return render_template('company_page.html', company=company, jobs=jobs)


@bp.get('/location/<location>')
def location(location):
    jobs = get_active_jobs(location=location)

    if len(jobs) == 0:
        return redirect(url_for('main.home'))

    return render_template('location_page.html', location=location, jobs=jobs)


@bp.route('/jobs/<slug>', methods=["GET", "POST"])
def jobs(slug):
    # TODO: Replace get active jobs with a new get job function.
    # TODO: I wonder if there's a better way to handle "days ago"
    jobs = get_active_jobs(slug=slug)

    today = datetime.datetime.now().replace(microsecond=0)

    for job in jobs:
        job["description"] = mistune.html(job["description"])
        job["timestamp"] = job["timestamp"].replace(tzinfo=None)

        # Removing HTML tags and characters from job description.
        CLEANR = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
        clean_description = re.sub(CLEANR, '', job["description"])[:1000]

        days_ago = (today - job["timestamp"])

        # if the characters are less than 8, that means
        # they don't have "days" yet.
        is_less_than_one_day = len(str(days_ago)) <= 8

        days_ago = str(days_ago).split(",")[0] + " " + "ago"

        if is_less_than_one_day:
            days_ago = "Today"

    if len(jobs) == 0:
        return redirect(url_for('main.home'))

    return render_template('job_page.html', jobs=jobs, slug=slug, days_ago=days_ago, clean_description=clean_description)


@bp.post('/<id>/increment')
def increment(id):
    increment_value(id=id, key='stats.num_of_applies')

    return Response(status=200)


@ bp.get('/job_submitted')
def job_submitted():

    return render_template('fragments/job_submitted.html')


@ bp.route('/settings', methods=["GET", "POST"])
@ login_required
def settings():
    fs = gridfs.GridFS(mongo.db)

    username = session.get("username")
    user = mongo.db.users.find_one_or_404({'email': username})

    form = UploadPicture()
    profile_image = form.file.data

    # if the form validates on submit and if the
    # file extension is allowed. Should probably check if the file is allowed
    # before letting the user upload a file.
    if form.validate_on_submit() and allowed_file(profile_image.filename):
        # If the upload files, the photo will be deleted.
        # Delete old file after submission.
        if user["profile_image_name"] != "default.png":
            find_and_delete_file(user["profile_image_name"])

        # I'm replacing the file name uploaded by the user
        # by a random string + the original file extension.
        # TODO: Prefix the file name with something that binds it to the user.
        filename = secure_filename(
            id_generator() + get_file_extension(profile_image.filename))

        outfile = io.BytesIO()

        with Image.open(profile_image) as im:
            (left, upper, right, lower) = (0, 0, 300, 300)
            croppedImage = im.crop((left, upper, right, lower))
            width, height = im.size

        # If the photo uploaded is already a square, don't crop it.
            if width == height:
                im.save(outfile, "JPEG")
            else:
                croppedImage.save(outfile, "JPEG")

        # Saving file on MongoDB.
        fs.put(outfile.getvalue(), filename=filename)

        mongo.db.users.update_one(
            {'_id': user['_id']}, {'$set': {'profile_image_name': filename}})
        return redirect(url_for('main.settings'))

    return render_template("settings.html", username=username, user=user, form=form)


@ bp.route('/file/<filename>')
def file(filename):
    return mongo.send_file(filename)


@ bp.get('/profile/<username>')
@ login_required
def profile(username):
    user = mongo.db.users.find_one_or_404({'name': username})

    return render_template("profile.html", username=username, user=user)

# Mission Ukraine


@ bp.get('/new')
def new_ukraine():

    return render_template('ukraine/new_ukraine.html')


@bp.get('/cities')
def get_city():
    if request.args.get('location') == 'portugal':
        return render_template('fragments/cities/portugal.html')

    else:
        return print("nothing is being returned")


@bp.post('/newJobUkraine')
def newJobUkraine():
    company = request.form['company']
    job_title = request.form['title']

    post_job(title=request.form['title'],
             company=request.form['company'],
             category=request.form['category'],
             location=request.form['city'],
             description=request.form['description'],
             link=request.form['link'],
             email=request.form['email'],
             status="active",
             visa_sponsor=bool(request.form['visa_sponsor']))
    # Notification sent to the person who submitted the job.
    send_email(subject='Your submission | Fuzzboard',
               to=request.form['email'],
               template='mail/new_job',
               job_title=job_title,
               company=company)
    # Notification sent to myself.
    send_email(subject='New submission at Fuzzboard',
               to=os.environ.get('MAIL_DEFAULT_RECEIVER'),
               template='mail/submission_notification',
               job_title=job_title,
               company=company)

    return job_submitted()


portuguese_cities = ['Açores', 'Aveiro', 'Beja', 'Braga', 'Bragança', 'Castelo Branco', 'Coimbra', 'Evora', 'Faro', 'Guarda',
                     'Leiria', 'Lisboa', 'Madeira', 'Portalegre', 'Porto', 'Santarém', 'Setúbal', 'Viana do Castelo', 'Vila Real', 'Viseu']


@bp.get('/savedJobs')
def savedJobs():
    if 'saved_jobs' not in session:
        return redirect(url_for('main.home'))

    if 'saved_jobs' in session:
        saved_jobs = [ObjectId(job) for job in session['saved_jobs']]
        jobs = list(mongo.db.jobs.find({'_id': {"$in": saved_jobs}}))

    return render_template('saved_jobs.html', jobs=jobs)
