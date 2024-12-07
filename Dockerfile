# Use the latest official Ubuntu image
FROM ubuntu:latest

# Install necessary tools
RUN apt-get update && \
    apt-get install -y git curl jq bash && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /action

# Copy the entrypoint script into the container
COPY entrypoint.sh /action/entrypoint.sh

# Make the script executable
RUN chmod +x /action/entrypoint.sh

# Define the entrypoint
ENTRYPOINT ["/action/entrypoint.sh"]
