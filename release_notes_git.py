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

    $ ./release_notes_github.py ovirt-3.6.5 [1] > notes.md

Where  'ovirt-3.6.5' is the current milestone and 1 is the RC number, if any.

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


from collections import OrderedDict
from ConfigParser import ConfigParser
from datetime import datetime

import bugzilla
import git
import jinja2

import requests


ORDINALS = {
    1: 'First',
    2: 'Second',
    3: 'Third',
    4: 'Fourth',
    5: 'Fifth',
    6: 'Sixth',
    7: 'Seventh',
    8: 'Eighth',
    9: 'Ninth',
    10: 'Tenth',
    # more than 10 RCs? lol
}


TEMPLATE = jinja2.Template(u'''\
---
title: oVirt {{ milestone }} Release Notes
category: documentation
---

# oVirt {{ milestone }} Release Notes

The oVirt Project is pleased to announce the availability of {{ milestone }}
{% if rc %}{{ rc }} Release Candidate{% else %}Release{% endif %} as
of {{ current_date }}.

oVirt is an open source alternative to VMware™ vSphere™, and provides an awesome
KVM management interface for multi-node virtualization.
This release is available now for Red Hat Enterprise Linux 7.2, CentOS Linux 7.2
(or similar).

{% if rc %}
This is pre-release software.
Please take a look at our [community page](/community/) to know how to
ask questions and interact with developers and users.
All issues or bugs should be reported via the [Red Hat Bugzilla](https://bugzilla.redhat.com/).
The oVirt Project makes no guarantees as to its suitability or usefulness.
This pre-release should not to be used in production, and it is not feature complete.
{% endif %}

To find out more about features which were added in previous oVirt releases,
check out the [previous versions release notes](/develop/release-management/releases/).
For a general overview of oVirt, read [the Quick Start Guide](Quick_Start_Guide)
and the [about oVirt](about oVirt) page.

An updated documentation has been provided by our downstream
[Red Hat Virtualization](https://access.redhat.com/documentation/en/red-hat-virtualization?version=4.0/)


## Install / Upgrade from previous versions

Users upgrading from 3.6 should be aware of following 4.0 changes around
authentication and certificates handling:

1. Single Sign-On using OAUTH2 protocol has been implemented in engine to
   allow SSO between webadmin, userportal and RESTAPI. More information can
   be found at https://bugzilla.redhat.com/1092744

2. Due to SSO it's required to access engine only using the same FQDN which
   was specified during engine-setup invocation. If your engine FQDN is not
   accessible from all engine clients, you will not be able to login. Please
   use ovirt-engine-rename tool to fix your FQDN, more information can be
   found at https://www.ovirt.org/documentation/how-to/networking/changing-engine-hostname/ .
   If you try to access engine using IP or DNS alias, an error will be
   thrown. Please consult following bugs targeted to oVirt 4.0.4 which
   should fix this limitation:
     https://bugzilla.redhat.com/1325746
     https://bugzilla.redhat.com/1362196

3. If you have used Kerberos SSO to access engine, please consult
   https://bugzilla.redhat.com/1342192 how to update your Apache
   configuration after upgrade to 4.0

4. If you are using HTTPS certificate signed by custom certificate
   authority, please take a look at https://bugzilla.redhat.com/1336838
   for steps which need to be done after migration to 4.0. Also please
   consult https://bugzilla.redhat.com/1313379 how to setup this custom
   CA for use with virt-viewer clients.


### Fedora / CentOS / RHEL

{% if rc %}
## RELEASE CANDIDATE

In order to install this Release Candidate you will need to enable pre-release repository.
{% endif %}

In order to install it on a clean system, you need to install

{% if rc %}
`# yum install `[`http://resources.ovirt.org/pub/yum-repo/ovirt-release40-pre.rpm`](http://resources.ovirt.org/pub/yum-repo/ovirt-release40-pre.rpm)
{% else %}
`# yum install `[`http://resources.ovirt.org/pub/yum-repo/ovirt-release40.rpm`](http://resources.ovirt.org/pub/yum-repo/ovirt-release40.rpm)
{% endif%}

{% if rc %}To test this pre release, you may read our
[Quick Start Guide](Quick Start Guide) or{% else %}and then follow our
[Quick Start Guide](Quick Start Guide) or{% endif %} a more updated documentation
from our downstream
[Red Hat Virtualization](https://access.redhat.com/documentation/en/red-hat-virtualization/4.0/)

{% if not rc %}
If you're upgrading from a previous release on Enterprise Linux 7 you just need
to execute:

      # yum install http://resources.ovirt.org/pub/yum-repo/ovirt-release40.rpm
      # yum update "ovirt-*-setup*"
      # engine-setup

Upgrade on Fedora 22 and Enterprise Linux 6 is not supported and you should
follow our [Migration Guide](../../documentation/migration-engine-36-to-40/) in
order to migrate to Enterprise Linux 7 or Fedora 23.
{% endif %}

### oVirt Hosted Engine

If you're going to install oVirt as Hosted Engine on a clean system please
follow [Hosted_Engine_Howto#Fresh_Install](Hosted_Engine_Howto#Fresh_Install)
guide or the corresponding Red Hat Virtualization
[Self Hosted Engine Guide](https://access.redhat.com/documentation/en/red-hat-virtualization/4.0/paged/self-hosted-engine-guide/)

If you're upgrading an existing Hosted Engine setup, please follow
[Hosted_Engine_Howto#Upgrade_Hosted_Engine](Hosted_Engine_Howto#Upgrade_Hosted_Engine)
guide or the corresponding Red Hat Virtualization
[Upgrade Guide](https://access.redhat.com/documentation/en/red-hat-virtualization/4.0/paged/upgrade-guide/)
''')


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

    def validate_bug(self, bug_id, target_milestones=None):
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
                target_milestones and
                bug.target_milestone not in target_milestones
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
                owner=self.GITHUB_REPO_OWNER,
                project=self.project,
                previous=r1,
                current=r2,
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


