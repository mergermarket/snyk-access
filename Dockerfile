FROM python:3.7 AS base

WORKDIR /opt/

ENV PYTHONPATH=.

COPY Pipfile Pipfile.lock ./

RUN pip install pipenv && \
    pipenv install --system

FROM base AS test

RUN pipenv install --system --dev

COPY ./snyk ./snyk
COPY ./tests ./tests
