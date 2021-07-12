from .models import post_job, get_jobs, get_all_jobs, update_entry_status, check_entry_timelimit, find_user_by_email, create_user
from flask import render_template, Blueprint, redirect, url_for, session
from .forms import NewJobSubmission, JobManagement, RefreshJobStatus, SignIn, SignUp
from .emails import send_email
from flask import make_response
from werkzeug.security import check_password_hash
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
                   to='malik@hey.com',
                   template='mail/submission_notification',
                   job_title=job_title,
                   company=company)
        return redirect(url_for('main.new'))
    return render_template('new.html', form=form, job_title=job_title, company=company)


@bp.route('/')
def home():
    # for job in filtered(lambda j:(j.category == 'design'), jobs)
    #            {% filter_jobs =%}
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


@bp.route('/admin', methods=["GET", "POST"])
def admin():

    if not session.get("user_id"):
        return redirect("/login")

    # form = JobManagement(id="test")

    form = JobManagement()
    refresh_button = RefreshJobStatus()

    jobs = get_all_jobs()

    if form.validate_on_submit():
        print("working")
        update_entry_status(form.id.data, form.status.data)
        return redirect(url_for('main.admin'))

    if refresh_button.validate_on_submit():
        print("working2")
        check_entry_timelimit()
        return redirect(url_for('main.admin'))

    return render_template('admin.html', form=form, refresh_button=refresh_button, jobs=jobs)


@bp.route("/login", methods=["GET", "POST"])
def login():
    form = SignIn()

    if session.get("username"):
        return redirect(url_for('main.home'))

    if form.validate_on_submit():
        email = form.email_address.data
        password = form.password.data
        user = find_user_by_email(email)

        # If user is found, store the email and id in session.
        if user:
            check = check_password_hash(user["password"], password)

            if check:
                session["username"] = email
                session["user_id"] = str(user["_id"])
                return redirect(url_for('main.home'))

    return render_template("auth/login.html", form=form)


""" @bp.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignUp()

    if session.get("username"):
        return redirect(url_for('main.home'))

    if form.validate_on_submit():
        user_email = form.email_address.data
        user_name = form.name.data
        create_user(user_email,
                    user_name, password=form.password.data)

        return redirect(url_for('main.home'))
    return render_template("auth/signup.html", form=form) """
