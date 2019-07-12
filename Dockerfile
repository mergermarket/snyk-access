FROM python:3.7 AS base

WORKDIR /opt/

ENV PYTHONPATH=/opt/

COPY Pipfile Pipfile.lock ./

RUN pip install pipenv && \
    pipenv install --system

FROM base AS test

RUN pipenv install --system --dev

COPY ./snyk ./snyk
COPY ./tests ./tests
COPY *.py ./

FROM test AS testrun

RUN py.test --flake8 --cov --mypy --mypy-ignore-missing-imports

FROM base AS main

RUN pipenv install --system

COPY ./snyk ./snyk
COPY *.py ./

ENTRYPOINT ["python", "/opt/snyk_access.py"]
