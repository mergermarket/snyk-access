import unittest

import httpretty

import snyk


class TestGroup(unittest.TestCase):

    def setUp(self):
        httpretty.enable(allow_net_connect=False)
        self.base_url = 'http://snyk'
        httpretty.register_uri(
            httpretty.POST,
            self.base_url + '/group/1/org',
            body='OK',
            adding_headers={
                'Content-Type': 'text/plain; charset=utf-8',
            },
        )
        self.client = snyk.HTTPClient(self.base_url, 'token', 1)
        self.group = snyk.Group(self.client, 'foo', '1')

    def tearDown(self):
        httpretty.disable()

    def test_create_org(self):
        self.group.create_org('bar')

        request = httpretty.last_request()

        assert request.parsed_body['name'] == 'bar'

    def test_create_org_with_source_org(self):
        source_org = snyk.Org(self.client, 'foo', '1', self.group)
        self.group.create_org('bar', source_org)

        request = httpretty.last_request()

        assert request.parsed_body['name'] == 'bar'
        assert request.parsed_body['sourceOrgId'] == source_org.id
