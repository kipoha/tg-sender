FROM python:3.10-alpine

WORKDIR /opt/services/backend/

COPY ../requirements.txt .

COPY . .

RUN  pip install -r requirements.txt
