FROM rabbitmq:3-management

ARG RABBITMQ_DEFAULT_PORT
ARG RABBITMQ_MANAGEMENT_PLUGIN_PORT

COPY rabbitmq.conf /etc/rabbitmq
COPY definitions.json /etc/rabbitmq

RUN sed -i s/RABBITMQ_DEFAULT_PORT/${RABBITMQ_DEFAULT_PORT}/g /etc/rabbitmq/rabbitmq.conf &&\
    sed -i s/RABBITMQ_MANAGEMENT_PLUGIN_PORT/${RABBITMQ_MANAGEMENT_PLUGIN_PORT}/g /etc/rabbitmq/rabbitmq.conf &&\
    cat /etc/rabbitmq/rabbitmq.conf &&\
    pip3 install -r common_requirements.txt -r requirements.txt
