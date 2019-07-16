import json
import unittest

import httpretty

import snyk


class TestCreateOrg(unittest.TestCase):

    def setUp(self):
        httpretty.enable(allow_net_connect=False)
        self.base_url = 'http://snyk'
        httpretty.register_uri(
            httpretty.POST,
            self.base_url + '/group/1/org',
            body=json.dumps({
                'id': 'aaaaaaaa-4438-cccc-a3ba-eeeeeeeeeeee',
                'name': 'bar',
                'created': '2019-07-16T16:08:47.648Z',
            }),
            adding_headers={
                'Content-Type': 'text/plain; charset=utf-8',
            },
        )
        self.client = snyk.HTTPClient(self.base_url, 'token', 1)
        self.group = snyk.Group(self.client, 'foo', '1')
        self.org = self.group.create_org('bar')

    def tearDown(self):
        httpretty.disable()

    def test_has_correct_id(self):
        assert self.org.id == 'aaaaaaaa-4438-cccc-a3ba-eeeeeeeeeeee'

    def test_has_correct_name(self):
        assert self.org.name == 'bar'

    def test_has_the_correct_group_assigned(self):
        assert self.org.group is self.group


class TestCreateOrgFromSource(unittest.TestCase):

    def setUp(self):
        httpretty.enable(allow_net_connect=False)
        self.base_url = 'http://snyk'
        httpretty.register_uri(
            httpretty.POST,
            self.base_url + '/group/1/org',
            body=json.dumps({
                'id': 'aaaaaaaa-4438-cccc-a3ba-eeeeeeeeeeee',
                'name': 'bar',
                'created': '2019-07-16T16:08:47.648Z',
            }),
            adding_headers={
                'Content-Type': 'text/plain; charset=utf-8',
            },
        )
        self.client = snyk.HTTPClient(self.base_url, 'token', 1)
        self.group = snyk.Group(self.client, 'foo', '1')
        self.source_org = snyk.Org(self.client, 'foo', '1', self.group)
        self.org = self.group.create_org('bar', self.source_org)

    def tearDown(self):
        httpretty.disable()

    def test_passes_source_org(self):
        request = httpretty.last_request()
        assert request.parsed_body['sourceOrgId'] == self.source_org.id

    def test_has_correct_id(self):
        assert self.org.id == 'aaaaaaaa-4438-cccc-a3ba-eeeeeeeeeeee'

    def test_has_correct_name(self):
        assert self.org.name == 'bar'

    def test_has_the_correct_group_assigned(self):
        assert self.org.group is self.group
