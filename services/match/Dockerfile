FROM python:3.11.4-slim

ENV PYTHONPATH "${PYTHONPATH}:/service_common:/protobufs"

COPY services/match/requirements.txt requirements.txt
COPY services/common/common_requirements.txt common_requirements.txt

RUN pip3 install -r common_requirements.txt -r requirements.txt