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

import requests


GITHUB_API_URL = 'https://api.github.com'
ORG_NAME = 'ovirt'
HEADERS = {}
BOTS = ['Dependabot[Bot]', 'Github-Actions[Bot]']
REPO_LINK = f"{GITHUB_API_URL}/repos/{ORG_NAME}"
contributer_cache = {}


class GithubAPI:
    """
    Class containing interactions with the github api
    """
    def __init__(self, github_api_key):
        self.headers = {
            "Authorization": f"token {github_api_key}"
        }
        self.last_release = self.get_latest_release_date("ovirt-engine")

    def collect_contributors(self, repo, contributors):
        """
        Collect contributions from a specific repo since the last release date
        """
        params = f"per_page=100&since={self.last_release}"
        url = f"{REPO_LINK}/{repo}/commits?{params}"
        response = requests.get(url, headers=self.headers, timeout=60)
        # just return contributors if the repo is empty or doesn't exist
        if response.status_code != 200:
            return contributors
        data = response.json()
        for commit in data:
            if str(commit["commit"]["author"]["name"]).title() in BOTS:
                continue
            if contributors.get(self.get_author(commit), None) is not None:
                contributors[self.get_author(commit)] += f", {repo}"
            else:
                contributors.update({self.get_author(commit): f"{repo}"})
        return contributors

    def fetch_repositories(self):
        """"
        Fetch all non archived repositories in the ovirt organization
        """
        params = f"per_page=100&q=org:{ORG_NAME} archived:false"
        url = f"{GITHUB_API_URL}/search/repositories?{params}"

        response = requests.get(url, headers=self.headers, timeout=60)
        if response.status_code != 200:
            raise RuntimeError(
                f"Error fetching repositories: "
                f"{response.status_code} - {response.text}"
            )
        data = response.json().get('items', [])
        repo_names = [f"{x['name']}" for x in data]
        return repo_names

    @staticmethod
    def get_author(commit):
        """
        Get the author of a commit
        If the commit is made by an existing github user, link to their profile
        If not, link to their email
        """
        author_name = str(commit['commit']['author']['name']).title()
        if commit["author"] is not None:
            # cache name linked to github account, reduces duplicates in list
            github_url = commit['author']['html_url']
            if contributer_cache.get(github_url, None) is not None:
                github_account = commit['author']['html_url']
                contributor_name = contributer_cache[github_account]
                return f"[{contributor_name}]({commit['author']['html_url']})"
            else:
                contributer_cache[commit['author']['html_url']] = author_name
            return f"[{author_name}]({commit['author']['html_url']})"
        else:
            return f"[{author_name}]({commit['commit']['author']['email']})"

    def collect_latest_tag(self, repo):
        """
        Collect tags from repo and returns latest release tag
        """
        url = f"{REPO_LINK}/{repo}/tags"
        response = requests.get(url, headers=self.headers, timeout=60)
        if response.status_code != 200:
            return None
        data = response.json()
        if len(data) == 0:
            return None
        for tag in data:
            if str(tag['name']).startswith(repo):
                return tag

    def check_tag_against_date(self, repo):
        """
        Collect the latest tag and see if it is after the last engine release
        """
        latest_tag = self.collect_latest_tag(repo)
        if latest_tag is None:
            return None
        commit_url = latest_tag['commit']['url']
        response = requests.get(commit_url, headers=self.headers, timeout=60)
        if response.status_code != 200:
            print("failed fetch latest tag commit")
            return None
        data = response.json()
        commit_date = data["commit"]["committer"]["date"]
        if commit_date > self.last_release:
            return latest_tag
        return None

    def get_latest_release_date(self, repo):
        """
        Get the latest release date based on github tags
        """
        tag = self.collect_latest_tag(repo)
        if tag is None:
            # Returns a very old date, to prevent breaking API calls
            return "1970-01-01T00:00:00Z"
        url_commit = tag['commit']['url']
        response = requests.get(url_commit, headers=self.headers, timeout=60)
        if response.status_code != 200:
            return "1970-01-01T00:00:00Z"
        data = response.json()
        commit_date = data["commit"]["committer"]["date"]
        return commit_date
