FROM --platform=linux/amd64 python:3.9

ENV DEBIAN_FRONTEND=noninteractive

# Add Google Chrome to the repositories
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list

# Update the packages
RUN apt-get update
# Install Google Chrome with verbose output
RUN apt-get install -y google-chrome-stable || (apt-get update && apt-get -f install -y)



RUN wget https://chromedriver.storage.googleapis.com/118.0.5993.88/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip && \
    mv chromedriver /usr/bin/chromedriver && \
    chmod +x /usr/bin/chromedriver && \
    rm chromedriver_linux64.zip

RUN apt-get update


RUN apt-get install -y tesseract-ocr

# Optional: Install any languages you need, e.g., English
RUN apt-get install -y tesseract-ocr-eng


RUN mkdir /app/
WORKDIR /app/

COPY src /app/src/
#COPY etc /app/etc/
COPY requirements.txt /app/
#COPY static /app/static

ENV PYTHONPATH=${PYTHONPATH}:${PWD}
RUN python3 -m venv .venv
COPY docker-entrypoint.sh /usr/bin/


ENTRYPOINT ["/usr/bin/docker-entrypoint.sh"]


