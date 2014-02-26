#!/usr/bin/python

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
List newest packages in the given repository
"""

import sys

import yum
from yum.packageSack import ListPackageSack
import rpmUtils.arch

def main():
    base = yum.YumBase()
    conf = base.doConfigSetup()
    base.setCacheDir(force=True)
    base.doLock()
    storage = base.doRepoSetup()
    myrepos = []

    repo = sys.argv[1]
    myrepos.extend(base.repos.findRepos(repo))
    for repo in base.repos.repos.values():
        repo.disable()
    for repo in myrepos:
        repo.enable()
    arches = rpmUtils.arch.getArchList('x86_64')
    arches.extend(rpmUtils.arch.getArchList('ppc64'))
    base.doSackSetup(arches)

    for repo in base.repos.listEnabled():
        reposack = ListPackageSack(base.pkgSack.returnPackages(repoid=repo.id))
        download_list = reposack.returnNewestByNameArch()
        pkg_list = [pkg.relativepath for pkg in download_list]
        pkg_list.sort()
        for pkg in pkg_list:
            print(pkg)

    base.closeRpmDB()

if __name__ == "__main__":
    main()
