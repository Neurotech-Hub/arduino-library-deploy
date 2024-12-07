# Use an official lightweight Python image
FROM python:3.11-slim

# Install necessary packages for git and requests
RUN apt-get update && \
    apt-get install -y git curl jq && \
    pip install requests semver && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /action

# Copy the Python script into the container
COPY action.py /action/action.py

# Mark the GitHub Actions workspace as a safe Git directory
RUN git config --global --add safe.directory /github/workspace

# Copy the entrypoint script into the container
COPY entrypoint.sh /action/entrypoint.sh

# Make the entrypoint script executable
RUN chmod +x /action/entrypoint.sh

# Define the entrypoint
ENTRYPOINT ["python", "/action/action.py"]
