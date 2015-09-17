#!/usr/bin/python -O
# -*- coding: utf-8 -*-


# Copyright (C) 2014 Red Hat, Inc., Sandro Bonazzola <sbonazzo@redhat.com>
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
Get bugs from bugzilla
TODO: integrate with check_patches
"""

import argparse
import bugzilla
import codecs
import git
import sys


BUGZILLA_SERVER = 'bugzilla.redhat.com'
BUGZILLA_HOME = 'https://%s/' % BUGZILLA_SERVER
BUGZILLA_URL = BUGZILLA_HOME + 'xmlrpc.cgi'


class GetBugs(object):
    def __init__(self):
        super(GetBugs, self).__init__()
        self._repo = git.Git('.')
        self._args = None

    def parse_args(self):
        parser = argparse.ArgumentParser(
            description=(
                'Check Bug-Url referenced between 2 git references'
            ),
        )
        parser.add_argument(
            'previous',
            metavar='previous',
            type=str,
            help='previous version git reference'
        )
        parser.add_argument(
            'current',
            metavar='current',
            type=str,
            help='previous version git reference'
        )
        parser.add_argument(
            '--show-target',
            action='store_true',
            help='shows target version in the output',
            default=False,
        )
        parser.add_argument(
            '--show-fixed',
            action='store_true',
            help='shows fixed-in-version in the output',
            default=False,
        )
        self._args = parser.parse_args()

    def main(self):
        self.parse_args()
        bzobj = bugzilla.RHBugzilla4(url=BUGZILLA_URL)
        current = []
        for line in self._repo.log([self._args.current]).splitlines():
            if line.lower().find('bug-url') >= 0:
                line = line.replace('show_bug.cgi?id=', '')
                try:
                    current.append(
                        int(
                            line[
                                line.find(BUGZILLA_SERVER) +
                                len(BUGZILLA_SERVER) + 1:
                            ]
                        )
                    )
                except ValueError as e:
                    sys.stderr.write(
                        'Invalid input in %s: %s\n' % (
                            self._args.current,
                            line,
                        )
                    )
                    sys.stderr.write(str(e))
        current.sort()

        previous = []
        for line in self._repo.log([self._args.previous]).splitlines():
            if line.lower().find('bug-url') >= 0:
                line = line.replace('show_bug.cgi?id=', '')
                try:
                    previous.append(
                        int(
                            line[
                                line.find(BUGZILLA_SERVER) +
                                len(BUGZILLA_SERVER) + 1:
                            ]
                        )
                    )
                except ValueError as e:
                    sys.stderr.write(
                        'Invalid input in %s: %s\n' % (
                            self._args.previous,
                            line,
                        )
                    )
                    sys.stderr.write(str(e))
        previous.sort()

        not_in_old = set(current) - set(previous)
        ids = list(not_in_old)
        ids.sort()

        list_url = "%sbuglist.cgi?action=wrap&bug_id=" % BUGZILLA_HOME
        for bug_id in ids:
            sys.stderr.write('fetching %d\n' % bug_id)
            queryobj = bzobj.build_query(bug_id=str(bug_id))
            ans = bzobj.query(queryobj)
            if ans:
                r = ans[0]
                if (
                    r.product in (
                        'Red Hat Enterprise Virtualization Manager',
                        'oVirt',
                        'Red Hat Storage',
                        'Red Hat Gluster Storage',
                    )
                ) or (
                    r.classification == 'oVirt'
                ):
                    if r.status not in (
                        'MODIFIED',
                        'ON_QA',
                        'VERIFIED',
                        'RELEASE_PENDING',
                        'CLOSED',
                    ):
                        sys.stderr.write(
                            "%d - is in status %s\n" % (bug_id, r.status)
                        )
                    else:
                        list_url += "%s%%2C " % bug_id
                        sys.stdout.write('{{BZ|')
                        sys.stdout.write(str(r.id))
                        sys.stdout.write('}}')
                        sys.stdout.write(' - ')
                        if self._args.show_target:
                            sys.stdout.write(str(r.target_release))
                            sys.stdout.write(' - ')
                        if self._args.show_fixed:
                            sys.stdout.write(str(r.fixed_in))
                            sys.stdout.write(' - ')
                        sys.stdout.write(
                            codecs.encode(
                                r.summary, "utf-8", "xmlcharrefreplace"
                            )
                        )
                        sys.stdout.write('<BR>\n')
                else:
                    sys.stderr.write(
                        "%d - has product %s\n" % (bug_id, r.product)
                    )
            else:
                sys.stderr.write("%d - is a private bug\n" % bug_id)
                list_url += "%s%%2C " % bug_id

        sys.stderr.flush()
        sys.stderr.write('\n\n'+list_url+'\n')
        sys.stderr.flush()

if __name__ == '__main__':
    GetBugs().main()
