from crypt import methods
from flask import render_template, Blueprint, redirect, url_for, session
from application.emails import send_password_reset_email
from .forms import ResetPasswordRequestForm, SignIn, SignUp, ResetPasswordForm
from .models import find_user_by_email, create_user, get_reset_password_token, verify_reset_password_token, set_password
from werkzeug.security import check_password_hash
from .database import mongo

auth = Blueprint('auth', __name__)


@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
# BUG: When the password is reset, the token apparently still works.
# TODO: Create message that flashes when user requests a password reset.
# Do the same for when the 2 passwords don't match.
# TODO: Create email that lets the user know his password has been reset.
def reset_password(token):

    if session.get("username"):
        return redirect(url_for('main.settings'))

    user = verify_reset_password_token(token)

    if not user:
        return redirect(url_for('main.home'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        set_password(user['_id'], form.password.data)
        #flash('Your password has been reset')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', form=form)


@auth.route('/reset_password_request', methods=['GET', 'POST'])
# BUG: When the email inputted by the user is not on the DB
# The page redirects the user to the homepage. This is a security issue.
# Nothing should be happening.
def reset_password_request():
    form = ResetPasswordRequestForm()

    if session.get("username"):
        return redirect(url_for('main.settings'))

    if form.validate_on_submit():
        email = form.email_address.data
        user = mongo.db.users.find_one_or_404(
            {'email': form.email_address.data})
        if user:
            send_password_reset_email(email)
        # display message 'Check your email for the instructions to reset your password'.

    return render_template("auth/reset_password_request.html", form=form)


@auth.route("/login", methods=["GET", "POST"])
def login():
    form = SignIn()

    if session.get("username"):
        return redirect(url_for('main.home'))

    if form.validate_on_submit():
        email = form.email_address.data
        password = form.password.data
        user = find_user_by_email(email)

        # Check if there's a user with that email in the db
        # if there is one, check if the account is active.
        # if it's active, check password and save details in session.
        if user:
            check = check_password_hash(user["password"], password)

            if check:

                if user["account_status"] != "active":
                    return "Your account is not active. If you think this is a mistake, please reach out to Malik."

                session["username"] = email
                session["user_id"] = str(user["_id"])
                return redirect(url_for('main.home'))

    return render_template("auth/login.html", form=form)


@auth.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@auth.route("/signup", methods=["GET", "POST"])
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
    return render_template("auth/signup.html", form=form)
