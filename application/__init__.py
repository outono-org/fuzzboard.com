import os
from dotenv import load_dotenv
from flask import Flask, redirect, url_for, request, send_from_directory
from flask_talisman import Talisman, GOOGLE_CSP_POLICY
from .views import bp
from .auth import auth
from .database import mongo
from .emails import mail

load_dotenv()

app = Flask(__name__)
app.register_blueprint(bp)
app.register_blueprint(auth)

csp = {
    'default-src': [
        '\'self\'',
        '*.googleapis.com',
        '*.googletagmanager.com',
        '*.gstatic.com',
        'cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css',
        'https://www.googletagmanager.com',
        '*.googleanalytics.com',
        '*.google-analytics.com',
    ],
    'script-src': [
        '\'self\'',
        'unsafe-inline',
        'ajax.googleapis.com',
        'https://code.jquery.com',
        'https://www.google.com',
        'www.googletagmanager.com',
        '*.googleanalytics.com',
        '*.google-analytics.com',
        'https://www.googletagmanager.com/',
    ],
    'img-src': [
        '\'self\'',
        '*.bootstrapcdn.com',
        '*.googleapis.com',
        'www.google-analytics.com',
        'https://ssl.gstatic.com',
        'https://www.gstatic.com',
    ],
}
Talisman(app,
         content_security_policy=csp,
         content_security_policy_nonce_in=['script-src']
         )

# Secret Key config for WTF forms.
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")

# Set maximum allowed payload for user uploads to 2MB
app.config['MAX_CONTENT_LENGTH'] = 2 * 1000 * 1000

# PyMongo Config
mongo.init_app(app, uri=os.environ.get("MONGODB_URI"),
               ssl=True, ssl_cert_reqs='CERT_NONE')


# Session config. Followed documentation
app.config["SESSION_TYPE"] = "mongodb"
app.config["SESSION_MONGODB"] = mongo.db
app.config["SESSION_MONGODB_DB"] = "startupjobs"
app.config["SESSION_MONGODB_COLLECT"] = "sessions"

# Sendgrid setup.
app.config['SECRET_KEY'] = 'top-secret!'
app.config['MAIL_SERVER'] = 'smtp.sendgrid.net'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'apikey'
app.config['MAIL_PASSWORD'] = os.environ.get('SENDGRID_API_KEY')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')

mail.init_app(app)


@ app.route('/robots.txt')
# @app.route('/sitemap.xml')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])


@ app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for('main.home'))
