# Snyk Access

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

## Run tests
```bash
./test.sh
```
