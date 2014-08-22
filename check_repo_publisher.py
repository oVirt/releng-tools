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
Perform validation based on publisher jobs
"""

import collections
import re
import sys
import urlgrabber


def main():
    server = "http://plain.resources.ovirt.org"
    if len(sys.argv) != 3:
        print("Usage:")
        print(
            "{command} {job} {repo}".format(
                command=sys.argv[0],
                job=(
                    "http://jenkins.ovirt.org/view/Publishers/job/"
                    "publish_ovirt_rpms_nightly_3.5/73/console"
                ),
                repo="/repos/ovirt-3.5-pre",
            )
        )
        sys.exit(1)
    job = sys.argv[1]
    baseurl = sys.argv[2]

    u = urlgrabber.urlopen(job)
    content = u.read()
    u.close()

    required = []
    for line in content.splitlines():
        if line.find('SSH: put') != -1:
            filename = line[line.find('[')+1:line.find(']')]
            if filename not in required:
                required.append(filename)
                if filename.endswith('.tar.gz'):
                    required.append(filename + '.sig')

    print("------------------------------")
    print("Checking Jenkins jobs goodness")
    print("------------------------------")

    print("publisher job: %s" % job)
    print(
        "repository: {server}{baseurl}\n\n".format(
            server=server,
            baseurl=baseurl,
        )
    )

    m = re.compile(r'^(?P<package>([a-zA-Z0-9]+\-)+[0-9\.]+[_0-9a-zA-Z\.]*)')
    for filename in required:
        if filename.endswith('.src.rpm'):
            package = m.match(filename)
            if package is not None:
                tarball = package.groupdict()['package'] + ".tar.gz"
                if tarball not in required:
                    print(
                        (
                            "missing sources : {tarball}\n"
                            "for rpm: {rpm}\n"
                            "found:\n"
                        ).format(
                            tarball=tarball,
                            rpm=filename,
                        )
                    )
                    for x in required:
                        if (
                            x.startswith(package.groupdict()['package']) and
                            x.endswith('tar.gz')
                        ):
                            print(x)

    not_required = []
    queue = collections.deque()
    queue.append(
        "{server}{baseurl}".format(
            server=server,
            baseurl=baseurl,
        )
    )

    m = re.compile('href="([^"]*)"')

    print(
        "\n\n\n"
        "-------------------------------------------------------\n"
        "Checking expected repository content from publisher job\n"
        "-------------------------------------------------------\n"
    )

    while queue:
        newitem = queue.popleft()
        print("processing %s" % newitem)
        u = urlgrabber.urlopen(newitem)
        root = u.read()
        u.close()
        for x in m.findall(root):
            if not (
                x.startswith('?') or
                x.startswith('/')
            ):
                if (
                    x.endswith('.rpm') or
                    x.endswith('.iso') or
                    x.endswith('.exe') or
                    x.endswith('.gz') or
                    x.endswith('.sig') or
                    x.endswith('.bz2') or
                    x.endswith('.xml') or
                    x.endswith('.zip')
                ):
                    if x in required:
                        required.remove(x)
                    else:
                        not_required.append(x)
                else:
                    queue.append(
                        "{baseurl}/{x}".format(
                            baseurl=newitem,
                            x=x,
                        )
                    )

    print(
        "The following packages were in the publisher job and are "
        "missing in the repo:"
    )
    for x in required:
        print x


if __name__ == "__main__":
    main()
