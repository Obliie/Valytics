# Use an official Grafana runtime as the base image
FROM grafana/grafana:latest

# Set environment variables if needed (e.g., for configuration)
# ENV GRAFANA_VARIABLE_NAME=value

# Copy custom configuration files if needed
# COPY config/custom-config.ini /etc/grafana/custom-config.ini

# Expose the Grafana port (default is 3000)
EXPOSE 3000

# Start Grafana
CMD ["grafana-server", "--config=/etc/grafana/grafana.ini", "cfg:default.paths.data=/var/lib/grafana", "cfg:default.paths.logs=/var/log/grafana"]
