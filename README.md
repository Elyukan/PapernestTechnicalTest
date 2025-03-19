# Papernest Technical Test

My technical test is in Python 3.10.16. I'm using Django4.1 and his framework DjangoRestFramework which provide tools to build REST API.

## Installation

### 1 - Poetry
I'm using Poetry which is a python package manager (like NPM). You can install it with your favorite package manager such as apt or directly on their website.
https://python-poetry.org/

If you struggle to install / use it, go to the next section.

Determine your python version (if it's not python 3.10.16 by default):

`poetry env use python3.10`

Install the dependencies:

`poetry install`

Run the project:

`poetry run manage.py runserver`

### 1(bis) - Requirements.txt

In case of you don't want to use poetry, you can also use a virtualenv and install it with pip:

`pip install -r requirements.txt`

NB: Don't forget to specify the python version

### 2 - Database setup

I'm using PostgreSQL so you have to run a postgresql server and create a database.

In Django, a good practice is to handle local settings in another file named `local_settings.py`.
Duplicate the `local_settings_exemple.py` file, rename it `local_settings.py` and fill it with your own database settings and logins.

Then, init the database:

`./manage.py migrate` or `poetry run manage.py migrate`


## How to use the application

### Database initialisation

In order to initialize the data we need to run the app, you have to run the following command:

`./manage.py init_network_provider_tower_data --path path/to/file` or `poetry run manage.py init_network_provider_tower_data --path path/to/file`

### Run the server

`./manage.py runserver` or `poetry run manage.py runserver`

It will run the server on this address `http://localhost:8000`

### Swagger

You can find the swagger at this url `http://localhost:8000/api/swagger/` on your browser.

### Endpoint

The main endpoint is at this endpoint :

`http://localhost:8000/api/coverage/`

This is a POST request which takes this payload format:

```
{
	"addresses": [
		{
			"address": "157 boulevard Mac Donald 75019 Paris",
			"identifier": "id1"
		},
		{
			"address": "5 avenue Anatole France 75007 Paris",
			"identifier": "id2"
		},
		{
			"address": "17 Rue René Cassin 51430 Bezannes",
			"identifier": "id7"
		}
	]
}
```

The return format is :

```
{
	"id1": {
		"SFR": {
			"2G": true,
			"3G": true,
			"4G": true
		},
		"Orange": {
			"2G": true,
			"3G": true,
			"4G": true
		},
		"Free": {
			"2G": true,
			"3G": true,
			"4G": true
		},
		"Bouygues": {
			"2G": true,
			"3G": true,
			"4G": true
		}
	},
	"id2": {
		"Orange": {
			"2G": true,
			"3G": true,
			"4G": true
		},
		"Bouygues": {
			"2G": true,
			"3G": true,
			"4G": true
		},
		"SFR": {
			"2G": true,
			"3G": true,
			"4G": true
		},
		"Free": {
			"2G": true,
			"3G": true,
			"4G": true
		}
	},
	"id7": {
		"Free": {
			"2G": true,
			"3G": true,
			"4G": true
		},
		"Orange": {
			"2G": true,
			"3G": true,
			"4G": true
		},
		"SFR": {
			"2G": true,
			"3G": true,
			"4G": true
		},
		"Bouygues": {
			"2G": true,
			"3G": true,
			"4G": true
		}
	}
}
```

### Settings

We are filtering the results that don't match enough to be sure to find the good address. In order to be sure, the public API send a matching score between `0.00` and `1.00` and we set a minimum value to determite if this result is a good match.

The settings variable is named `MIN_MATCH_SCORE` and is default value is `0.70`. 

You can modify it directly in the `local_settings.py` file.

### Admin

You can access to an administation interface at this url `http://localhost:8000/admin` in your browser.

It allows you to see the database instances for each models created.

In order to access it you have to create a superuser account, run the following command:

`./manage.py createsuperuser` or `poetry run manage.py createsuperuser`

And then you can log in.


### Tests (WIP)

You can run the tests with this following command:

`pytest`
