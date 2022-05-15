# Crypto Tax Checker - Docker None

Quickly check your tax records for common mistakes.

## Installation - Docker

The easiest way to get up and running is with [Docker](https://www.docker.com/).

Just [install Docker](https://www.docker.com/get-started) and
[Docker Compose](https://docs.docker.com/compose/install/)
and then run:

```
make init
```

This will spin up a database, web worker, celery worker, and Redis broker and run your migrations.

You can then go to [localhost:8000](http://localhost:8000/) to view the app.

### Using the Makefile

You can run `make` to see other helper functions, and you can view the source
of the file in case you need to run any specific commands.

For example, you can run management commands in containers using the same method 
used in the `Makefile`. E.g.

```
docker-compose exec web python manage.py createsuperuser
```

## Installation - Native

You can also install/run the app directly on your OS using the instructions below.

Setup a virtualenv and install requirements
(this example uses [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/)):

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```


## Set up database

*If you are using Docker you can skip these steps.*

Create a database named `crypto_tax_checker`.

```
createdb crypto_tax_checker
```

Create database tables:

```
./manage.py migrate
```

## Playing with Postgres from Command Line

```bash
psql
```

will open a connection to terminal. To see Users, use `\du`

```bash
\list       # List the databases
\connect    # Connect to a database
\du         # List users in current database
\dt         # List tables in current database
\q          # quit
```

## Running server

**Docker:**

```bash
make start
```

To clean the volumes:
```bash
docker-compose down -v
```


**Native:**

```bash
./manage.py runserver
```

## Building front-end

To build JavaScript and CSS files, first install npm packages:

**Docker:**

```bash
make npm-install
```

**Native:**

```bash
npm install
```

Then build (and watch for changes locally):

**Docker:**

```bash
make npm-watch
```

**Native:**

```bash
npm run dev-watch
```

## Running Celery

Celery can be used to run background tasks. If you use Docker it will start automatically.

You can run it using:

```bash
celery -A crypto_tax_checker worker -l INFO
```

## Google Authentication Setup

To setup Google Authentication, follow the [instructions here](https://django-allauth.readthedocs.io/en/latest/providers.html#google).

## Twitter Authentication Setup

To setup Twitter Authentication, follow the [instructions here](https://django-allauth.readthedocs.io/en/latest/providers.html#twitter).

## Running Tests

To run tests:

**Docker:**

```bash
make test
```

**Native:**

```bash
./manage.py test
```

Or to test a specific app/module:

**Docker:**

```bash
docker-compose exec web python manage.py test apps.utils.tests.test_slugs
```

**Native:**

```bash
./manage.py test apps.utils.tests.test_slugs
```

On Linux-based systems you can watch for changes using the following:

```bash
find . -name '*.py' | entr python ./manage.py test
```
