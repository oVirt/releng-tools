#!/usr/bin/python3

# Copyright (C) 2021 Red Hat, Inc.
# Author: Lev Veyde <lveyde@redhat.com>
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
#

import argparse
import hawkey
import os
import requests
import rpm
import sys

from dnf.subject import Subject

node_baseurl = ('https://jenkins.ovirt.org/job/ovirt-node-ng-image_master_'
                'build-artifacts-el8-x86_64/{}/artifact/exported-artifacts/'
                'ovirt-node-ng-image.manifest-rpm')

appliance_baseurl = ('https://jenkins.ovirt.org/job/ovirt-appliance_master_'
                     'build-artifacts-el8-x86_64/{}/artifact/'
                     'exported-artifacts/'
                     'ovirt-engine-appliance-manifest-rpm')

pkg_name_width = 40
pkg_ver_width = 40


class ColorPrint(object):
    Colors = {
        'red': '\033[1;31m',
        'blue': '\033[1;34m',
        'green': '\033[0;32m',
    }

    Prefixes = {
        'ok': 'OK: ',
        'warn': 'Warning: ',
        'err': 'Error: ',
    }

    RESET = "\033[0;0m"

    @staticmethod
    def print_message(message_prefix, message):
        prefix_color, prefix_text = message_prefix
        sys.stdout.write(prefix_color)
        print(prefix_text, end="")
        sys.stdout.write(ColorPrint.RESET)
        print(message)


def process_list(package_list):
    packages = {}
    for rpm_package in package_list:
        if rpm_package.strip() != '':
            subject = Subject(rpm_package)
            nevra = subject.get_nevra_possibilities(forms=hawkey.FORM_NEVRA)
            (
                pkg_name,
                version,
                release,
                epoch,
                arch,
            ) = (
                nevra[0].name,
                nevra[0].version,
                nevra[0].release,
                nevra[0].epoch,
                nevra[0].arch,
            )

            if pkg_name == '':
                print("Couldn't process package {}".format(rpm_package))
        else:
            continue

        packages[pkg_name] = {}
        packages[pkg_name]['rpm'] = rpm_package
        packages[pkg_name]['pkg_name'] = pkg_name
        packages[pkg_name]['version'] = version
        packages[pkg_name]['release'] = release
        packages[pkg_name]['epoch'] = epoch
        packages[pkg_name]['arch'] = arch
    return packages


def version_compare(package1, package2):
    return rpm.labelCompare(
        (
            package1['epoch'],
            package1['version'],
            package1['release'],
        ),
        (
            package2['epoch'],
            package2['version'],
            package2['release'],
        )
    )


def combine_list(package_list1, package_list2):
    pkg_list = []

    for package_list in (package_list1, package_list2):
        for package_name in package_list:
            pkg_list.append(package_name)

    pkg_set = set(pkg_list)
    pkg_list = sorted(list(pkg_set))
    return pkg_list


