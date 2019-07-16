'''
import os
from snyk import Snyk

snyk = Snyk(os.environ['SNYK_TOKEN'])
snyk.orgs()
>>> [Org, Org]
'''
from __future__ import annotations

import json
from urllib.parse import urljoin
from urllib.request import urlopen, Request
from typing import List, Dict, Any, Optional


SNYK_API_URL = 'https://snyk.io/api/v1/'
TIMEOUT = 10


class SnykError(Exception):
    pass


class HTTPClient:

    JSON_CONTENT_TYPE = 'application/json'

    def __init__(self, url: str, token: str, timeout: float):
        self.url = url
        self.token = token
        self.timeout = timeout

    @property
    def headers(self) -> Dict[str, str]:
        return {
            'Accept': self.JSON_CONTENT_TYPE,
            'Content-Type': self.JSON_CONTENT_TYPE,
            'Authorization': f'token {self.token}',
        }

    def get_json(self, path: str) -> Dict[str, Any]:
        api_url = urljoin(self.url, path)
        request = Request(api_url, headers=self.headers)
        response = urlopen(request, timeout=self.timeout)
        if 'application/json' not in response.getheader('Content-Type'):
            raise SnykError('Response is not JSON')
        data = json.load(response)
        response.close()
        return data

    def post_json(self, path: str, body: Dict[str, Any]) -> Any:
        api_url = urljoin(self.url, path)
        request = Request(
            api_url,
            data=json.dumps(body).encode('utf-8'),
            headers=self.headers,
            method='POST',
        )
        response = urlopen(request, timeout=self.timeout)
        data = json.load(response)
        response.close()
        return data

    def delete(self, path: str) -> None:
        api_url = urljoin(self.url, path)
        request = Request(
            api_url,
            headers=self.headers,
            method='DELETE',
        )
        response = urlopen(request, timeout=self.timeout)
        response.close()


class Group:

    def __init__(self, client: HTTPClient, name: str, id: str):
        self.client = client
        self.name = name
        self.id = id

    def create_org(self, name: str, source_org: Org = None):
        path = urljoin(urljoin('group/', f'{self.id}/'), 'org')
        body = {'name': name}
        if source_org:
            body['sourceOrgId'] = source_org.id
        data = self.client.post_json(path, body)
        return Org(self.client, data['name'], data['id'], self)


class Org:

    def __init__(
        self,
        client: HTTPClient,
        name: str,
        id: str,
        group: Optional[Group],
    ):
        self.client = client
        self.name = name
        self.id = id
        self.group = group

    @property
    def integrations(self) -> Dict[str, Any]:
        return self.client.get_json(f'org/{self.id}/integrations')

    def import_github_project(self, owner: str, name: str):
        github_integration_id = self.integrations['github']
        self.client.post_json(
            f'org/{self.id}/integrations/{github_integration_id}/import',
            {'target': {'owner': owner, 'name': name, 'branch': 'master'}}
        )

    def projects(self) -> List[Project]:
        data = self.client.get_json(f'org/{self.id}/projects')
        return [
            Project(self.client, d['name'], d['id'], self)
            for d in data['projects']
        ]


class Project:

    def __init__(self, client: HTTPClient, name: str, id: str, org: Org):
        self.client = client
        self.name = name
        self.id = id
        self.org = org

    def delete(self):
        path = f'org/{self.org.id}/project/{self.id}'
        self.client.delete(path)


class Snyk:

    def __init__(
        self, token: str, url: str = SNYK_API_URL, timeout: float = TIMEOUT,
    ):
        self.token = token
        self.url = url
        self.timeout = timeout

    @property
    def client(self) -> HTTPClient:
        return HTTPClient(self.url, self.token, self.timeout)

    def orgs(self) -> List[Org]:
        data = self.client.get_json('orgs')
        orgs = []
        groups: Dict[str, Group] = {}
        for org in data.get('orgs', []):
            if not org['group']:
                group = None
            elif org['group']['id'] in groups:
                group = groups[org['group']['id']]
            else:
                group = Group(
                    self.client,
                    org['group']['name'],
                    org['group']['id'],
                )
            orgs.append(Org(self.client, org['name'], org['id'], group))
        return orgs
