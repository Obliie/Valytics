FROM rabbitmq:3-management

ARG RABBITMQ_DEFAULT_PORT
ARG RABBITMQ_MANAGEMENT_PLUGIN_PORT

COPY rabbitmq.conf /etc/rabbitmq
COPY definitions.json /etc/rabbitmq

RUN cat /etc/rabbitmq/rabbitmq.conf
