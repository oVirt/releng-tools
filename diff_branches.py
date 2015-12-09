#!/usr/bin/python -O
# -*- coding: utf-8 -*-


# Copyright (C) 2014-2015 Red Hat, Inc., Sandro Bonazzola <sbonazzo@redhat.com>
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
Check patches merged on a trunk and not merged in a branch
"""


import argparse
import git


class PatchesChecker(object):
    def __init__(self):
        super(PatchesChecker, self).__init__()
        self._repo = git.Git('.')
        self._args = None

    def parse_args(self):
        parser = argparse.ArgumentParser(
            description=(
                'Check patches merged on a trunk and not merged in a branch'
            ),
        )
        parser.add_argument(
            'trunk',
            metavar='trunk',
            type=str,
            help='branch to be used as reference trunk'
        )
        parser.add_argument(
            'branch',
            metavar='branch',
            type=str,
            help='new branch to be compared with reference trunk'
        )
        self._args = parser.parse_args()

    def parse_log(self, logs, data):
        current_commit = None
        for i in range(len(logs)):
            line = logs[i]
            if line.startswith('commit '):
                if current_commit:
                    data[current_commit['commit']] = current_commit.copy()
                current_commit = {'commit': line}
                current_commit['Author'] = logs[i+1]
                current_commit['Date'] = logs[i+2]
                current_commit['Subject'] = logs[i+4]
            elif line.find('Change-Id:') != -1:
                current_commit['Change'] = line
            elif line.find('Bug-Url:') != -1:
                current_commit['Bug'] = line
        if current_commit:
            data[current_commit['commit']] = current_commit.copy()

    def main(self):
        self.parse_args()
        master = self._repo.log([self._args.trunk]).splitlines()
        master_data = {}
        self.parse_log(master, master_data)
        print('%d patches on %s' % (len(master_data), self._args.trunk))
        branch = self._repo.log([self._args.branch]).splitlines()
        branch_data = {}
        self.parse_log(branch, branch_data)

        print('%d patches on %s' % (len(branch_data), self._args.branch))

        in_branch = [
            branch_data[x]['Change']
            for x in branch_data
            if 'Change' in branch_data[x]
        ]

        count = 0
        for commit in master_data:
            if (
                'Change' in master_data[commit] and
                master_data[commit]['Change'] not in in_branch
            ):
                count += 1
                print(master_data[commit]['commit'])
                print(master_data[commit]['Author'])
                print(master_data[commit]['Date'])
                print(master_data[commit]['Subject'])
                print(master_data[commit]['Change'])
                print(master_data[commit].get('Bug', ''))
                print('')

        print (
            '%d Patches in %s and not in %s branch according to Change-Id' % (
                count, self._args.trunk, self._args.branch
            )
        )


if __name__ == '__main__':
    PatchesChecker().main()
