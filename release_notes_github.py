#!/usr/bin/python
# coding: utf-8

# Copyright the oVirt Authors
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import argparse
import os
import sys
from datetime import datetime

import jinja2
from dotenv import load_dotenv

from github_api import GithubAPI

TEMPLATE_FILE = "release_notes.template"
ORG_LINK = "https://github.com/oVirt/"


def generate_template(target_release, authors, release_type):
    """
    Generate the template part of the release notes
    """
    template_loader = jinja2.FileSystemLoader(searchpath="./")
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template(TEMPLATE_FILE)
    sys.stdout.write(
        template.render(
            milestone=target_release,
            current_date=datetime.now().strftime("%B %d %Y"),
            authors="\n  - ".join(sorted(authors)),
            release_type=release_type,
        )
    )


def generate_contributors_section(git_api, include_projects, repos):
    """
    Generate the contributors section after the template
    """
    sys.stdout.write("### Contributors\n\n")
    contributors = {}
    for repo in repos:
        contributors = git_api.collect_contributors(repo, contributors)
    contributors = dict(sorted(contributors.items()))
    sys.stdout.write(
        f"{len(contributors)} people contributed to this release:\n\n"
    )
    for contributor, repo in contributors.items():
        if include_projects:
            sys.stdout.write(f"* {contributor} (Contributed to: {repo})\n")
        else:
            sys.stdout.write(f"* {contributor}\n")
    sys.stdout.write("\n")


def generate_new_releases_section(git_api, repos):
    """
    Generate the new releases section after the template
    """
    sys.stdout.write("### New Releases\n\n")
    new_tags = {
        repo: git_api.check_tag_against_date(repo)
        for repo in repos
        if git_api.check_tag_against_date(repo) is not None
    }
    if new_tags:
        for repo, tag in new_tags.items():
            github_link = f"{ORG_LINK}/{repo}/releases/tag/{tag['name']}"
            sys.stdout.write(f"* [{tag['name']}]({github_link})\n")
    else:
        sys.stdout.write("No new packages released")
    sys.stdout.write("\n\n")


def main():
    """
    Main function to parse arguments and generate the full release notes
    """
    parser = argparse.ArgumentParser(
        description='Generate release notes from template'
    )
    parser.add_argument('target_release', metavar='TARGET-RELEASE',
                        help='target release. e.g. 4.2.0')
    parser.add_argument('--contrib-project-list', action='store_true',
                        help='if included, list projects '
                             'each author contributed to')
    # Important: these need to be part of the authors list on ovirt-site
    parser.add_argument('--release-author', type=str,
                        help='add the specified (comma separated) author(s) '
                             'id(s) to the \'authors:\' tag of the notes')
    parser.add_argument('--release-type', type=str,
                        help='release type: alpha, beta, rc, empty if GA')
    args = parser.parse_args()
    load_dotenv()
    author_list = args.release_author.split(",") if args.release_author else []
    github_api_key = os.getenv("GITHUB-API-KEY")
    git_api = GithubAPI(github_api_key)
    repos = git_api.fetch_repositories()
    generate_template(args.target_release, author_list, args.release_type)
    generate_new_releases_section(git_api, repos)
    generate_contributors_section(git_api, args.contrib_project_list, repos)


if __name__ == "__main__":
    main()