def compare(package_list1, package_list2):
    not_changed = {}
    upgraded = {}
    downgraded = {}
    added = {}
    removed = {}

    pkg_list = combine_list(package_list1, package_list2)

    for pkg_name in pkg_list:
        package_name = "{0:{pkg_name_width}}".format(
            pkg_name,
            pkg_name_width=pkg_name_width,
        )
        if pkg_name in package_list1 and pkg_name in package_list2:
            cmp = version_compare(
                package_list1[pkg_name],
                package_list2[pkg_name],
            )
            if cmp:
                versions = ("{0:{pkg_ver_width}}{1:{pkg_ver_width}}".format(
                    package_list1[pkg_name]['version'] +
                    '-' + package_list1[pkg_name]['release'],
                    package_list2[pkg_name]['version'] +
                    '-' + package_list2[pkg_name]['release'],
                    pkg_ver_width=pkg_ver_width,
                ))

                if cmp < 0:
                    color = ColorPrint.Colors['green']
                    upgraded[pkg_name] = {}
                    upgraded[pkg_name]['pkg_name'] = pkg_name
                    upgraded[pkg_name]['old_rpm'] = (
                        package_list1[pkg_name]['rpm']
                    )
                    upgraded[pkg_name]['new_rpm'] = (
                        package_list2[pkg_name]['rpm']
                    )
                    upgraded[pkg_name]['old_version'] = (
                        package_list1[pkg_name]['version']
                    )
                    upgraded[pkg_name]['new_version'] = (
                        package_list2[pkg_name]['version']
                    )
                    upgraded[pkg_name]['old_release'] = (
                        package_list1[pkg_name]['release']
                    )
                    upgraded[pkg_name]['new_release'] = (
                        package_list1[pkg_name]['release']
                    )
                    upgraded[pkg_name]['old_epoch'] = (
                        package_list1[pkg_name]['epoch']
                    )
                    upgraded[pkg_name]['new_epoch'] = (
                        package_list2[pkg_name]['epoch']
                    )
                    upgraded[pkg_name]['arch'] = (
                        package_list1[pkg_name]['arch']
                    )
                else:
                    color = ColorPrint.Colors['red']
                    downgraded[pkg_name] = {}
                    downgraded[pkg_name]['pkg_name'] = pkg_name
                    downgraded[pkg_name]['old_rpm'] = (
                        package_list1[pkg_name]['rpm']
                    )
                    downgraded[pkg_name]['new_rpm'] = (
                        package_list2[pkg_name]['rpm']
                    )
                    downgraded[pkg_name]['old_version'] = (
                        package_list1[pkg_name]['version']
                    )
                    downgraded[pkg_name]['new_version'] = (
                        package_list2[pkg_name]['version']
                    )
                    downgraded[pkg_name]['old_release'] = (
                        package_list1[pkg_name]['release']
                    )
                    downgraded[pkg_name]['new_release'] = (
                        package_list1[pkg_name]['release']
                    )
                    downgraded[pkg_name]['old_epoch'] = (
                        package_list1[pkg_name]['epoch']
                    )
                    downgraded[pkg_name]['new_epoch'] = (
                        package_list2[pkg_name]['epoch']
                    )
                    downgraded[pkg_name]['arch'] = (
                        package_list1[pkg_name]['arch']
                    )

                ColorPrint.print_message(
                    (
                        color,
                        package_name,
                    ),
                    versions,
                )
            else:
                not_changed[pkg_name] = {}
                not_changed[pkg_name]['pkg_name'] = pkg_name
                not_changed[pkg_name]['rpm'] = package_list1[pkg_name]['rpm']
                not_changed[pkg_name]['version'] = (
                    package_list1[pkg_name]['version']
                )
                not_changed[pkg_name]['release'] = (
                    package_list1[pkg_name]['release']
                )
                not_changed[pkg_name]['epoch'] = (
                    package_list1[pkg_name]['epoch']
                )
                not_changed[pkg_name]['arch'] = (
                    package_list1[pkg_name]['arch']
                )

        elif pkg_name in package_list1:
            removed[pkg_name] = {}
            removed[pkg_name]['pkg_name'] = pkg_name
            removed[pkg_name]['rpm'] = package_list1[pkg_name]['rpm']
            removed[pkg_name]['version'] = package_list1[pkg_name]['version']
            removed[pkg_name]['release'] = package_list1[pkg_name]['release']
            removed[pkg_name]['epoch'] = package_list1[pkg_name]['epoch']
            removed[pkg_name]['arch'] = package_list1[pkg_name]['arch']

            versions = ("{0:{pkg_ver_width}}".format(
                package_list1[pkg_name]['version'] + '-' +
                package_list1[pkg_name]['release'],
                pkg_ver_width=pkg_ver_width,
                )
            )
            color = ColorPrint.Colors['blue']
            ColorPrint.print_message(
                (
                    color,
                    package_name,
                ),
                versions,
            )
        else:
            added[pkg_name] = {}
            added[pkg_name]['pkg_name'] = pkg_name
            added[pkg_name]['rpm'] = package_list2[pkg_name]['rpm']
            added[pkg_name]['version'] = package_list2[pkg_name]['version']
            added[pkg_name]['release'] = package_list2[pkg_name]['release']
            added[pkg_name]['epoch'] = package_list2[pkg_name]['epoch']
            added[pkg_name]['arch'] = package_list2[pkg_name]['arch']

            versions = ("{0:{pkg_ver_width}}{1:{pkg_ver_width}}".format(
                '    ',
                package_list2[pkg_name]['version'] + '-' +
                package_list2[pkg_name]['release'],
                pkg_ver_width=pkg_ver_width,
                )
            )
            color = ColorPrint.Colors['blue']
            ColorPrint.print_message(
                (
                    color,
                    package_name,
                ),
                versions,
            )
    result = {}
    result['added'] = added
    result['downgraded'] = downgraded
    result['not_changed'] = not_changed
    result['removed'] = removed
    result['upgraded'] = upgraded
    return result


def process_build_arg(arg, type):
    if os.path.isfile(os.path.abspath(arg)):
        with open(os.path.abspath(arg)) as f:
            build_list = f.readlines().decode("utf-8")
    else:
        if type == 'appliance':
            url = appliance_baseurl.format(arg)
        else:
            url = node_baseurl.format(arg)

        r = requests.get(url, allow_redirects=True)
        if r.status_code != 200:
            sys.stderr.write(
                "Can't fetch manifest from {} - got status code {}\n".format(
                    url,
                    r.status_code,
                )
            )
            sys.exit(1)
        build_list = r.content.decode("utf-8").splitlines()

    return build_list


def main():
    global pkg_name_width, pkg_ver_width
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'first_build',
        metavar='FIRST-BUILD',
        help='first build. either a Jenkins build number e.g.'
             ' 529 or a local manifest filename'
    )
    parser.add_argument(
        'second_build',
        metavar='SECOND-BUILD',
        help='second build either a Jenkins build number e.g.'
             ' 584 or a local manifest filename'
    )
    parser.add_argument(
        '--build-type',
        type=str,
        default='node',
        help='build type: node or appliance. default=node'
    )
    parser.add_argument(
        '--name-width',
        type=int,
        default=40,
        help='package name column width. default=40'
    )
    parser.add_argument(
        '--version-width',
        type=int,
        default=40,
        help='package version column width. default=40'
    )
    args = parser.parse_args()
    pkg_name_width = args.name_width
    pkg_ver_width = args.version_width

    build1_content = process_build_arg(args.first_build, args.build_type)
    build2_content = process_build_arg(args.second_build, args.build_type)

    list1 = process_list(build1_content)
    list2 = process_list(build2_content)
    compare(list1, list2)


if __name__ == '__main__':
    sys.exit(main())

# vim: expandtab tabstop=4 shiftwidth=4
