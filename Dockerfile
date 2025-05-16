FROM python:3.10-slim

RUN apt-get update && apt-get install -y git 

WORKDIR /app

COPY setup.cfg setup.py /app
COPY mwcp /app/mwcp

RUN pip install . && cp -r /app/mwcp/yara_repo/. /root/yara_repo/ 
