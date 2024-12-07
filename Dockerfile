FROM python:3.11-slim

# Install necessary dependencies
RUN apt-get update && \
    apt-get install -y git curl jq && \
    pip install requests semver && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /action

# Copy the Python script and entrypoint shell script into the container
COPY action.py /action/action.py
COPY entrypoint.sh /action/entrypoint.sh

# Make sure the entrypoint script is executable
RUN chmod +x /action/entrypoint.sh

# Set the entrypoint to the shell script
ENTRYPOINT ["/action/entrypoint.sh"]
