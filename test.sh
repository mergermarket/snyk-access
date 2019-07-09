#!/bin/bash

set -euo pipefail

IMAGE_ID="$(basename $(pwd))"

docker image build -t "${IMAGE_ID}:test" --target=test .

docker container run --rm --name "${IMAGE_ID}-test" \
    "${IMAGE_ID}:test" \
    py.test --flake8 --cov --mypy --mypy-ignore-missing-imports
