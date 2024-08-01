# Flask Application

This is a Flask application configured to be run using Gunicorn.

## Running the Application

To run the application using Gunicorn, use the following command:

```bash
gunicorn -c gunicorn_config.py run:app
