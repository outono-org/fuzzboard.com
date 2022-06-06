from datetime import datetime
from datetime import timedelta
from itertools import count
from flask import render_template, Blueprint, redirect, url_for, session
from .decorators import login_required, admin_required
from .database import mongo
from .forms import JobManagement, RefreshJobStatus
from .models import get_jobs, update_entry_status, check_entry_timelimit, get_users
from .models import add_stats_to_jobs, get_active_jobs, add_user_types_to_db

admin = Blueprint('admin', __name__)


@admin.route('/update', methods=["GET", "POST"])
@login_required
@admin_required
def update_db():
    """ This route enables admins to make structural changes to the DB
    like adding a new field to every document.

    Make sure to comment or remove the function after calling it in production. """

    print("something")

    add_user_types_to_db()

    return redirect(url_for('main.home'))


@admin.route('/admin', methods=["GET", "POST"])
@login_required
@admin_required
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


def num_of_applies_this_week():
    # FIX: This function is only counting the number of applies
    # for jobs added in the last 7 days. That's incorrect.
    # We're NOT counting properly because we don't
    # have a timestamp for every 'apply' click.
    total_num = 0
    # Counts the number of jobs added in the last 7 days.
    jobs = mongo.db.jobs.find(
        {
            'created_on': {"$gt": datetime.utcnow() - timedelta(days=7)}
        }
    )

    for job in jobs:
        print(job)
        num_of_applies = list(job['stats'].values())[0]
        total_num = total_num + num_of_applies

    return total_num


def num_of_jobs_added_this_week():
    # Counts the number of jobs added in the last 7 days.
    num_of_jobs = mongo.db.jobs.find({
        'created_on': {"$gt": datetime.utcnow() - timedelta(days=7)}
    }).count()

    return num_of_jobs


@admin.get('/dashboard')
@login_required
@admin_required
def dashboard_page():

    return render_template('dashboard.html', num_of_applies=num_of_applies(), num_of_jobs=num_of_jobs_added_this_week(), num_of_applies_this_week=num_of_applies_this_week())
