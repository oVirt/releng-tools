#!/usr/bin/env python
# coding: utf-8

# Copyright (C) 2016 Red Hat, Inc.
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

"""
This script generates release notes for oVirt projects, fetching commits from
Github.

To run it:

    $ ./release_notes_github.py ovirt-3.6.5 > notes.md

Where  'ovirt-3.6.5' is the current milestone.

WARNING: when running this, if user gets '403 Forbidden' errors from
Github API, it is due to API rate limiting. To work around this, just
go to https://github.com/settings/tokens and create a new token (no need
to select any scope), and export it as an environment variable:

    $ export GITHUB_OAUTH_TOKEN="your token here"

"""

import atexit
import codecs
import os
import re
import shutil
import sys
import tempfile

import bugzilla
import git
import requests

from collections import OrderedDict
from ConfigParser import ConfigParser


class Bugzilla(object):

    BUGZILLA_API_URL = 'https://bugzilla.redhat.com/xmlrpc.cgi'

    re_bug_id = re.compile(
        r'bug-url: +http.+/(show_bug\.cgi\?id=)?(?P<bug_id>[0-9]+) *',
        re.IGNORECASE
    )

    def __init__(self):
        self.bz = bugzilla.RHBugzilla(url=self.BUGZILLA_API_URL)

    def get_bug(self, bug_id):
        q = self.bz.build_query(bug_id=str(bug_id))
        r = self.bz.query(q)
        if r:
            return r[0]

    def get_bug_id_from_message(self, message):
        m = self.re_bug_id.search(message)
        if m:
            return int(m.group('bug_id'))

    def validate_bug(self, bug_id, target_milestone=None):
        bug = self.get_bug(bug_id)
        if not bug:
            sys.stderr.write("%d - invalid bug\n" % bug_id)
            return None

        if (
            bug.product in (
                'Red Hat Enterprise Virtualization Manager',
                'oVirt',
                'Red Hat Storage',
                'Red Hat Gluster Storage',
            )
        ) or (
            bug.classification == 'oVirt'
        ):
            if bug.status not in (
                'MODIFIED',
                'ON_QA',
                'VERIFIED',
                'RELEASE_PENDING',
                'CLOSED',
            ):
                sys.stderr.write(
                    (
                        '{bug} - is in status {status} and targeted '
                        'to {milestone}; '
                        'assignee: {assignee}\n'
                    ).format(
                        bug=bug_id,
                        status=bug.status,
                        milestone=bug.target_milestone,
                        assignee=codecs.encode(
                            bug.assigned_to, 'utf-8', 'xmlcharrefreplace'
                        )
                    )
                )
                return None

            elif (
                target_milestone is not None and
                bug.target_milestone != target_milestone
            ):
                sys.stderr.write(
                    '%d - is targeted to %s; assignee: %s\n' % (
                        bug_id,
                        bug.target_milestone,
                        codecs.encode(
                            bug.assigned_to, 'utf-8', 'xmlcharrefreplace'
                        )
                    )
                )
                return None
        else:
            sys.stderr.write(
                '%d - has product %s\n' % (bug_id, bug.product)
            )
            return None

        return bug


class GitHubProject(object):

    GITHUB_API_URL = 'https://api.github.com'
    GITHUB_REPO_OWNER = 'oVirt'

    def __init__(self, project):
        self.project = project

        self.session = requests.Session()
        self.session.headers['Accept'] = 'application/json'

        oauth_token = os.environ.get('GITHUB_OAUTH_TOKEN')
        if oauth_token is not None:
            self.session.headers['Authorization'] = 'token %s' % oauth_token

    def _do_request(self, endpoint):
        r = self.session.get(self.GITHUB_API_URL + endpoint)
        r.raise_for_status()
        return r.json()

    def get_commits_between_revs(self, r1, r2):
        r = self._do_request(
            '/repos/{owner}/{project}/compare/{previous}...{current}'.format(
                owner = self.GITHUB_REPO_OWNER,
                project = self.project,
                previous = r1,
                current = r2,
            )
        )
        commits = r.get('commits', [])
        rv = []
        for commit in commits:
            rv.append({
                'sha': commit.get('sha'),
                'message': commit.get('commit', {}).get('message'),
            })
        return rv


