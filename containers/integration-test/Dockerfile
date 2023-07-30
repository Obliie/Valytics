FROM python:3.11.4-slim

ENV PYTHONPATH "${PYTHONPATH}:/protobufs"

COPY builder/integration-test/requirements.txt requirements.txt
RUN pip3 install -r requirements.txt