def generate_notes(milestone, rc=None):

    def sort_function(x, y):
        priorities = ['unspecified', 'low', 'medium', 'high', 'urgent']

        def get_priority_index(a):
            if a is None:
                return 0
            try:
                return priorities.index(a.strip().lower())
            except ValueError:
                return 0

        return (
            get_priority_index(y.get('priority')) -
            get_priority_index(x.get('priority'))
        )

    cp = ConfigParser()
    if not cp.read(['milestones/%s.conf' % milestone]):
        raise RuntimeError('Failed to read config file for milestone: %s' % (
            milestone,
        ))

    target_milestones = [milestone]
    if cp.has_section('default') and cp.get('default', 'target_milestones'):
        milestones = cp.get('default', 'target_milestones')
        if milestones:
            target_milestones = [i.strip() for i in milestones.split(',')]

    bz = Bugzilla()

    generated = OrderedDict()

    for project in cp.sections():
        if project == 'default':
            continue

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
            bug = bz.validate_bug(bug_id, target_milestones)
            bugs_found.append(bug_id)
            if bug:
                cf_doc_type = bug.cf_doc_type
                if 'docs needed' in cf_doc_type.lower():
                    cf_doc_type = 'Unclassified'
                doc_type = generated.setdefault(cf_doc_type, OrderedDict())
                proj = doc_type.setdefault(project_name or project, {})
                team = proj.setdefault(bug.cf_ovirt_team, [])
                team.append({
                    'id': bug_id,
                    'priority': bug.priority,
                    'summary': codecs.encode(
                        bug.summary, "utf-8", "xmlcharrefreplace"
                    ),
                })
                if cf_doc_type.lower() != 'bug fix':
                    team[-1]['release_notes'] = '<br>'.join(
                        codecs.encode(
                            bug.cf_release_notes,
                            'utf-8',
                            'xmlcharrefreplace'
                        ).splitlines()
                    )
                team.sort(sort_function)

        sys.stderr.write('\n')

    sys.stdout.write(TEMPLATE.render(
        rc=ORDINALS[rc] if rc else None,
        milestone=milestone.split('-')[-1],
        current_date=datetime.utcnow().strftime('%B %d, %Y')
    ))

    sys.stdout.write('## What\'s New in %s?\n\n' % milestone.split('-')[-1])

    bug_fixes = None
    bug_types = generated.keys()
    bug_types.sort()
    for bug_type in bug_types:
        if bug_type.lower() == 'bug fix':
            bug_fixes = generated[bug_type]
            continue
        sys.stdout.write('### %s\n\n' % bug_type)

        for project in generated[bug_type]:
            sys.stdout.write('#### %s\n\n' % project)
            teams = generated[bug_type][project].keys()
            teams.sort()
            for team in teams:
                sys.stdout.write('##### Team: %s\n\n' % team)

                for bug in generated[bug_type][project][team]:
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
        teams = bug_fixes[project].keys()
        teams.sort()
        for team in teams:
            sys.stdout.write('#### Team: %s\n\n' % team)

            for bug in bug_fixes[project][team]:
                sys.stdout.write(
                    ' - [BZ {id}](https://bugzilla.redhat.com/{id}) '
                    '<b>{summary}</b><br>\n'.format(**bug)
                )

            sys.stdout.write('\n')


def main(argv):
    if len(argv) < 1 or len(argv) > 2:
        sys.stderr.write(
            'You must provide target release and (optionally) the '
            'RC number as arguments.\n'
        )
        return 1
    rc = None
    try:
        rc = int(argv[1].strip())
    except IndexError:
        pass
    generate_notes(argv[0], rc)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
