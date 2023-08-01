FROM python:3.11.4-slim

COPY containers/python-lint/.flake8 .flake8

COPY containers/python-lint/requirements.txt requirements.txt
RUN pip3 install -r requirements.txt