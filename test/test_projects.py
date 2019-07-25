import unittest

import httpretty

import snyk


class TestProject(unittest.TestCase):

    def setUp(self):
        httpretty.enable(allow_net_connect=False)
        base_url = 'http://snyk'
        httpretty.register_uri(
            httpretty.DELETE,
            base_url + '/org/a1/project/42',
            body='{}',
            adding_headers={
                'Content-Type': 'application/json',
            },
        )
        client = snyk.HTTPClient(base_url, 'token', 1)
        org = snyk.Org(
            client,
            'foo',
            'a1',
            snyk.Group(client, 'foo', '1'),
        )
        data = {
            'id': '42',
            'issueCountsBySeverity': {
                'medium': 2,
                'low': 0,
                'high': 0
            },
            'created': '2019-06-18T22:20:10.232Z',
            'totalDependencies': 16,
            'readOnly': False,
            'type': 'pip',
            'imageTag': '0.0.0',
            'lastTestedDate': '2019-07-08T06:16:26.386Z',
            'testFrequency': 'daily',
            'origin': 'github',
            'name': 'owner/p-foo:requirements.txt'
        }
        self.project = snyk.Project(client, data, org)

    def tearDown(self):
        httpretty.disable()

    def test_delete(self):
        self.project.delete()

        request = httpretty.last_request()

        assert request.method == httpretty.DELETE

    def test_repo_name(self):
        assert self.project.repo_name == 'p-foo'
