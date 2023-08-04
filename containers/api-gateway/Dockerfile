FROM envoyproxy/envoy:v1.22.0

ARG RIOT_INGEST_SERVICE_PORT
ARG MATCH_SERVICE_PORT

COPY ./containers/api-gateway/envoy.json /etc/envoy/envoy.json
RUN sed -i s/RIOT_INGEST_SERVICE_PORT/${RIOT_INGEST_SERVICE_PORT}/g /etc/envoy/envoy.json &&\
    sed -i s/MATCH_SERVICE_PORT/${MATCH_SERVICE_PORT}/g /etc/envoy/envoy.json