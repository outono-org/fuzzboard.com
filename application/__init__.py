import os
from dotenv import load_dotenv
from flask import Flask
from .views import bp

load_dotenv()

app = Flask(__name__)
app.register_blueprint(bp)

# Secret Key config for WTF forms.
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
