FROM python:3.11.4-slim

ENV PYTHONPATH "${PYTHONPATH}:/service_common:/protobufs"

COPY containers/integration-test/requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
