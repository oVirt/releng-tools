#!/usr/bin/python -O
# -*- coding: utf-8 -*-


# Copyright (C) 2015 Red Hat, Inc., Sandro Bonazzola <sbonazzo@redhat.com>
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
Get info from bugzilla for helping with release note writing
"""


import argparse
import bugzilla
import codecs
import sys
import copy
import collections

BUGZILLA_SERVER = 'bugzilla.redhat.com'
BUGZILLA_HOME = 'https://%s/' % BUGZILLA_SERVER
BUGZILLA_URL = BUGZILLA_HOME + 'xmlrpc.cgi'


class GetReleaseNotes(object):
    def __init__(self):
        super(GetReleaseNotes, self).__init__()
        self._args = None
        self._bugs = collections.OrderedDict()
        self._bugs['ovirt-engine'] = collections.OrderedDict()
        self._bugs['ovirt-engine']['en'] = []
        self._bugs['ovirt-engine']['bug'] = []
        self._bugs['vdsm'] = collections.OrderedDict()
        self._bugs['vdsm']['en'] = []
        self._bugs['vdsm']['bug'] = []


    def parse_args(self):
        parser = argparse.ArgumentParser(
            description=(
                'Get release notes for a given target milestone'
            ),
        )
        parser.add_argument(
            'target_milestone',
            metavar='target_milestone',
            type=str,
            help='Target Milestone',
        )
        self._args = parser.parse_args()

    def main(self):
        self.parse_args()
        bzobj = bugzilla.RHBugzilla4(url=BUGZILLA_URL)
        queryobj = bzobj.build_query(
            target_milestone=self._args.target_milestone,
        )
        ans = bzobj.query(queryobj)
        list_url = "%sbuglist.cgi?action=wrap&bug_id=" % BUGZILLA_HOME
        for bz in ans:
            if not (
                (
                    bz.product in (
                        'Red Hat Enterprise Virtualization Manager',
                        'oVirt',
                        'Red Hat Storage',
                        'Red Hat Gluster Storage',
                    )
                ) or (bz.classification == 'oVirt')
            ):
                sys.stderr.write(
                    "%d - has product %s\n" % (bz.id, bz.product)
                )
            if bz.status not in (
                'MODIFIED',
                'ON_QA',
                'VERIFIED',
                'RELEASE_PENDING',
                'CLOSED',
            ):
                sys.stderr.write(
                    "%d - is in %s state\n" % (bz.id, bz.status)
                )
                continue
            if bz.resolution in (
                'WONTFIX',
                'DUPLICATE',
                'NOTABUG',
                'DEFERRED',
            ):
                sys.stderr.write(
                    "%d - is in resolution %s\n" % (bz.id, bz.resolution)
                )
                continue

            if bz.classification != 'oVirt':
                product = bz.component
            else:
                product = bz.product

            if product not in self._bugs:
                self._bugs[product] = collections.OrderedDict()
                self._bugs[product]['en'] = []
                self._bugs[product]['bug'] = []

            if bz.cf_doc_type == 'Enhancement':
                self._bugs[product]['en'].append(copy.copy(bz))
            else:
                self._bugs[product]['bug'].append(copy.copy(bz))

        for product in self._bugs:
            print('\n' *3)

            print('\n## ' + product + '\n')

            for bugtype in self._bugs[product]:
                if len(self._bugs[product][bugtype]) == 0:
                    continue

                if bugtype == 'bug':
                    print('\n### Bug fixes:\n')
                else:
                    print('\n### Enhancements:\n')


                for bz in self._bugs[product][bugtype]:
                    print ' - [BZ %s](%s%s) <b>%s</b><br>' % (
                        str(bz.id),
                        BUGZILLA_HOME,
                        str(bz.id),
                        codecs.encode(
                            bz.summary, "utf-8", "xmlcharrefreplace"
                        )

                    )
                    if bugtype != "bug":
                        notes = bz.cf_release_notes.splitlines()
                        for line in notes:
                            print(
                                codecs.encode(
                                    line, "utf-8", "xmlcharrefreplace"
                                ) + '<br>'
                            )
            list_url += "%s%%2C " % bz.id
        print()
        print(list_url)


if __name__ == '__main__':
    GetReleaseNotes().main()
