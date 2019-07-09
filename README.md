# Snyk SDK

For interacting with the Snyk API in Python (>= 3.7).

## Usage
```python
import os
from snyk import Snyk

snyk = Snyk(os.environ['SNYK_TOKEN'])
snyk.orgs()
>>> [Org, Org]
```
