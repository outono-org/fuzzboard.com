import os
from dotenv import load_dotenv
from flask import Flask
from .views import bp
from .emails import mail

load_dotenv()

app = Flask(__name__)
app.register_blueprint(bp)

# Secret Key config for WTF forms.
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")

# Email setup
app.config["MAIL_DEFAULT_SENDER"] = "malikpiara@gmail.com"
app.config["MAIL_SERVER"] = "smtp.googlemail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")


mail.init_app(app)
