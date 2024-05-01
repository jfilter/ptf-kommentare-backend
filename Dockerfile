FROM python:3.7

WORKDIR /app

RUN pip install pipenv
ADD . .
RUN pipenv install --system
RUN pip uninstall -y Werkzeug
RUN pip install Werkzeug==1.0.1
CMD gunicorn app:app
