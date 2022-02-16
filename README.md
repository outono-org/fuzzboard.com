## Getting Started

**_Prerequisites: Python 3.9.0._**

```shell script
$ git clone https://github.com/outono-org/startup-jobs.git

$ cd startup-jobs

$ python3 -m venv venv              # Create a virtual environment.

$ source venv/bin/activate          # Activate your virtual environment.

$ pip install -r requirements.txt   # Install project requirements.

$ export FLASK_APP=app.py

$ export FLASK_ENV=development      # Enable hot reloading, debug mode.

$ flask run
```

The app will only work locally when the debug is enabled due to [Flask-talisman](https://github.com/GoogleCloudPlatform/flask-talisman), which forces all connects to https.

The default content security policy is extremely strict and will prevent loading any resources that are not in the same domain as the application. [Here are some examples on how to change the default policy](https://github.com/GoogleCloudPlatform/flask-talisman#content-security-policy).

## Setting up the database

Create a `.env` file in the root directory of your project and connect the app to a MongoDB atlas cluster.
