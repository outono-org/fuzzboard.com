from crypt import methods
import re
import os
import datetime
import mistune
from .database import mongo
from flask.wrappers import Response
from flask import request
from .models import post_job, get_active_jobs, get_recent_jobs, save_email, save_email_test_startups, increment_bookmark_value, id_generator, get_file_extension, find_and_delete_file, allowed_file
from flask import render_template, Blueprint, redirect, url_for, session
from .forms import NewJobSubmission, NewsletterSubscribe, StartupsTestForm, UploadPicture
from .decorators import login_required
from .emails import send_email
import string
from flask_ckeditor import CKEditor
from flask_mde import Mde
from flask_simplemde import SimpleMDE
from werkzeug.utils import secure_filename

bp = Blueprint('main', __name__)

ckeditor = CKEditor()
mde = Mde()
simplemde = SimpleMDE()


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
                 status="pending")
        # Notification sent to the person who submitted the job.
        send_email(subject='Your submission | Startup Jobs',
                   to=form.email.data,
                   template='mail/new_job',
                   job_title=job_title,
                   company=company)
        # Notification sent to myself.
        send_email(subject='New submission at Startup Jobs',
                   to=os.environ.get('MAIL_DEFAULT_SENDER'),
                   template='mail/submission_notification',
                   job_title=job_title,
                   company=company)

        return job_submitted()


@bp.get('/new')
def new():
    form = NewJobSubmission()

    return render_template('new.html', form=form)


""" @bp.route('/mde-test', methods=["GET", "POST"])
def mdetest():

    if request.method == 'POST':
        content = request.form['content']

    print(content)

    return render_template('mde-test.html') """


@bp.get('/new_job_form')
def new_job_form():
    form = NewJobSubmission()

    return render_template('fragments/new_job_form.html', form=form)


@bp.get('/get_jobs/<category>')
def htmx_get_jobs(category):
    jobs = get_active_jobs(category=category)
    subscribe_form = NewsletterSubscribe()

    return render_template('fragments/get_jobs.html', jobs=jobs, category=category, subscribe_form=subscribe_form,)


@bp.post('/bookmark')
# Right now we're saving the number of clicks on the bookmarking icon
# from people who don't have an account to have a sense of the interest
# in the 'save a job' feature.
def bookmark():
    if not session.get("username"):
        increment_bookmark_value()

    return Response(200)


@bp.route('/', methods=["GET", "POST"])
def home():

    recent_jobs = get_recent_jobs()

    categories_list = [
        get_active_jobs(category="development"),
        get_active_jobs(category="design"),
        get_active_jobs(category="marketing"),
        get_active_jobs(category="product management"),
        get_active_jobs(category="business development"),
        get_active_jobs(category="other")
    ]

    subscribe_form = NewsletterSubscribe()

    if subscribe_form.validate_on_submit():
        save_email(subscribe_form.MERGE0.data)
        return redirect(url_for('main.home'))

    return render_template('home.html',
                           subscribe_form=subscribe_form,
                           recent_jobs=recent_jobs,
                           categories_list=categories_list)


@bp.get('/<category>')
def category(category):
    jobs = get_active_jobs(category=category)

    if len(jobs) == 0:
        return redirect(url_for('main.home'))

    return render_template('category_page.html', category=category, jobs=jobs)


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


@bp.route('/saved', methods=["GET", "POST"])
def saved_jobs():
    form = StartupsTestForm()

    if form.validate_on_submit():
        save_email_test_startups(form.email.data, form.feedback.data)
        return redirect(url_for('main.home'))

    return render_template('saved_jobs.html', form=form)


@bp.get('/jobs/<slug>')
def jobs(slug):
    # TODO: Replace get active jobs with a new get job function.
    jobs = get_active_jobs(slug=slug)

    today = datetime.datetime.now()

    for job in jobs:
        job["description"] = mistune.html(job["description"])
        job["timestamp"] = job["timestamp"].replace(tzinfo=None)

        CLEANR = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
        clean_description = re.sub(CLEANR, '', job["description"])[:1000]

        """ print(today)
        print(job["timestamp"])
        print(today - job["timestamp"]) """

        days_ago = (today - job["timestamp"])

        days_ago = str(days_ago).split(",")[0] + " " + "ago"

        is_less_than_one_day = int(str(days_ago).split(",")[0][0]) < 1

        if is_less_than_one_day:
            days_ago = "Today"

    if len(jobs) == 0:
        return redirect(url_for('main.home'))

    return render_template('job_page.html', jobs=jobs, slug=slug, days_ago=days_ago, clean_description=clean_description)


@bp.get('/job_submitted')
def job_submitted():

    return render_template('fragments/job_submitted.html')


@bp.route('/settings', methods=["GET", "POST"])
@login_required
def settings():
    username = session.get("username")
    user = mongo.db.users.find_one_or_404({'email': username})

    form = UploadPicture()
    profile_image = form.file.data

    # if the form validates on submit and if the
    # file extension is allowed. Should probably check if the file is allowed
    # before letting the user upload a file.
    if form.validate_on_submit() and allowed_file(profile_image.filename):

        if user["profile_image_name"] != "default.png":
            find_and_delete_file(user["profile_image_name"])

        # I'm replacing the file name uploaded by the user
        # by a random string + the original file extension.
        filename = secure_filename(
            id_generator() + get_file_extension(profile_image.filename))

        """ with Image.open(profile_image) as im:
            (left, upper, right, lower) = (0, 0, 300, 300)
            croppedImage = im.crop((left, upper, right, lower))

            croppedImage.save(profile_image, format='WEBP')

            print(filename, filename, filename)
        croppedImage.show() """

        mongo.save_file(filename, profile_image)

        mongo.db.users.update_one(
            {'_id': user['_id']}, {'$set': {'profile_image_name': filename}})
        return redirect(url_for('main.settings'))

    return render_template("settings.html", username=username, user=user, form=form)


@bp.route('/file/<filename>')
def file(filename):
    return mongo.send_file(filename)


@bp.get('/profile/<username>')
@login_required
def profile(username):
    user = mongo.db.users.find_one_or_404({'name': username})

    return render_template("profile.html", username=username, user=user)
