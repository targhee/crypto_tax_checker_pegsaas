# crypto_tax_checker

Quickly check your tax records for common mistakes.

## Installation

Setup a virtualenv and install requirements
(this example uses [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/)):

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Set up database

Create a database named `crypto_tax_checker`.

```
createdb crypto_tax_checker
```

Create database tables:

```
./manage.py migrate
```

## Running server

```bash
./manage.py runserver
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

## Building front-end

To build JavaScript and CSS files, first install npm packages:

```bash
npm install
```

Then build (and watch for changes locally):

```bash
npm run dev-watch
```

## Running Celery

Celery can be used to run background tasks.

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

```bash
./manage.py test
```

Or to test a specific app/module:

```bash
./manage.py test apps.utils.tests.test_slugs
```

On Linux-based systems you can watch for changes using the following:

```bash
find . -name '*.py' | entr python ./manage.py test
```
