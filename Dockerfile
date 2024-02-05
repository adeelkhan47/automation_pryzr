# Use the official Python 3.9 image as the base image
FROM --platform=linux/amd64 python:3.9

# Set environment variables to avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install Google Chrome and Tesseract OCR
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends google-chrome-stable tesseract-ocr tesseract-ocr-eng && \
    google-chrome-stable --version && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set up the working directory and copy the necessary files
WORKDIR /app/
COPY src /app/src/
COPY requirements.txt /app/
COPY docker-entrypoint.sh /usr/bin/

# Set the PYTHONPATH environment variable
ENV PYTHONPATH=${PYTHONPATH}:${PWD}

# Create a virtual environment
RUN python3 -m venv .venv

# Set the entry point for the container
ENTRYPOINT ["/usr/bin/docker-entrypoint.sh"]
