#!/usr/bin/python3

# Copyright (C) 2020-2022 Red Hat, Inc.
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

import glob
import hawkey
import os
import rpm
import sys

DEBUG = 0
base_dir = "/var/www/html/pub/"
base_repo_dir = base_dir + "yum-repo/"

repos = (
    {
        'link': 'ovirt-release43.rpm',
        'pkg_name': 'ovirt-release43',
        'dir': ('ovirt-4.3',),
        'distro': 'el7',
        'glob': 'ovirt-release43-4.3.*',
    },
    {
        'link': 'ovirt-release43-snapshot.rpm',
        'pkg_name': 'ovirt-release43-snapshot',
        'dir': ('ovirt-4.3-snapshot',),
        'distro': 'el7',
        'glob': 'ovirt-release43-snapshot-4.3.*',
    },
    {
        'link': 'ovirt-release44.rpm',
        'pkg_name': 'ovirt-release44',
        'dir': ('ovirt-4.4',),
        'distro': 'el8',
        'glob': 'ovirt-release44-4.4.*',
    },
    {
        'link': 'ovirt-release44-pre.rpm',
        'pkg_name': 'ovirt-release44-pre',
        'dir': ('ovirt-4.4', 'ovirt-4.4-pre'),
        'distro': 'el8',
        'glob': 'ovirt-release44-pre-4.4.*',
    },
    {
        'link': 'ovirt-release-master.rpm',
        'pkg_name': 'ovirt-release-master',
        'dir': ('ovirt-master-snapshot',),
        'distro': 'el8',
        'glob': 'ovirt-release-master-4.5.*',
    },
)


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
        print(prefix_text),
        sys.stdout.write(ColorPrint.RESET)
        print(message)


def find_latest_package(repo):
    rpms = []
    for dir in repo['dir']:
        dir_rpms = glob.glob(os.path.join(
            base_dir,
            dir,
            "rpm",
            repo['distro'],
            "noarch",
            repo['glob']
        ))
        if dir_rpms:
            for rpm_file in dir_rpms:
                rpm_base_filename = os.path.basename(rpm_file)
                nevra = hawkey.split_nevra(rpm_base_filename[:-len(".rpm")])
                pkg_name = nevra.name
                version = nevra.version
                release = str(nevra.release)
                epoch = str(nevra.epoch)
                arch = nevra.arch
                rpm_entry = {}
                rpm_entry['rpm_file'] = rpm_file
                rpm_entry['rpm_base_filename'] = rpm_base_filename
                rpm_entry['pkg_name'] = pkg_name
                rpm_entry['version'] = version
                rpm_entry['release'] = release
                rpm_entry['epoch'] = epoch
                rpm_entry['arch'] = arch
                if pkg_name == repo['pkg_name']:
                    rpms.append(rpm_entry)
                else:
                    msg = (
                        "Warning: glob definition ({}) of package {} "
                        "seems to be not specific enough, as it caught "
                        "other package ({})".format(
                            repo['glob'],
                            repo['pkg_name'],
                            pkg_name,
                        )
                    )
                    ColorPrint.print_message(
                        (
                            ColorPrint.Colors['blue'],
                            ColorPrint.Prefixes['warn'],
                        ),
                        msg,
                    )

    latest_pkg = {}
    for pkg in rpms:
        if not latest_pkg:
            latest_pkg = pkg
        else:
            if rpm.labelCompare(
                (
                    latest_pkg['epoch'],
                    latest_pkg['version'],
                    latest_pkg['release'],
                ),
                (
                    pkg['epoch'],
                    pkg['version'],
                    pkg['release'],
                )
            ) < 0:
                latest_pkg = pkg

    if DEBUG:
        for rpm_entry in rpms:
            print("\t %s" % (rpm_entry))
        print("\t Latest: %s" % (latest_pkg))
    return latest_pkg['rpm_file']


def main():
    ret = 0
    for repolink in repos:
        print("\n{}:".format(repolink['link']))
        link = base_repo_dir + repolink['link']
        if not os.path.islink(link):
            msg = (
                "\t{} is not a link!".format(repolink['link'])
            )
            ColorPrint.print_message(
                (
                    ColorPrint.Colors['red'],
                    ColorPrint.Prefixes['err'],
                ),
                msg,
            )
            ret = 1
            continue
        if not os.path.exists(
            os.path.normpath(os.path.join(base_repo_dir, os.readlink(link)))
        ):
            msg = (
                "\tBroken link, {} points to "
                "non existing file ({})".format(
                    repolink['link'],
                    os.readlink(link),
                )
            )
            ColorPrint.print_message(
                (
                    ColorPrint.Colors['red'],
                    ColorPrint.Prefixes['err'],
                ),
                msg,
            )
            ret = 2
            continue
        pkg = os.path.realpath(base_repo_dir + repolink['link'])
        basename = os.path.basename(pkg)
        nevra = hawkey.split_nevra(basename[:-len(".rpm")])
        pkg_name = nevra.name
        pkg_arch = nevra.arch
        if repolink['pkg_name'] != pkg_name:
            msg = (
                "\tA link to {} is pointing "
                "to wrong package ({})".format(
                    repolink['link'],
                    pkg_name,
                )
            )
            ColorPrint.print_message(
                (
                    ColorPrint.Colors['red'],
                    ColorPrint.Prefixes['err'],
                ),
                msg,
            )
            ret = 3
            continue
        if pkg_arch != 'noarch':
            msg = (
                "\tA link to {} is pointing to a "
                "package of non-noarch type ({})".format(
                    repolink['link'],
                    pkg_arch,
                )
            )
            ColorPrint.print_message(
                (
                    ColorPrint.Colors['red'],
                    ColorPrint.Prefixes['err'],
                ),
                msg,
            )
            ret = 4
            continue
        latest_pkg = find_latest_package(repolink)
        if not os.path.basename(latest_pkg) == basename:
            msg = (
                "\tCurrently points to: {}\n\t( {} )\n\t"
                "But a more recent package is available at:\n\t( {} )".format(
                    basename,
                    os.readlink(link),
                    os.path.relpath(latest_pkg, base_repo_dir)
                )
            )
            ColorPrint.print_message(
                (
                    ColorPrint.Colors['blue'],
                    ColorPrint.Prefixes['warn'],
                ),
                msg,
            )
            ret = 5
        else:
            msg = (
                "\tPoints to: {}\n\t( {} )".format(
                    basename,
                    os.readlink(link),
                )
            )
            ColorPrint.print_message(
                (
                    ColorPrint.Colors['green'],
                    ColorPrint.Prefixes['ok'],
                ),
                msg,
            )
    print("")
    return(ret)


if __name__ == '__main__':
    sys.exit(main())

# vim: expandtab tabstop=4 shiftwidth=4
