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


BUGZILLA_SERVER = 'bugzilla.redhat.com'
BUGZILLA_HOME = 'https://%s/' % BUGZILLA_SERVER
BUGZILLA_URL = BUGZILLA_HOME + 'xmlrpc.cgi'


class GetReleaseNotes(object):
    def __init__(self):
        super(GetReleaseNotes, self).__init__()
        self._args = None
        self._bugs = {}

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
            #if bz.cf_fixed_in != "ovirt 4.0.0 alpha1":
                #continue
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
            if '---' in bz.target_release:
                sys.stderr.write(
                    "%d - has no target release so we consider it "
                    "not fixed\n" % (bz.id,)
                )
                continue

            if bz.cf_doc_type not in self._bugs:
                self._bugs[bz.cf_doc_type] = {}

            product = bz.product
            if bz.classification != 'oVirt':
                product = bz.component

            if product not in self._bugs[bz.cf_doc_type]:
                self._bugs[bz.cf_doc_type][product] = []

            self._bugs[bz.cf_doc_type][product].append(copy.copy(bz))

        for doc_type in self._bugs:
            print('\n' *10)
            print('\n## ' + doc_type + '\n')
            for product in self._bugs[doc_type]:
                print('\n### ' + product + '\n')
                for bz in self._bugs[doc_type][product]:
                    print ' - [BZ %s](%s%s) <b>%s</b><br>' % (
                        str(bz.id),
                        BUGZILLA_HOME,
                        str(bz.id),
                        codecs.encode(
                            bz.summary, "utf-8", "xmlcharrefreplace"
                        )

                    )
                    if doc_type != "Bug Fix":
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
