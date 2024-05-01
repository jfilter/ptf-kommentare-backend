FROM python:3.7

WORKDIR /app

RUN pip install pipenv
ADD . .
RUN pipenv install --system
CMD gunicorn app:app
