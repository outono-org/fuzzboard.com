from flask import render_template, Blueprint, redirect, url_for, session
from .decorators import login_required
from .database import mongo
from .forms import JobManagement, RefreshJobStatus
from .models import get_jobs, update_entry_status, check_entry_timelimit, get_users
from .models import add_stats_to_jobs, get_active_jobs

admin = Blueprint('admin', __name__)


@admin.route('/update', methods=["GET", "POST"])
@login_required
def update_db():
    # important: I'm changing the DB by adding a new field to every entry
    # add_slug_to_db()
    # add_description_to_db()
    # encode_job_urls()
    # add_visa_status_to_db()
    add_stats_to_jobs()
    return redirect(url_for('main.home'))


@admin.route('/admin', methods=["GET", "POST"])
@login_required
def dashboard():
    user = mongo.db.users.find_one_or_404({'email': session["username"]})

    # get id and return user name. if modified is = user, return name

    form = JobManagement()
    refresh_button = RefreshJobStatus()

    jobs = get_jobs()
    users = get_users()

    if form.validate_on_submit():
        update_entry_status(form.id.data, form.status.data,
                            user["_id"])
        return redirect(url_for('admin.dashboard'))

    if refresh_button.validate_on_submit():
        check_entry_timelimit()
        return redirect(url_for('admin.dashboard'))

    return render_template('admin.html', form=form, refresh_button=refresh_button, jobs=jobs, users=users)


def num_of_applies():
    jobs = get_active_jobs()
    total_num = 0

    for job in jobs:
        num_of_applies = list(job['stats'].values())[0]
        total_num = total_num + num_of_applies
    return total_num


@admin.route('/dashboard', methods=["GET", "POST"])
@login_required
def dashboard_page():

    return render_template('dashboard.html', num_of_applies=num_of_applies())
