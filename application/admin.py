from flask import render_template, Blueprint, redirect, url_for, session
from .decorators import login_required
from .database import mongo
from .forms import JobManagement, RefreshJobStatus
from .models import get_jobs, update_entry_status, check_entry_timelimit, get_users

admin = Blueprint('admin', __name__)


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
