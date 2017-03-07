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
Gerrit.

For details on how to run the script, run:

    $ ./release_notes_git.py --help
"""

BUGZILLA_SERVER = 'bugzilla.redhat.com'
BUGZILLA_HOME = 'https://%s/' % BUGZILLA_SERVER

import argparse
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

oVirt is an open source alternative to VMware™ vSphere™, and provides an
awesome KVM management interface for multi-node virtualization.
This release is available now for Red Hat Enterprise Linux 7.3,
CentOS Linux 7.3 (or similar).

{% if rc %}
This is pre-release software.
Please take a look at our [community page](/community/) to know how to
ask questions and interact with developers and users.
All issues or bugs should be reported via the
[Red Hat Bugzilla](https://bugzilla.redhat.com/enter_bug.cgi?classification=oVirt).
The oVirt Project makes no guarantees as to its suitability or usefulness.
This pre-release should not to be used in production, and it is not feature
complete.
{% endif %}

To find out more about features which were added in previous oVirt releases,
check out the
[previous versions release notes](/develop/release-management/releases/).
For a general overview of oVirt, read
[the Quick Start Guide](Quick_Start_Guide)
and the [about oVirt](about oVirt) page.

[Installation guide](http://www.ovirt.org/documentation/install-guide/Installation_Guide/)
is available for updated and detailed installation instructions.

### Fedora / CentOS / RHEL

{% if rc %}
## RELEASE CANDIDATE

In order to install this Release Candidate you will need to enable pre-release repository.
{% endif %}

In order to install it on a clean system, you need to install

{% if rc %}
`# yum install `[`http://resources.ovirt.org/pub/yum-repo/ovirt-release41-pre.rpm`](http://resources.ovirt.org/pub/yum-repo/ovirt-release41-pre.rpm)
{% else %}
`# yum install `[`http://resources.ovirt.org/pub/yum-repo/ovirt-release41.rpm`](http://resources.ovirt.org/pub/yum-repo/ovirt-release41.rpm)
{% endif%}

and then follow our
[Installation guide](http://www.ovirt.org/documentation/install-guide/Installation_Guide/)

{% if not rc %}
If you're upgrading from a previous release on Enterprise Linux 7 you just need
to execute:

      # yum install http://resources.ovirt.org/pub/yum-repo/ovirt-release41.rpm
      # yum update "ovirt-*-setup*"
      # engine-setup

{% endif %}

### oVirt Hosted Engine

If you're going to install oVirt as Hosted Engine on a clean system please
follow [Hosted_Engine_Howto#Fresh_Install](Hosted_Engine_Howto#Fresh_Install)
guide or the corresponding section in
[Self Hosted Engine Guide](/documentation/self-hosted/Self-Hosted_Engine_Guide/)

If you're upgrading an existing Hosted Engine setup, please follow
[Hosted_Engine_Howto#Upgrade_Hosted_Engine](Hosted_Engine_Howto#Upgrade_Hosted_Engine)
guide or the corresponding section within the
[Upgrade Guide](/documentation/upgrade-guide/upgrade-guide/)

### EPEL

TL;DR Don't enable all of EPEL on oVirt machines.

The ovirt-release package enables the epel repositories and includes several
specific packages that are required from there. It also enables and uses
the CentOS OpsTools SIG repos, for other packages.

EPEL currently includes collectd 5.7.1, and the collectd package there includes
the write_http plugin.

OpsTools currently includes collectd 5.7.0, and the write_http plugin is
packaged separately.

ovirt-release does not use collectd from epel, so if you only use it, you
should be ok.

If you want to use other packages from EPEL, you should make sure to not
include collectd. Either use `includepkgs` and add those you need, or use
`excludepkgs=collectd*`.

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


class GerritGitProject(object):

    GERRIT_GIT_BASE_URL = 'https://gerrit.ovirt.org/'

    def __init__(self, project, basedir=None):
        self.repo_url = self.GERRIT_GIT_BASE_URL + project

        if basedir is not None:
            self.repo_path = os.path.join(basedir, '%s.git' % project)
        else:
            self.repo_path = tempfile.mkdtemp(prefix='release-notes-')
            atexit.register(shutil.rmtree, self.repo_path)

        # this tests if the repo was actually cloned
        if os.path.isdir(os.path.join(self.repo_path, 'objects')):
            self.repo = git.Git(self.repo_path)
            self.repo.fetch('-p')
        else:
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


def generate_notes(milestone, rc=None, git_basedir=None):

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
    bug_list = []

    for project in cp.sections():
        if project == 'default':
            continue

        sys.stderr.write('Project: %s\n\n' % (project,))

        gh = GerritGitProject(project, git_basedir)
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
                proj = doc_type.setdefault(project_name or project, [])
                proj.append({
                    'id': bug_id,
                    'priority': bug.priority,
                    'summary': codecs.encode(
                        bug.summary, "utf-8", "xmlcharrefreplace"
                    ),
                })
                if cf_doc_type.lower() == 'no doc update':
                    proj[-1]['release_notes'] = ''
                elif cf_doc_type.lower() != 'bug fix':
                    proj[-1]['release_notes'] = '<br>'.join(
                        codecs.encode(
                            bug.cf_release_notes,
                            'utf-8',
                            'xmlcharrefreplace'
                        ).splitlines()
                    )
                proj.sort(sort_function)

        sys.stderr.write('\n')

    sys.stdout.write(
        codecs.encode(
            TEMPLATE.render(
                rc=ORDINALS[rc] if rc else None,
                milestone=milestone.split('-')[-1],
                current_date=datetime.utcnow().strftime('%B %d, %Y')
            ),
            'utf-8',
            'xmlcharrefreplace'
        )
    )

    sys.stdout.write(
        '\n\n## What\'s New in %s?\n\n' % milestone.split('-')[-1]
    )

    bug_fixes = None
    bug_types = generated.keys()
    bug_types.sort()
    for bug_type in bug_types:
        if bug_type.lower() == 'bug fix':
            bug_fixes = generated[bug_type]
            continue
        sys.stdout.write(
            '### %s\n\n' % bug_type.replace("Enhancement", "Enhancements")
        )

        for project in generated[bug_type]:
            sys.stdout.write('#### %s\n\n' % project)
            for bug in generated[bug_type][project]:
                sys.stdout.write(
                    ' - [BZ {id}](https://bugzilla.redhat.com/{id}) '
                    '<b>{summary}</b><br>{release_notes}\n'.format(**bug)
                )
                bug_list.append(bug)

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
            bug_list.append(bug)

        sys.stdout.write('\n')
    list_url = "%sbuglist.cgi?action=wrap&bug_id=" % BUGZILLA_HOME
    for bug in set(bug['id'] for bug in bug_list):
        list_url += "{id}%2C%20".format(id=bug)
    sys.stderr.write('\n\n\n'+list_url+'\n')


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--rc', type=int,
                        help='RC number of the release, if any')
    parser.add_argument('--git-basedir', metavar='DIR',
                        help=(
                            'base directory to store git repositories. will '
                            'use temp dirs by default'
                        ))
    parser.add_argument('target_release', metavar='TARGET-RELEASE',
                        help='target release. e.g. ovirt-3.6.5')

    args = parser.parse_args()

    generate_notes(args.target_release, args.rc, args.git_basedir)

    return 0


if __name__ == '__main__':
    sys.exit(main())
