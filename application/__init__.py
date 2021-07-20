import os
from dotenv import load_dotenv
from flask import Flask, redirect, url_for, request, send_from_directory
from flask_talisman import Talisman
from .views import bp
from .auth import auth
from .database import client
from .emails import mail

load_dotenv()

app = Flask(__name__)
app.register_blueprint(bp)
app.register_blueprint(auth)

csp = {
    'default-src': [
        '\'self\'',
        '*.googleapis.com',
        '*.gstatic.com',
        'cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css'
    ],
    'img-src': '*',
}
Talisman(app, content_security_policy=csp)

# Secret Key config for WTF forms.
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")

# Session config. Followed documentation
app.config["SESSION_TYPE"] = "mongodb"
app.config["SESSION_MONGODB"] = client
app.config["SESSION_MONGODB_DB"] = "startupjobs"
app.config["SESSION_MONGODB_COLLECT"] = "sessions"

# Email setup
app.config["MAIL_DEFAULT_SENDER"] = "malikpiara@gmail.com"
app.config["MAIL_SERVER"] = "smtp.googlemail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")


mail.init_app(app)


@app.route('/robots.txt')
# @app.route('/sitemap.xml')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])


@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for('main.home'))
