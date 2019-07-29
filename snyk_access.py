import argparse
import json
import os
from typing import cast, Any, List, Union
import logging

from snyk import Snyk, Org, Project


logging.basicConfig(format='[%(asctime)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def find_org(snyk: Snyk, org_name: str) -> Org:
    orgs = snyk.orgs()
    return [o for o in orgs if o.name == org_name][0]


def repos_to_import(data: List[Any]) -> List[str]:
    snyk_repos: List[str] = []
    for obj in data:
        snyk: Union[List[str], bool] = obj.get('apps', {}).get('snyk', [])
        if type(snyk) is bool and snyk is True:
            snyk_repos += obj.get('repos', [])
        elif type(snyk) is not bool:
            snyk_repos += cast(List[str], snyk)
    return snyk_repos


def projects_to_delete(
    projects: List[Project],
    imported_repos: List[str],
) -> List[Project]:
    return [
        project for project in projects
        if (
            project.origin == 'github' and
            project.repo_name not in imported_repos
        )
    ]


def main(owner: str, org_name: str, filename: str) -> None:
    logger.info(
        f'Importing GitHub repos from {owner} into {org_name} org in Snyk'
    )
    snyk = Snyk(os.environ['SNYK_TOKEN'])

    org: Org = find_org(snyk, org_name)

    logger.info(f'Loading data from {filename}')
    with open(filename) as f:
        data = json.load(f)

    repos: List[str] = repos_to_import(data)

    for repo in repos:
        logger.info(f'Importing {repo}')
        org.import_github_project(owner, repo)

    to_delete = projects_to_delete(org.projects, repos)

    for project in to_delete:
        logger.info(f'Removing {project.name}')
        project.delete()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Import repos from GitHub into Snyk',
    )
    parser.add_argument('--owner', help='GitHub owner', required=True)
    parser.add_argument(
        '--org',
        help='Name of Snyk organisation to import into',
        required=True,
    )
    parser.add_argument(
        '--access-file',
        help='A JSON file containing config',
        required=True,
    )

    args = parser.parse_args()
    main(args.owner, args.org, args.access_file)
