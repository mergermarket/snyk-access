import json
import unittest

import httpretty

import snyk


class TestOrgs(unittest.TestCase):

    def setUp(self):
        httpretty.enable(allow_net_connect=False)
        base_url = 'http://snyk'
        httpretty.register_uri(
            httpretty.GET,
            base_url + '/orgs',
            body=json.dumps({
               'orgs': [
                  {
                     'group': {
                        'id': 'aaaaaaaa-badd-cccc-b463-eeeeeeeeeeee',
                        'name': 'FooGroup'
                     },
                     'name': 'BarOrg',
                     'id': '7b7b7b7b-bbbb-4172-dddd-eeeeeeeeeeee'
                  },
                  {
                     'group': {
                        'id': 'aaaaaaaa-badd-cccc-b463-eeeeeeeeeeee',
                        'name': 'FooGroup'
                     },
                     'name': 'RabOrg',
                     'id': 'eeeeeeee-bbbb-4172-dddd-aaaaaaaaaaaa'
                  }
               ]
            }),
            adding_headers={
                'Content-Type': 'application/json',
            },
        )
        s = snyk.Snyk('token', url=base_url)
        self.orgs = s.orgs()

    def tearDown(self):
        httpretty.disable()

    def test_two_orgs(self):
        assert len(self.orgs) == 2

    def test_org_name(self):
        assert self.orgs[0].name == 'BarOrg'

    def test_org_id(self):
        assert self.orgs[0].id == '7b7b7b7b-bbbb-4172-dddd-eeeeeeeeeeee'

    def test_org_group_name(self):
        assert self.orgs[0].group.name == 'FooGroup'

    def test_org_group_id(self):
        assert self.orgs[0].group.id == 'aaaaaaaa-badd-cccc-b463-eeeeeeeeeeee'


class TestImportProjects(unittest.TestCase):

    def setUp(self):
        httpretty.enable(allow_net_connect=False)
        base_url = 'http://snyk'
        httpretty.register_uri(
            httpretty.GET,
            base_url + '/org/a1/integrations',
            body=json.dumps({
               'github': 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee',
               'ecr': 'ffffffff-gggg-hhhh-iiii-jjjjjjjjjjjj'
            }),
            adding_headers={
                'Content-Type': 'application/json',
            },
        )
        httpretty.register_uri(
            httpretty.POST,
            base_url + (
                '/org/a1/integrations/'
                'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee/import'
            ),
            body='{}',
            adding_headers={
                'Content-Type': 'application/json',
            },
        )
        client = snyk.HTTPClient(base_url, 'token', 1)
        self.org = snyk.Org(
            client,
            'foo',
            'a1',
            snyk.Group(client, 'foo', '1'),
        )

    def tearDown(self):
        httpretty.disable()

    def test_import_github_project(self):
        self.org.import_github_project('owner', 'name')

        request = httpretty.last_request()

        assert request.parsed_body['target']['owner'] == 'owner'
        assert request.parsed_body['target']['name'] == 'name'
        assert request.parsed_body['target']['branch'] == 'master'


class TestListProjects(unittest.TestCase):

    def setUp(self):
        httpretty.enable(allow_net_connect=False)
        base_url = 'http://snyk'
        httpretty.register_uri(
            httpretty.GET,
            base_url + '/org/a1/projects',
            body=json.dumps({
                'org': {
                    'name': 'Foo',
                    'id': 'a1'
                },
                'projects': [
                    {
                        'type': 'golangdep',
                        'readOnly': False,
                        'totalDependencies': 54,
                        'created': '2019-06-19T10:01:27.128Z',
                        'id': '1',
                        'issueCountsBySeverity': {
                            'medium': 0,
                            'low': 0,
                            'high': 0
                        },
                        'name': 'owner/team-metadata-sync:Gopkg.lock',
                        'origin': 'github',
                        'testFrequency': 'daily',
                        'lastTestedDate': '2019-07-08T07:54:45.015Z',
                        'imageTag': '0.0.0'
                    },
                    {
                        'id': '2',
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
                        'name': 'owner/build-lambda:requirements.txt'
                    },
                    {
                        'testFrequency': 'daily',
                        'name': 'jenkins-autoscaler:latest',
                        'origin': 'ecr',
                        'lastTestedDate': '2019-07-08T05:56:23.695Z',
                        'imageTag': 'latest',
                        'type': 'apk',
                        'readOnly': False,
                        'totalDependencies': 42,
                        'created': '2019-07-01T13:06:01.994Z',
                        'issueCountsBySeverity': {
                            'high': 0,
                            'low': 0,
                            'medium': 0
                        },
                        'id': '3'
                    }
                ]
            }),
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
        self.projects = org.projects()

    def tearDown(self):
        httpretty.disable()

    def test_three_projects(self):
        assert len(self.projects) == 3

    def test_project_name(self):
        assert self.projects[0].name == 'owner/team-metadata-sync:Gopkg.lock'

    def test_project_id(self):
        assert self.projects[0].id == '1'
