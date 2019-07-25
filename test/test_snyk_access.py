import json
import unittest
from unittest.mock import MagicMock, patch, call, mock_open

import snyk
import snyk_access


class TestFindOrg(unittest.TestCase):

    def test_find_org(self):
        snyk_client = MagicMock(spec=snyk.Snyk)
        http_client = MagicMock(spec=snyk.HTTPClient)
        group = MagicMock(spec=snyk.Group)
        orgs = [
            snyk.Org(http_client, f'team-{i}', str(i), group)
            for i in range(10)
        ]
        org_name = 'myorg'
        orgs.append(snyk.Org(http_client, org_name, '42', group))
        snyk_client.orgs.return_value = orgs

        org = snyk_access.find_org(snyk_client, org_name)

        assert org.id == '42'


class TestFindRepos(unittest.TestCase):

    def test_snyk_app_in_one_block(self):
        data = [
            {
                'teams': {
                    'foo-team': 'pull',
                },
                'apps': {
                    'snyk': [
                        'project-a',
                        'project-b',
                    ],
                },
                'repos': [
                    'project-a',
                    'project-b',
                    'project-c',
                    'project-d',
                ],
            },
            {
                'teams': {
                    'bar-team': 'push',
                },
                'repos': [
                    'project-e',
                ],
            },
        ]

        repos = snyk_access.repos_to_import(data)

        assert sorted(repos) == ['project-a', 'project-b']

    def test_snyk_app_enabled_in_two_blocks(self):
        data = [
            {
                'teams': {
                    'foo-team': 'pull',
                },
                'apps': {
                    'snyk': True,
                },
                'repos': [
                    'project-a',
                    'project-b',
                    'project-c',
                    'project-d',
                ],
            },
            {
                'teams': {
                    'bar-team': 'push',
                },
                'apps': {
                    'snyk': True,
                },
                'repos': [
                    'project-e',
                ],
            },
        ]

        repos = snyk_access.repos_to_import(data)

        assert sorted(repos) == [
            'project-a',
            'project-b',
            'project-c',
            'project-d',
            'project-e',
        ]

    def test_snyk_app_in_two_blocks_enabled_and_listed(self):
        data = [
            {
                'teams': {
                    'foo-team': 'pull',
                },
                'apps': {
                    'snyk': [
                        'project-a',
                        'project-b',
                    ],
                },
                'repos': [
                    'project-a',
                    'project-b',
                    'project-c',
                    'project-d',
                ],
            },
            {
                'teams': {
                    'bar-team': 'push',
                },
                'apps': {
                    'snyk': True,
                },
                'repos': [
                    'project-e',
                ],
            },
        ]

        repos = snyk_access.repos_to_import(data)

        assert sorted(repos) == ['project-a', 'project-b', 'project-e']

    def test_snyk_app_in_two_blocks(self):
        data = [
            {
                'teams': {
                    'foo-team': 'pull',
                },
                'apps': {
                    'snyk': [
                        'project-a',
                        'project-b',
                    ],
                },
                'repos': [
                    'project-a',
                    'project-b',
                    'project-c',
                    'project-d',
                ],
            },
            {
                'teams': {
                    'bar-team': 'push',
                },
                'apps': {
                    'snyk': [
                        'project-e',
                    ],
                },
                'repos': [
                    'project-e',
                ],
            },
        ]

        repos = snyk_access.repos_to_import(data)

        assert sorted(repos) == ['project-a', 'project-b', 'project-e']


class TestSnykAccess(unittest.TestCase):

    @patch('snyk_access.Snyk')
    @patch.dict('snyk_access.os.environ', {'SNYK_TOKEN': 'token'})
    def test_project_import(self, Snyk):
        snyk_client = MagicMock(spec=snyk.Snyk)
        http_client = MagicMock(spec=snyk.HTTPClient)
        group = MagicMock(spec=snyk.Group)
        orgs = [
            snyk.Org(http_client, f'team-{i}', str(i), group)
            for i in range(10)
        ]
        org_name = 'myorg'
        org = MagicMock(spec=snyk.Org)
        org.client = http_client
        org.name = org_name
        org.id = '42'
        org.group = group
        orgs.append(org)
        snyk_client.orgs.return_value = orgs
        Snyk.return_value = snyk_client

        data = [
            {
                'teams': {
                    'foo-team': 'pull',
                },
                'apps': {
                    'snyk': [
                        'project-a',
                        'project-b',
                    ],
                },
                'repos': [
                    'project-a',
                    'project-b',
                    'project-c',
                    'project-d',
                ],
            },
            {
                'teams': {
                    'bar-team': 'push',
                },
                'repos': [
                    'project-e',
                ],
            },
        ]

        with patch(
            'snyk_access.open',
            mock_open(read_data=json.dumps(data)),
        ) as open_:

            snyk_access.main('owner', 'myorg', 'access.json')

            open_.assert_called_once_with('access.json')

            assert org.import_github_project.call_count == 2

            org.import_github_project.assert_has_calls([
                call('owner', 'project-a'),
                call('owner', 'project-b'),
            ])

    @patch('snyk_access.Snyk')
    @patch.dict('snyk_access.os.environ', {'SNYK_TOKEN': 'token'})
    def test_remove_projects_not_listed(self, Snyk):
        snyk_client = MagicMock(spec=snyk.Snyk)
        http_client = MagicMock(spec=snyk.HTTPClient)
        group = MagicMock(spec=snyk.Group)
        orgs = [
            snyk.Org(http_client, f'team-{i}', str(i), group)
            for i in range(10)
        ]
        org_name = 'myorg'
        org = MagicMock(spec=snyk.Org)
        org.client = http_client
        org.name = org_name
        org.id = '42'
        org.group = group
        org.projects.return_value = [
            snyk.Project(
                http_client,
                {
                    'id': '1',
                    'name': 'owner/project-c:requirements.txt',
                    'origin': 'github',
                },
                org,
            ),
            snyk.Project(
                http_client,
                {
                    'id': '2',
                    'name': 'owner/project-d:requirements.txt',
                    'origin': 'github',
                },
                org,
            ),
            snyk.Project(
                http_client,
                {
                    'id': '3',
                    'name': 'project-x',
                    'origin': 'cli',
                },
                org,
            ),
        ]
        orgs.append(org)
        snyk_client.orgs.return_value = orgs
        Snyk.return_value = snyk_client

        data = [
            {
                'teams': {
                    'foo-team': 'pull',
                },
                'apps': {
                    'snyk': [
                        'project-a',
                        'project-b',
                    ],
                },
                'repos': [
                    'project-a',
                    'project-b',
                    'project-c',
                    'project-d',
                ],
            },
            {
                'teams': {
                    'bar-team': 'push',
                },
                'repos': [
                    'project-e',
                ],
            },
        ]

        with patch('snyk_access.open', mock_open(read_data=json.dumps(data))):

            snyk_access.main('owner', 'myorg', 'access.json')

            assert http_client.delete.call_count == 2

            http_client.delete.assert_has_calls([
                call('org/42/project/1'),
                call('org/42/project/2'),
            ])
