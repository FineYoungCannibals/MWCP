FROM python:3.10-slim

RUN apt-get update  && apt-get upgrade -y

WORKDIR /app

COPY src .
# test

RUN pip install . && cp -r /app/mwcp/yara_repo/. /opt/yara_repo/ 
