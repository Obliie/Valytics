# Use the mockserver/mockserver base image
FROM mockserver/mockserver

# Set the environment variable
ENV MOCKSERVER_INITIALIZATION_JSON_PATH /config/mockserver-config.json

# Copy your custom configuration file into the container
COPY containers/mock-server/mockserver-config.json /config/mockserver-config.json