FROM python:3.10.8-slim

ARG DB_USERNAME
ARG DB_PASSWORD
ARG DB_HOST
ARG DB_PORT
ARG DB_NAME
ARG DB_SCHEMA

ENV DB_USERNAME=${DB_USERNAME}
ENV DB_PASSWORD=${DB_PASSWORD}
ENV DB_HOST=${DB_HOST}
ENV DB_PORT=${DB_PORT}
ENV DB_NAME=${DB_NAME}
ENV DB_SCHEMA=${DB_SCHEMA}

ENV PYTHONUNBUFFERED 1

WORKDIR /app
RUN apt-get update && apt-get install -y jq

COPY Pipfile Pipfile.lock ./

RUN pip3 install pipenv
# https://stackoverflow.com/questions/46503947/how-to-get-pipenv-running-in-docker
RUN pipenv install --system --deploy --ignore-pipfile
RUN pip3 install awscli

COPY . ./

# https://stackoverflow.com/questions/49133234/docker-entrypoint-with-env-variable-and-optional-arguments
ENTRYPOINT [ "/bin/bash", "./ops/run.sh" ]