#!/usr/bin/env python
# coding: utf-8

# Copyright (C) 2016-2018 Red Hat, Inc.
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

import argparse
import atexit
import codecs
import os
import re
import shutil
import sys
import tempfile
import time


from collections import OrderedDict
from ConfigParser import ConfigParser
from datetime import datetime

import bugzilla
import git
import jinja2


BUGZILLA_SERVER = 'bugzilla.redhat.com'
BUGZILLA_HOME = 'https://%s/' % BUGZILLA_SERVER

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
layout: toc
---

# oVirt {{ milestone }} Release Notes

The oVirt Project is pleased to announce the availability of the {{ milestone }} \
{% if release_type == "rc" %}{{ release }} Release Candidate\
{% elif release_type == "alpha" %}{{ release }} Alpha release\
{% elif release_type == "beta" %}{{ release }} Beta release\
{% else %}release{% endif %} as of {{ current_date }}.

oVirt is an open source alternative to VMware™ vSphere™, providing an
awesome KVM management interface for multi-node virtualization.
This release is available now for Red Hat Enterprise Linux 7.5,
CentOS Linux 7.5 (or similar).

{% if release_type %}
To find out how to interact with oVirt developers and users and ask questions,
visit our [community page]"(/community/).
All issues or bugs should be reported via
[Red Hat Bugzilla](https://bugzilla.redhat.com/enter_bug.cgi?classification=oVirt).
The oVirt Project makes no guarantees as to its suitability or usefulness.
This pre-release should not to be used in production, and it is not feature
complete.
{% endif %}

For a general overview of oVirt, read the [Quick Start Guide](/documentation/quickstart/quickstart-guide/)
and visit the [About oVirt](/documentation/introduction/about-ovirt/) page.

For detailed installation instructions, read the [Installation Guide](/documentation/install-guide/Installation_Guide/).

To learn about features introduced before {{ milestone }}, see the [release notes for previous versions](/documentation/#previous-release-notes).


## Install / Upgrade from previous versions

### CentOS / RHEL

{% if release_type == "rc" %}
## RELEASE CANDIDATE

In order to install this Release Candidate you will need to enable pre-release repository.
{% endif %}
{% if release_type == "alpha" %}
## ALPHA RELEASE

In order to install this Alplha Release you will need to enable pre-release repository.
{% endif %}
{% if release_type == "beta" %}
## BETA RELEASE

In order to install this Beta Release you will need to enable pre-release repository.
{% endif %}

In order to install it on a clean system, you need to install

{% if release_type %}
`# yum install `[`http://resources.ovirt.org/pub/yum-repo/ovirt-release{{ release_rpm  }}-pre.rpm`](http://resources.ovirt.org/pub/yum-repo/ovirt-release{{ release_rpm  }}-pre.rpm)
{% else %}
`# yum install `[`http://resources.ovirt.org/pub/yum-repo/ovirt-release{{ release_rpm  }}.rpm`](http://resources.ovirt.org/pub/yum-repo/ovirt-release{{ release_rpm  }}.rpm)
{% endif%}

and then follow our
[Installation Guide](http://www.ovirt.org/documentation/install-guide/Installation_Guide/).

{% if not release_type %}
If you're upgrading from a previous release on Enterprise Linux 7 you just need
to execute:

      # yum install http://resources.ovirt.org/pub/yum-repo/ovirt-release{{ release_rpm  }}.rpm
      # yum update "ovirt-*-setup*"
      # engine-setup

{% endif %}

### No Fedora support

Regretfully, Fedora is not supported anymore, and RPMs for it are not provided.
These are still built for the master branch, so users that want to test them,
can use the [nightly snapshot](/develop/dev-process/install-nightly-snapshot/).
At this point, we only try to fix problems specific to Fedora if they affect
developers. For some of the work to be done to restore support for Fedora, see
also tracker [bug 1460625](https://bugzilla.redhat.com/showdependencytree.cgi?id=1460625&hide_resolved=0).

### oVirt Hosted Engine

If you're going to install oVirt as a Hosted Engine on a clean system please
follow [Hosted_Engine_Howto#Fresh_Install](/documentation/how-to/hosted-engine/#fresh-install)
guide or the corresponding section in
[Self Hosted Engine Guide](/documentation/self-hosted/Self-Hosted_Engine_Guide/).

If you're upgrading an existing Hosted Engine setup, please follow
[Hosted_Engine_Howto#Upgrade_Hosted_Engine](/documentation/how-to/hosted-engine/#upgrade-hosted-engine)
guide or the corresponding section within the
[Upgrade Guide](/documentation/upgrade-guide/upgrade-guide/).

### EPEL

Don't enable all of EPEL on oVirt machines.

The ovirt-release package enables the EPEL repositories and includes several
specific packages that are required from there. It also enables and uses
the CentOS SIG repos, for other packages.

If you want to use other packages from EPEL, you should make sure to
use `includepkgs` and add only those you need avoiding to override
packages from other repos.
''')


class Bugzilla(object):

    BUGZILLA_API_URL = 'https://bugzilla.redhat.com/xmlrpc.cgi'

    re_bug_id = re.compile(
        r'bug-url: +http.+/(show_bug\.cgi\?id=)?(?P<bug_id>[0-9]+) *',
        re.IGNORECASE
    )

    def __init__(self):
        self.bz = bugzilla.RHBugzilla(
            url=self.BUGZILLA_API_URL,
            cookiefile=None,
            tokenfile=None,
            use_creds=False,
        )

    def get_bug(self, bug_id):
        q = self.bz.build_query(bug_id=str(bug_id))
        retry = 5
        while retry > 0:
            try:
                r = self.bz.query(q)
                retry = 0
            except IOError:
                sys.stderr.write("Error fetching bug, retrying")
                time.sleep(1)
                retry -= 1
        if r:
            return r[0]

    def get_bugs_in_milestone(self, milestone):
        q = self.bz.build_query(target_milestone=str(milestone))
        retry = 5
        r = None
        while retry > 0:
            try:
                r = self.bz.query(q)
                retry = 0
            except IOError:
                sys.stderr.write(
                    "Error fetching milestone {milestone}, retrying\n".format(
                        milestone=milestone,
                    )
                )
                time.sleep(5)
                retry -= 1
        if r:
            return r

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
                        '{bugzilla}{bug} - is in status {status} and targeted '
                        'to {milestone}; '
                        'assignee: {assignee}\n'
                    ).format(
                        bugzilla=BUGZILLA_HOME,
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
                bug.target_milestone not in target_milestones and (
                    (
                        bug.product in (
                            'Red Hat Enterprise Virtualization Manager',
                            'oVirt',
                        )
                    ) or (bug.classification == 'oVirt')
                )
            ):
                if not (
                    bug.status == 'CLOSED' and
                    bug.resolution in (
                        'CURRENTRELEASE',
                        'ERRATA',
                    )
                ):
                    sys.stderr.write(
                        '%s%d - is targeted to %s; assignee: %s\n' % (
                            BUGZILLA_HOME,
                            bug_id,
                            bug.target_milestone,
                            codecs.encode(
                                bug.assigned_to, 'utf-8', 'xmlcharrefreplace'
                            )
                        )
                    )
                    # Not returning None because it could have been cloned
                # May have been cloned to zstream.
                for blocked in bug.blocks:
                    sys.stderr.write(
                        'checking if %s%d has been cloned to %s%d\n' % (
                            BUGZILLA_HOME,
                            bug_id,
                            BUGZILLA_HOME,
                            blocked,
                        )
                    )
                    blocked_bug = self.validate_bug(blocked, target_milestones)
                    if (
                        blocked_bug and
                        bug.summary in blocked_bug.summary and
                        'ZStream' in blocked_bug.keywords and
                        blocked_bug.target_milestone in target_milestones
                    ):
                        sys.stderr.write(
                            '%d - has been cloned to %s;\n' % (
                                bug_id,
                                blocked_bug.id,
                            )
                        )
                        return blocked_bug
                return None
        else:
            sys.stderr.write(
                '%s%d - has product %s\n' % (
                    BUGZILLA_HOME,
                    bug_id,
                    bug.product
                )
            )
            return None

        return bug


class GerritGitProject(object):

    GERRIT_GIT_BASE_URL = 'https://gerrit.ovirt.org/'

    def __init__(self, project, basedir=None, base_url=GERRIT_GIT_BASE_URL):
        self.repo_url = base_url + project

        if basedir is not None:
            self.repo_path = os.path.join(basedir, '%s.git' % project)
        else:
            self.repo_path = os.path.join(
                tempfile.mkdtemp(prefix='release-notes-'),
                '%s.git' % project
            )
            atexit.register(shutil.rmtree, self.repo_path)

        # this tests if the repo was actually cloned
        if os.path.isdir(self.repo_path):
            self.repo = git.Git(self.repo_path)
            retry = 10
            while retry > 0:
                try:
                    sys.stderr.write("Updating %s\n" % self.repo_path)
                    self.repo.fetch('-p')
                    self.repo.fetch('-t')
                    self.repo.pull()
                    retry = 0
                except git.exc.GitCommandError as e:
                    sys.stderr.write("Error updating repo, retrying\n")
                    time.sleep(1)
                    retry -= 1
        else:
            retry = 10
            while retry > 0:
                try:
                    sys.stderr.write("Cloning %s\n" % self.repo_url)
                    git.Repo.clone_from(self.repo_url, self.repo_path)
                    retry = 0
                except git.exc.GitCommandError as e:
                    sys.stderr.write("Error cloning repo, retrying\n")
                    time.sleep(1)
                    retry -= 1
        self.repo = git.Git(self.repo_path)

    def get_commits_between_revs(self, r1, r2):
        if not r1:
            log = self.repo.log('%s' % (r2,))
        else:
            log = self.repo.log('%s..%s' % (r1, r2))
        current = None
        rv = []
        for line in log.splitlines():
            if line.startswith('commit '):
                if current is not None:
                    current.setdefault('message', [])
                    rv.append(current)
                current = {
                    'sha': line[7:].strip(),
                }
            elif line.strip().lower().startswith('bug-url'):
                current.setdefault('message', [])
                current['message'].append(line.strip())

        if current is not None:
            current.setdefault('message', '')
            rv.append(current)

        return rv


def search_for_missing_builds(target_milestones, bugs_listed_in_git_logs):
    sys.stderr.write("\n\n\n------------ REPORTS ------------\n\n\n")
    bz = Bugzilla()
    targeted_bugs = set()
    bug_list = []
    for milestone in target_milestones:
        bug_list += bz.get_bugs_in_milestone(milestone)
    targeted_bugs |= set(
        bug.id for bug in bug_list
        if not (bug.status == 'CLOSED' and bug.resolution == 'DUPLICATE')
    )
    not_referenced = targeted_bugs ^ bugs_listed_in_git_logs
    still_open = set(
        bug.id for bug in bug_list
        if bug.status in ('NEW', 'ASSIGNED', 'POST')
    )

    downstream_rebase = set(
        bug.id for bug in bug_list
        if (
            (bug.id in (not_referenced - still_open)) and
            (bug.product == 'Red Hat Enterprise Virtualization Manager') and
            (bug.cf_doc_type.lower().find('rebase') != -1)
        )
    )

    trackers = set(
        bug.id for bug in bug_list
        if (
            (bug.id in (not_referenced - still_open - downstream_rebase)) and
            ('Tracking' in bug.keywords)
        )
    )

    test_only = set(
        bug.id for bug in bug_list
        if (
            (bug.id in (not_referenced - still_open - downstream_rebase)) and
            ('TestOnly' in bug.keywords)
        )
    )

    downstream_only = set(
        bug.id for bug in bug_list
        if (
            (bug.id in (not_referenced - still_open)) and
            (bug.product == 'Red Hat Enterprise Virtualization Manager') and
            (bug.component in (
                'Documentation',
                'rhv-log-collector-analyzer',
                'rhevm-setup-plugins',
                'rhvm-setup-plugins',
                'rhevm-dependencies',
                'rhvm-dependencies',
                'rhevm-appliance',
                'rhvm-appliance',
                'rhev-guest-tools',
                'ansible',
                'cockpit',
                'rhvm-branding-rhv',
                )
            )
        )
    )

    sys.stderr.write('\nBugs not yet fixed for this release:\n')
    list_url = "%sbuglist.cgi?action=wrap&bug_id=" % BUGZILLA_HOME
    for bug in still_open:
        list_url += "{id}%2C%20".format(id=bug)
    sys.stderr.write(list_url+'\n')

    sys.stderr.write('\nDownstream rebase bugs:\n')
    list_url = "%sbuglist.cgi?action=wrap&bug_id=" % BUGZILLA_HOME
    for bug in downstream_rebase:
        list_url += "{id}%2C%20".format(id=bug)
    sys.stderr.write(list_url+'\n')


    sys.stderr.write('\nDownstream only bugs:\n')
    list_url = "%sbuglist.cgi?action=wrap&bug_id=" % BUGZILLA_HOME
    for bug in downstream_only:
        list_url += "{id}%2C%20".format(id=bug)
    sys.stderr.write(list_url+'\n')


    sys.stderr.write('\nTracker bugs:\n')
    list_url = "%sbuglist.cgi?action=wrap&bug_id=" % BUGZILLA_HOME
    for bug in trackers:
        list_url += "{id}%2C%20".format(id=bug)
    sys.stderr.write(list_url+'\n')

    sys.stderr.write('\nTest Only bugs:\n')
    list_url = "%sbuglist.cgi?action=wrap&bug_id=" % BUGZILLA_HOME
    for bug in test_only:
        list_url += "{id}%2C%20".format(id=bug)
    sys.stderr.write(list_url+'\n')

    sys.stderr.write('\nBugs not referenced but targeted for this release:\n')
    list_url = "%sbuglist.cgi?action=wrap&bug_id=" % BUGZILLA_HOME
    for bug in (
        not_referenced - still_open - downstream_rebase - trackers - downstream_only - test_only
    ):
        list_url += "{id}%2C%20".format(id=bug)
    sys.stderr.write(list_url+'\n')



def generate_notes(milestone, rc=None, git_basedir=None, release_type=None):

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

    def section_sort_function(x, y):
        # From lowest to highest priority
        sections = [
            "No Doc Update",
            "Unclassified",
            "Bug Fix",
            "Rebase: Bug Fixes Only",
            "Known Issue",
            "Deprecated Functionality",
            "Removed functionality",
            "Technology Preview",
            "Rebase: Bug Fixes and Enhancements",
            "Rebase: Enhancements Only",
            "Enhancement",
            "Release Note",
        ]

        def get_section_index(a):
            if a is None:
                return 0
            try:
                return sections.index(a.strip())
            except ValueError:
                sys.stderr.write("%s is not a known doc_type\n" % a)
                return 0

        return (get_section_index(y) - get_section_index(x))

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
        if cp.has_option(project, 'baseurl'):
            gh = GerritGitProject(
                project,
                git_basedir,
                cp.get(project, 'baseurl')
            )
        else:
            gh = GerritGitProject(project, git_basedir)
        if cp.has_option(project, 'previous'):
            previous = cp.get(project, 'previous')
        else:
            previous = None
        current = cp.get(project, 'current')
        project_name = cp.get(project, 'name')
        if not current:
            raise RuntimeError(
                'Every project must provide previous and current revisions')

        commits = gh.get_commits_between_revs(previous, current)

        bugs_found = []

        for commit in commits:
            for message in commit['message']:
                bug_id = bz.get_bug_id_from_message(message)
                if bug_id is None:
                    sys.stderr.write(
                        'Ignoring commit %s; no bug url found\n' % (
                            commit['sha'],
                        )
                    )
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
                sys.stderr.write('Validating bug #%d\n' % (
                    bug_id,
                ))
                bug = bz.validate_bug(bug_id, target_milestones)
                if bug is None:
                    sys.stderr.write('Bug #%d is not valid\n' % (
                        bug_id,
                    ))
                else:
                    sys.stderr.write('Bug #%d is valid\n' % (
                        bug.id,
                    ))
                    if bug.id != bug_id:
                        # A clone has been created after the patch has been merged
                        sys.stderr.write(
                            'A clone of bug #%d has been created after the patch '
                            'has been merged; clone is bug #%d\n' % (
                            bug_id,
                            bug.id
                        ))
                        bug_id = bug.id
                        if bug_id in bugs_found:
                            sys.stderr.write('Ignoring repeated bug; bug #%d\n' % (
                                bug_id,
                            ))
                            continue
                    bugs_found.append(bug_id)

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
                            ).replace(
                                # kramdown, our site's processor, replaces --
                                # with an en-dash. Escape to prevent that.
                                # https://kramdown.gettalong.org/syntax.html
                                ' -- ',
                                ' \-- '
                            ).splitlines()
                        )
                    proj.sort(sort_function)
        list_url = "%sbuglist.cgi?action=wrap&bug_id=" % BUGZILLA_HOME
        for bug in bugs_found:
            list_url += "{id}%2C%20".format(id=bug)
        if bugs_found:
            sys.stderr.write(
                '\nBugs in {project} fixed in version {version}:\n'.format(
                    project=project,
                    version=current,
                )
            )
            sys.stderr.write(list_url+'\n\n\n\n')

    sys.stdout.write(
        codecs.encode(
            TEMPLATE.render(
                release=ORDINALS[rc] if rc else None,
                milestone=milestone.split('-')[-1],
                current_date=datetime.utcnow().strftime('%B %d, %Y'),
                release_type=release_type,
                release_rpm="".join(milestone.split('-')[1].split('.')[0:2])
            ),
            'utf-8',
            'xmlcharrefreplace'
        )
    )

    sys.stdout.write(
        '\n\n## What\'s New in %s?\n\n' % milestone.split('-')[-1]
    )

    bug_types = generated.keys()
    bug_types.sort(section_sort_function)
    for bug_type in bug_types:
        sys.stdout.write(
            '### %s\n\n' % bug_type
            .replace("Enhancement", "Enhancements")
            .replace("Unclassified", "Other")
            .replace("Bug Fix", "Bug Fixes")
        )

        for project in generated[bug_type]:
            sys.stdout.write('#### %s\n\n' % project)
            for bug in generated[bug_type][project]:
                if bug_type.lower() == 'bug fix':
                    sys.stdout.write(
                        ' - [BZ {id}](https://bugzilla.redhat.com/{id}) '
                        '<b>{summary}</b><br>\n'.format(**bug)
                    )
                else:
                    sys.stdout.write(
                        ' - [BZ {id}](https://bugzilla.redhat.com/{id}) '
                        '<b>{summary}</b><br>{release_notes}\n'.format(**bug)
                    )

                bug_list.append(bug)

            sys.stdout.write('\n')
    list_url = "%sbuglist.cgi?action=wrap&bug_id=" % BUGZILLA_HOME
    bugs_listed_in_git_logs = set(bug['id'] for bug in bug_list)
    search_for_missing_builds(target_milestones, bugs_listed_in_git_logs)

    for bug in bugs_listed_in_git_logs:
        list_url += "{id}%2C%20".format(id=bug)
    sys.stderr.write('\n\n\nBugs included in this release notes:\n')
    sys.stderr.write(list_url+'\n')


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--release', type=int,
                        help='RC number of the release, if type is specified')
    parser.add_argument('--release-type', type=str,
                        help='release type: alpha, beta, rc, empty if GA')
    parser.add_argument('--git-basedir', metavar='DIR', default=None,
                        help=(
                            'base directory to store git repositories. will '
                            'use temp dirs by default'
                        ))
    parser.add_argument('target_release', metavar='TARGET-RELEASE',
                        help='target release. e.g. ovirt-3.6.5')

    args = parser.parse_args()

    generate_notes(
        args.target_release,
        args.release,
        args.git_basedir,
        args.release_type
    )

    return 0


if __name__ == '__main__':
    sys.exit(main())

# vim: expandtab tabstop=4 shiftwidth=4
