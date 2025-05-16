FROM python:3.10-slim

RUN apt-get update && apt-get install -y git 

WORKDIR /app

COPY src .

RUN pip install . && cp -r /app/mwcp/yara_repo/. /root/yara_repo/ 
