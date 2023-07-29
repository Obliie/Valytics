FROM python:3.11.4-slim

COPY builder/python-lint/.flake8 .flake8

COPY builder/python-lint/requirements.txt requirements.txt
RUN pip3 install -r requirements.txt