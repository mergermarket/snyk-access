# Snyk Access
[![Docker Cloud Build Status](https://img.shields.io/docker/cloud/build/mergermarket/snyk-access.svg)](https://hub.docker.com/r/mergermarket/snyk-access)

Imports projects from GitHub into Synk.

## Usage
```bash
docker container run --rm \
    -e SNYK_TOKEN \
    -v $(pwd):$(pwd) \
    -w $(pwd) \
    mergermarket/snyk-access --owner <github-owner> --org <snyk-org> --access-file ./access.json
```

Example of minimal `access.json` config:
```json
[
  {
    "apps": {
      "snyk": [
        "first-repo",
        "second-repo"
      ]
    }
  }
]
```

Example of more complex `access.json` config:
```json
[
  {
    "apps": {
      "snyk": true
    },
    "repos": [
      "first-repo",
      "second-repo",
      "third-repo",
      "fourth-repo"
    ]
  },
  {
    "apps": {
      "snyk": [
        "fifth-repo"
      ]
    },
    "repos": [
        "fifth-repo",
        "a-repo",
        "b-repo",
        "c-repo"
    ]
  }
]
```

## Run tests
```bash
./test.sh
```