class GerritGitProject(object):

    GERRIT_GIT_BASE_URL = 'https://gerrit.ovirt.org/'

    def __init__(self, project):
        # this creates a brand new bare repository for the sake of
        # consistency
        self.repo_url = self.GERRIT_GIT_BASE_URL + project
        self.repo_path = tempfile.mkdtemp(prefix='release-notes-')
        atexit.register(shutil.rmtree, self.repo_path)
        git.Repo.clone_from(self.repo_url, self.repo_path, bare=True)
        self.repo = git.Git(self.repo_path)

    def get_commits_between_revs(self, r1, r2):
        log = self.repo.log('%s..%s' % (r1, r2))
        current = None
        rv = []
        for line in log.splitlines():
            if line.startswith('commit '):
                if current is not None:
                    current.setdefault('message', '')
                    rv.append(current)
                current = {
                    'sha': line[7:].strip(),
                }
            elif line.strip().lower().startswith('bug-url'):
                current['message'] = line.strip()

        if current is not None:
            current.setdefault('message', '')
            rv.append(current)

        return rv


def generate_notes(milestone):

    cp = ConfigParser()
    if not cp.read(['milestones/%s.conf' % milestone]):
        raise RuntimeError('Failed to read config file for milestone: %s' % (
            milestone,
        ))

    bz = Bugzilla()

    generated = OrderedDict()

    for project in cp.sections():
        sys.stderr.write('Project: %s\n\n' % (project,))

        gh = GerritGitProject(project)
        previous = cp.get(project, 'previous')
        current = cp.get(project, 'current')
        project_name = cp.get(project, 'name')

        if not previous or not current:
            raise RuntimeError(
                'Every project must provide previous and current revisions')

        commits = gh.get_commits_between_revs(previous, current)

        bugs_found = []

        for commit in commits:
            bug_id = bz.get_bug_id_from_message(commit['message'])
            if bug_id is None:
                sys.stderr.write('Ignoring commit %s; no bug url found\n' % (
                    commit['sha'],
                ))
                continue
            if bug_id in bugs_found:
                sys.stderr.write('Ignoring repeated bug; bug #%d\n' % (
                    bug_id,
                ))
                continue
            sys.stderr.write('Fetching commit %s; bug #%d\n' % (
                commit['sha'],
                bug_id,
            ))
            bug = bz.validate_bug(bug_id, milestone)
            bugs_found.append(bug_id)
            if bug:
                doc_type = generated.setdefault(bug.cf_doc_type, OrderedDict())
                proj = doc_type.setdefault(project_name or project, [])
                proj.append({
                    'id': bug_id,
                    'summary': codecs.encode(
                        bug.summary, "utf-8", "xmlcharrefreplace"
                    ),
                })
                if bug.cf_doc_type.lower() != 'bug fix':
                    proj[-1]['release_notes'] = '<br>'.join(
                        codecs.encode(
                            bug.cf_release_notes,
                            'utf-8',
                            'xmlcharrefreplace'
                        ).splitlines()
                    )
                proj.sort(lambda x, y: x['id'] - y['id'])

        sys.stderr.write('\n')

    sys.stdout.write('## What\'s New in %s?\n\n' % milestone.split('-')[-1])

    bug_fixes = None

    for bug_type in generated:
        if bug_type.lower() == 'bug fix':
            bug_fixes = generated[bug_type]
            continue
        sys.stdout.write('### %s\n\n' % bug_type)

        for project in generated[bug_type]:
            sys.stdout.write('#### %s\n\n' % project)

            for bug in generated[bug_type][project]:
                sys.stdout.write(
                    ' - [BZ {id}](https://bugzilla.redhat.com/{id}) '
                    '<b>{summary}</b><br>{release_notes}\n'.format(**bug)
                )

            sys.stdout.write('\n')

    if not bug_fixes:
        return

    sys.stdout.write('## Bug fixes\n\n')

    for project in bug_fixes:
        sys.stdout.write('### %s\n\n' % project)

        for bug in bug_fixes[project]:
            sys.stdout.write(
                ' - [BZ {id}](https://bugzilla.redhat.com/{id}) '
                '<b>{summary}</b><br>\n'.format(**bug)
            )

        sys.stdout.write('\n')


def main(argv):
    if len(argv) != 1:
        sys.stderr.write('You must provide target release as argument.\n')
        return 1
    generate_notes(argv[0])
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
