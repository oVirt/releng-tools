#!/usr/bin/python

# Copyright (C) 2017 Red Hat, Inc.
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
Recursively check for old rpms under a path
"""

import argparse
import collections
import os
from rpmUtils.miscutils import splitFilename
from distutils.version import LooseVersion


def check(basedir):
    print("------------------------------")
    print("Recursively check for old rpms")
    print("------------------------------")

    duplicates = []
    dirlist = []
    for root, dirs, files in os.walk(basedir):
        for d in dirs:
            dirlist.append(os.path.join(root, d))

    for wdir in dirlist:
        repo = collections.defaultdict(dict)
        for filename in os.listdir(wdir):
            if filename.endswith(".rpm"):
                (n, v, r, e, a) = splitFilename(filename)
                if not e:
                    e = 'e'
                if a in repo and e in repo[a] and n in repo[a][e]:
                    sv = repo[a][e][n][0]
                    if LooseVersion(sv) > LooseVersion(v):
                        d = os.path.join(wdir, filename)
                        duplicates.append(d)
                    else:
                        d = os.path.join(wdir, repo[a][e][n][1])
                        duplicates.append(d)
                        repo[a][e][n] = (v, filename)
                else:
                    if e not in repo[a]:
                        repo[a][e] = {}
                    repo[a][e][n] = (v, filename)

    duplicates.sort()
    for d in duplicates:
        print(d)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="The base path to be checked recursively")
    args = parser.parse_args()
    check(args.path)
