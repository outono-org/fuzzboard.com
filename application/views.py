import os

from flask.wrappers import Response
from wtforms.fields import html5
from .models import post_job, get_active_jobs, get_jobs, get_recent_jobs, update_entry_status, check_entry_timelimit, save_email, save_email_test_startups, find_bookmark_job_counter, increase_bookmark_job_counter, get_active_jobs2
from flask import render_template, Blueprint, redirect, url_for, session
from .forms import NewJobSubmission, JobManagement, RefreshJobStatus, NewsletterSubscribe, StartupsTestForm
from .decorators import login_required
from .emails import send_email
from flask import make_response
from feedgen.feed import FeedGenerator


bp = Blueprint('main', __name__)


@bp.post('/newJob')
def newJob():
    form = NewJobSubmission()
    company = form.company.data
    job_title = form.title.data

    if form.validate_on_submit():
        post_job(form.title.data,
                 form.company.data,
                 form.category.data,
                 form.location.data,
                 form.link.data,
                 form.email.data,
                 "pending")
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


@bp.get('/new_job_form')
def new_job_form():
    form = NewJobSubmission()

    return render_template('new_job_form.html', form=form)


@bp.get('/get_jobs/<category>')
def htmx_get_jobs(category):
    jobs = get_active_jobs(category)
    subscribe_form = NewsletterSubscribe()

    return render_template('get_jobs.html', jobs=jobs, category=category, subscribe_form=subscribe_form,)


@bp.post('/bookmark')
# Right now we're saving the number of clicks on the bookmarking icon
# from people who don't have an account to have a sense of the interest
# in the 'save a job' feature.
def bookmark():

    if not session.get("username"):
        number_of_clicks = find_bookmark_job_counter()
        increase_bookmark_job_counter(number_of_clicks)

    return Response(200)


@bp.route('/', methods=["GET", "POST"])
def home():
    subscribe_form = NewsletterSubscribe()

    recent_jobs = get_recent_jobs()
    dev_jobs = get_active_jobs("development")
    design_jobs = get_active_jobs("design")
    marketing_jobs = get_active_jobs("marketing")
    bizdev_jobs = get_active_jobs("business development")
    other_jobs = get_active_jobs("other")

    if subscribe_form.validate_on_submit():
        save_email(subscribe_form.MERGE0.data)
        return redirect(url_for('main.home'))

    return render_template('home.html',
                           subscribe_form=subscribe_form,
                           recent_jobs=recent_jobs,
                           development=dev_jobs,
                           design=design_jobs,
                           marketing=marketing_jobs,
                           bizdev=bizdev_jobs,
                           other=other_jobs)


@bp.get('/<category>')
def category(category):
    jobs = get_active_jobs(category)

    for job in jobs:
        # if job['category'] == category:
        return render_template('category_page.html', category=category, jobs=jobs)

    return redirect(url_for('main.home'))


@bp.get('/company/<company>')
def company(company):
    jobs = get_active_jobs2()

    for job in jobs:
        if job['company'] == company:
            return render_template('company_page.html', company=company, jobs=jobs)

    return redirect(url_for('main.home'))


@bp.get('/location/<location>')
def location(location):
    jobs = get_active_jobs2()

    for job in jobs:
        if job['location'] == location:
            return render_template('location_page.html', location=location, jobs=jobs)

    return redirect(url_for('main.home'))


@bp.get('/feed')
def rss():
    fg = FeedGenerator()
    fg.title('Startup Jobs Portugal')
    fg.description('Real-time feed for jobs at Startup Jobs Portugal.')
    fg.link(href='https://startupjobsportugal.com/')

    for job in get_active_jobs2():
        fe = fg.add_entry()
        fe.title(job['title'])
        fe.link(href=job['url'])
        fe.content(job['company'])
        fe.description(job['company'])
        fe.guid(str(job['_id']), permalink=False)
        fe.author(name='Startup Jobs Portugal')
        fe.pubDate(job['timestamp'])

    response = make_response(fg.rss_str())
    response.headers.set('Content-Type', 'application/rss+xml')

    return response


@bp.route('/admin', methods=["GET", "POST"])
@login_required
def admin():
    # form = JobManagement(id="test")

    form = JobManagement()
    refresh_button = RefreshJobStatus()

    jobs = get_jobs()

    if form.validate_on_submit():
        update_entry_status(form.id.data, form.status.data)
        return redirect(url_for('main.admin'))

    if refresh_button.validate_on_submit():
        check_entry_timelimit()
        return redirect(url_for('main.admin'))

    return render_template('admin.html', form=form, refresh_button=refresh_button, jobs=jobs)


@bp.route('/saved', methods=["GET", "POST"])
def saved_jobs():
    form = StartupsTestForm()

    if form.validate_on_submit():
        save_email_test_startups(form.email.data, form.feedback.data)
        return redirect(url_for('main.home'))

    return render_template('saved_jobs.html', form=form)


@bp.get('/job_submitted')
def job_submitted():

    return render_template('job_submitted.html')
