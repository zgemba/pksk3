# PKSK replacement

Minimal Flask replacement for the PKSK website.

## Local development

Create a Python 3.13 virtual environment, install the dependencies, and run:

```text
pip install -r requirements-dev.txt
flask --app wsgi run --debug
```

The application is currently a runnable scaffold. The implementation plan is documented in [`recap.md`](recap.md).
