from application.models import post_job, get_jobs
from flask import render_template, Blueprint, redirect, url_for
from .forms import NewJobSubmission

bp = Blueprint('main', __name__)


@bp.route('/new', methods=["GET", "POST"])
def new():
    form = NewJobSubmission()
    if form.validate_on_submit():
        post_job(form.title.data,
                 form.company.data,
                 form.category.data,
                 form.location.data,
                 form.link.data,
                 form.email.data)
        return redirect(url_for('main.new'))
    return render_template('new.html', form=form)


@bp.route('/')
def home():
    jobs = get_jobs()
    return render_template('home.html', jobs=jobs)
