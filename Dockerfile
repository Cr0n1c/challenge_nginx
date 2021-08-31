# hadolint ignore=DL3007
FROM python:3.9-slim-buster

WORKDIR /tmp/app

COPY . .

# Change this file as much as needed to fit with your implementation
#
# Just make sure that it fits with the running instructions from the README

ENTRYPOINT ["python3", "app/parser.py"]
CMD []