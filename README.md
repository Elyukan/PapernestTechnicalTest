# Papernest Technical Test

My technical test is in Python 3.10.16. I'm using Django4.1 and his framework DjangoRestFramework which provide tools to build REST API.

## Installation

### 1 - Poetry
I'm using Poetry which is a python package manager (like NPM). You can install it with your favorite package manager such as apt or directly on their website.
https://python-poetry.org/

If you're struggling to install / use it, go to the next section.

Determine your python version (if it's not python 3.10.16 by default):

`poetry env use python3.10`

Install the dependencies:
`poetry install`

Run the project:
`poetry run manage.py runserver`

### 1(bis) - Requirements.txt

In case of you don't want to use poetry, you can also use a virtualenv and install it with pip:
`pip install -r requirements.txt`

### 2 - Database setup

I'm using PostgreSQL so you have to launch a postgresql server and create a database.

In Django, a good practice is to handle local settings in another file which is called `local_settings.py`.
Duplicate the `local_settings_exemple.py` file, rename it `local_settings.py` and fill it with your own database settings and logins.

Then, init the database:
`./manage.py migrate` or `poetry run manage.py migrate`