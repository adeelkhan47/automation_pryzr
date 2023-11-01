FROM --platform=linux/amd64 python:3.9

ENV DEBIAN_FRONTEND=noninteractive

RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    dpkg -i google-chrome-stable_current_amd64.deb && \
    apt-get install -f -y && \
    rm google-chrome-stable_current_amd64.deb

# Manually download and install ChromeDriver for version 118.0.5993.88
RUN wget https://chromedriver.storage.googleapis.com/118.0.5993.88/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip && \
    mv chromedriver /usr/bin/chromedriver && \
    chmod +x /usr/bin/chromedriver && \
    rm chromedriver_linux64.zip


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


