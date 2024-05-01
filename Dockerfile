FROM python:3.7

RUN pip install pipenv
ADD . .
RUN pipenv install
