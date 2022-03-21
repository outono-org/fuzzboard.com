import os
from dotenv import load_dotenv
from flask import Flask, redirect, url_for, request, send_from_directory
from flask_talisman import Talisman, GOOGLE_CSP_POLICY
from .views import bp, simplemde
from .auth import auth
from .admin import admin
from .feeds import feed
from .database import mongo
from .emails import mail

load_dotenv()

app = Flask(__name__)
app.register_blueprint(bp)
app.register_blueprint(auth)
app.register_blueprint(admin)
app.register_blueprint(feed)

csp = {
    'default-src': [
        '\'self\'',
        '*.googleapis.com',
        '*.googletagmanager.com',
        '*.gstatic.com',
        'cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css',
        '*.googleanalytics.com',
        '*.google-analytics.com',
        'cdn.ckeditor.com/*',
        'unsafe-inline',
        '\'unsafe-inline\'',
        'cdn.jsdelivr.net/simplemde/latest/simplemde.min.css',
        'maxcdn.bootstrapcdn.com/font-awesome/latest/css/font-awesome.min.css',
        'https://maxcdn.bootstrapcdn.com/font-awesome/latest/fonts/fontawesome-webfont.woff2',
        'https://maxcdn.bootstrapcdn.com/font-awesome/latest/fonts/fontawesome-webfont.woff',
        'maxcdn.bootstrapcdn.com/font-awesome/latest/fonts/fontawesome-webfont.ttf',
        'https://cdn.jsdelivr.net/codemirror.spell-checker/latest/en_US.aff',
        'https://cdn.jsdelivr.net/codemirror.spell-checker/latest/en_US.dic',
    ],
    'script-src': [
        '\'self\'',
        'unsafe-inline',
        '\'unsafe-inline\'',
        '\'unsafe-eval\'',
        'ajax.googleapis.com',
        'code.jquery.com',
        'google.com',
        'googletagmanager.com',
        '*.googletagmanager.com',
        '*.googleanalytics.com',
        '*.google-analytics.com',
        'googletagmanager.com/',
        'cdn.ckeditor.com/*',
        'cdn.ckeditor.com/4.14.0/basic/ckeditor.js',
        'cdn.ckeditor.com/4.14.0/basic/*',
        'cdn.ckeditor.com/4.14.0/basic/styles.js',
        'cdn.ckeditor.com/4.14.0/basic/lang/en.js',
        'cdn.jsdelivr.net/simplemde/latest/simplemde.min.js',
    ],
    'script-src-elem': [
        '\'self\'',
        '\'unsafe-inline\'',
        'googletagmanager.com',
        '*.googletagmanager.com',
        '*.googleanalytics.com',
        '*.google-analytics.com',
        'googletagmanager.com/',
        'cdn.jsdelivr.net/simplemde/latest/simplemde.min.js',
    ],
    'script-src-attr': [
        '\'self\'',
        '\'unsafe-inline\'',
        '*.googletagmanager.com',
    ],
    'img-src': [
        '\'self\'',
        'https://cdn.sstatic.net/Img/unified/wmd-buttons.svg',
    ],
}
Talisman(app,
         content_security_policy=csp,
         content_security_policy_nonce_in=['script-src']
         )

# Secret Key config for WTF forms.
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")

# Set maximum allowed payload for user uploads to 2.5MB
app.config['MAX_CONTENT_LENGTH'] = 2.5 * 1000 * 1000

# PyMongo Config
mongo.init_app(app, uri=os.environ.get("MONGODB_URI"),
               ssl=True, ssl_cert_reqs='CERT_NONE')


# Session config. Followed documentation

app.config["SESSION_TYPE"] = "mongodb"
app.config["SESSION_MONGODB"] = mongo.db

# Sendgrid setup.
app.config['SECRET_KEY'] = 'top-secret!'
app.config['MAIL_SERVER'] = 'smtp.sendgrid.net'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'apikey'
app.config['MAIL_PASSWORD'] = os.environ.get('SENDGRID_API_KEY')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')

mail.init_app(app)


app.config['SIMPLEMDE_JS_IIFE'] = True
app.config['SIMPLEMDE_USE_CDN'] = True
simplemde.init_app(app)


@ app.route('/robots.txt')
# @app.route('/sitemap.xml')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])


@ app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for('main.home'))
