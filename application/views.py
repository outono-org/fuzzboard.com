import os

from flask.wrappers import Response
from .models import post_job, get_active_jobs, get_jobs, get_active_dev_jobs, get_active_design_jobs, get_active_marketing_jobs, get_active_bizdev_jobs, get_active_other_jobs, update_entry_status, check_entry_timelimit, save_email, save_email_test_startups
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

        response = job_submitted()
        return response


@bp.get('/new')
def new():
    form = NewJobSubmission()

    return render_template('new.html', form=form)


@bp.route('/', methods=["GET", "POST"])
def home():
    subscribe_form = NewsletterSubscribe()

    jobs = get_active_jobs()
    dev_jobs = get_active_dev_jobs()
    design_jobs = get_active_design_jobs()
    marketing_jobs = get_active_marketing_jobs()
    bizdev_jobs = get_active_bizdev_jobs()
    other_jobs = get_active_other_jobs()

    if subscribe_form.validate_on_submit():
        save_email(subscribe_form.MERGE0.data)
        return redirect(url_for('main.home'))

    return render_template('home.html',
                           subscribe_form=subscribe_form,
                           jobs=jobs,
                           development=dev_jobs,
                           design=design_jobs,
                           marketing=marketing_jobs,
                           bizdev=bizdev_jobs,
                           other=other_jobs)


@bp.get('/<category>')
def category(category):
    jobs = get_active_jobs()

    for job in jobs:
        if job['category'] == category:
            return render_template('category_page.html', category=category, jobs=jobs)

    return redirect(url_for('main.home'))


@bp.get('/company/<company>')
def company(company):
    jobs = get_active_jobs()

    for job in jobs:
        if job['company'] == company:
            return render_template('company_page.html', company=company, jobs=jobs)

    return redirect(url_for('main.home'))


@bp.get('/feed')
def rss():
    fg = FeedGenerator()
    fg.title('Startup Jobs Portugal')
    fg.description('Real-time feed of jobs at Startup Jobs Portugal.')
    fg.link(href='https://startup-jobs.herokuapp.com/')

    for job in get_active_jobs():
        fe = fg.add_entry()
        fe.title(job['title'])
        fe.link(href=job['url'])
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


@bp.route('/startups', methods=["GET", "POST"])
def startups():
    form = StartupsTestForm()

    if form.validate_on_submit():
        save_email_test_startups(form.email.data, form.feedback.data)
        return redirect(url_for('main.home'))

    return render_template('startups.html', form=form)


@bp.get('/job_submitted')
def job_submitted():

    return render_template('job_submitted.html')
