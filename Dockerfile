FROM python:3.9

ENV DEBIAN_FRONTEND=noninteractive

# Install necessary packages
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y wget gnupg2 ca-certificates apt-transport-https && \
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable

# Make sure Chrome is available at /usr/bin/google-chrome-stable
RUN which google-chrome-stable

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


