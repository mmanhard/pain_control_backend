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

[Live version of the application can be found here!](http://www.mypaincontroller.com/)

[Live version of the back-end can be found here!](http://api.mypaincontroller.com/)

## Tech Stack

Back-End: Flask + Python

Database: MongoDB

Tools: Webpack + Babel

[Check here for the front-end stack!](https://github.com/mmanhard/pain_control_app#tech-stack)

## Installation and Usage

### Install

Follow the steps below in the local directory where your forked repo is located:

1. Create and activate a virtual environment to manage the dependencies for this
project:
```
$ python3 -m venv
$ . venv/bin/activate
```

2. Install the app's dependencies:
```
$ pip3 install -r requirements.txt
```

### Build and Run - Development

After activating the virtual environment and installing dependencies, build and
serve the app with the following steps:
```
$ export FLASK_APP=src
$ export FLASK_ENV=development
$ flask run
```

By default, the flask development server will listen on port **5000**. If you
need to use a different one, append `-p PORT_NUM`, where `PORT_NUM` is the
desired port number, to `flask run`.

### Build and Run - Production

After activating the virtual environment and installing dependencies, build and
serve the app with the following command:
```
$ gunicorn 'src:create_app()'
```

### Deployment

The [live version](http://api.mypaincontroller.com/) of the backend is hosted
on Heroku.

## Application Overview

An overview of the app as well as some demos can be found
[here!](https://github.com/mmanhard/pain_control_app#application-overview)

## Future Improvements

This app is a work-in-progress. Expect a list of potential improvements to be
added here!