# hadolint ignore=DL3007
FROM python:3.9-slim-buster

WORKDIR /tmp/app
COPY . .
RUN pip install -r requirements.txt
ENTRYPOINT ["python3", "app/parser.py"]
CMD []