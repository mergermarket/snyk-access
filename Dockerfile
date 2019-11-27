FROM python:3.8.0-alpine3.10 AS base

WORKDIR /opt/

ENV PYTHONPATH=/opt/

COPY Pipfile Pipfile.lock ./

RUN apk add --no-cache --virtual .build-deps gcc musl-dev && \
    pip install pipenv && \
    pipenv install --system && \
    apk del .build-deps

FROM base AS test

RUN apk add --no-cache --virtual .build-deps gcc musl-dev && \
    pipenv install --system --dev && \
    apk del .build-deps

COPY ./snyk ./snyk
COPY ./test ./test
COPY *.py ./

FROM test AS testrun

RUN py.test --flake8 --cov --mypy --mypy-ignore-missing-imports

FROM base AS main

COPY ./snyk ./snyk
COPY *.py ./

ENTRYPOINT ["python", "/opt/snyk_access.py"]
