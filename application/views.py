from application.models import post_job, get_jobs
from flask import render_template, Blueprint, redirect, url_for
from .forms import NewJobSubmission
from .emails import send_email
from .models import get_jobs
from flask import make_response
from feedgen.feed import FeedGenerator

bp = Blueprint('main', __name__)


@bp.route('/new', methods=["GET", "POST"])
def new():
    form = NewJobSubmission()
    company = form.company.data
    job_title = form.title.data

    if form.validate_on_submit():
        post_job(form.title.data,
                 form.company.data,
                 form.category.data,
                 form.location.data,
                 form.link.data,
                 form.email.data)
        # Notification sent to the person who submitted the job.
        send_email(subject='Your submission | Startup Jobs',
                   to=form.email.data,
                   template='mail/new_job',
                   job_title=job_title,
                   company=company)
        # Notification sent to myself.
        send_email(subject='New submission at Startup Jobs',
                   to='malik@hey.com',
                   template='mail/submission_notification',
                   job_title=job_title,
                   company=company)
        return redirect(url_for('main.new'))
    return render_template('new.html', form=form, job_title=job_title, company=company)


@bp.route('/')
def home():
    jobs = get_jobs()

    return render_template('home.html', jobs=jobs)


@bp.route('/<category>')
def category(category):
    jobs = get_jobs()

    for job in jobs:
        if job['category'] == category:
            return render_template('category_page.html', category=category, jobs=jobs)

    return redirect(url_for('main.home'))


@bp.route('/feed')
def rss():
    fg = FeedGenerator()
    fg.title('Startup Jobs Portugal')
    fg.description('Real-time feed of jobs at Startup Jobs Portugal.')
    fg.link(href='https://startup-jobs.herokuapp.com/')

    for job in get_jobs():
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
