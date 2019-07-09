import unittest

import httpretty

import snyk


class TestProjectDelete(unittest.TestCase):

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
        self.project = snyk.Project(client, 'p-foo', 42, org)

    def tearDown(self):
        httpretty.disable()

    def test_delete(self):
        self.project.delete()

        request = httpretty.last_request()

        assert request.method == httpretty.DELETE
