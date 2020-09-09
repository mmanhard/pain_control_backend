# Pain Control - Back-End

Pain control is a web application that gives users the ability to track their
pain levels over time in an effort to better understand how they feel on a
regular basis.

Throughout the day, users enter the pain levels they're feeling in different
parts of their body, called pain points. Later on, Pain Control maps out how
each of the user's pain points have changed throughout the day as well as
over time. This information empowers the user by helping them make insights about
their pain and giving them an effective tool to communicate their pain history to
doctors.

Please note: this is the source code for the **back-end**. [Front-end source code can be found here!](https://github.com/mmanhard/pain_control_app)

## Live Version

[Live version of the application can be found here!](https://www.mypaincontroller.com/)

[Live version of the back-end can be found here!](https://api.mypaincontroller.com/)

## Tech Stack

Back-End: Flask + Python

Database: MongoDB

[Check here for the front-end stack!](https://github.com/mmanhard/pain_control_app#tech-stack)

## Installation and Usage

#### Requirements

* `pip3` >= v19.0.3
* `MongoDB` >= v4.2.2
* `python` >= v3.7.4
* `heroku CLI` >= 7.42.11 (if deploying)

#### Install

Follow the steps below in the local directory where your forked repo is located:

##### 1. Create and activate a virtual environment to manage the dependencies for this
project:
```
$ python3 -m venv venv
$ . venv/bin/activate
```

##### 2. Install the app's dependencies:
```
$ pip3 install -r requirements.txt
```

##### 3. Start mongod, the daemon process for MongoDB. Do the following in a separate
tab and keep it open and running while using the app:
```
$ mongod
```

By default, `mongod` will store data at `/data/db` and run on port `27017`.
Look [here](https://docs.mongodb.com/manual/reference/program/mongod/) to
modify either of these default settings.

##### 4. Configure the database:
```
$ export MONGODB_URI=`mongodb://localhost:<PORT_NUM>/<DATABASE_NAME>`
```

Where `<PORT_NUM>` is the port your `mongod` process is running on and
`<DATABASE_NAME>` is the name you would like to give your database.

#### Build and Run - Development

After activating the virtual environment and installing dependencies, build and
serve the app with the following steps:
```
$ export FLASK_APP=src
$ export FLASK_ENV=development
$ export APP_SETTINGS='config.DevelopmentConfig'
$ flask run
```

By default, the flask development server will listen on port **5000**. If you
need to use a different one, append `-p PORT_NUM`, where `PORT_NUM` is the
desired port number, to `flask run`.

#### Build and Run - Production

After activating the virtual environment and installing dependencies, build and
serve the app with the following commands:
```
$ export APP_SETTINGS='config.ProductionConfig'
$ gunicorn 'src:create_app()'
```

#### Deployment

The [live version](https://api.mypaincontroller.com/) of the backend is hosted
on Heroku.

You can host your own forked version by following the steps below from the
directory where your local repo is located:

##### 1. Login in to Heroku and create a new Heroku app using the Heroku CLI:

```
$ heroku login
$ heroku create <APP_NAME>
```

Where `<APP_NAME>` is the name you have selected for your back-end application.

##### 2. Configure the app for production:

```
$ heroku config:set APP_SETTINGS=config.ProductionConfig -a <APP_NAME>
```

##### 3. Add all files, commit them, and push the commit to the Heroku git repo:

```
$ heroku git:remote -a <APP_NAME>
$ git add .
$ git commit -am "Enter a nice commit message here!"
$ git push heroku master
```

After pushing changes, Heroku will automatically build the production version
of the app and run it using the steps detailed earlier. Heroku will let you know
the URL where you can visit your deployed version of the app.