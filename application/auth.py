from flask import render_template, Blueprint, redirect, url_for, session
from .forms import SignIn, SignUp
from .models import find_user_by_email, create_user
from werkzeug.security import check_password_hash

auth = Blueprint('auth', __name__)


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
