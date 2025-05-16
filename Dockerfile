FROM python:3.10-slim

RUN apt-get update && apt-get install -y git 

WORKDIR /app

COPY mwcp /app/mwcp

RUN pip install ./MWCP && cp -r /app/MWCP/mwcp/yara_repo/. /root/yara_repo/ 
