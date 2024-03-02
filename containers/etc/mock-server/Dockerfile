FROM mockserver/mockserver:latest

# Set the environment variable to disable MockServer logging
ENV MOCKSERVER_LOG_LEVEL=WARN

# Set the environment variable for MockServer initialization JSON path
ENV MOCKSERVER_INITIALIZATION_JSON_PATH /etc/mockserver/mockserver-config.json

# Copy your custom configuration file
COPY containers/etc/mock-server/mockserver-config.json /etc/mockserver/mockserver-config.json
