# Dockerfile
FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y git curl jq && \
    pip install requests semver && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Mark the GitHub workspace as a safe directory
RUN git config --global --add safe.directory /github/workspace

WORKDIR /action

COPY action.py /action/action.py
COPY entrypoint.sh /action/entrypoint.sh

RUN chmod +x /action/entrypoint.sh

ENTRYPOINT ["python", "/action/action.py"]
