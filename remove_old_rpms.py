#!/usr/bin/python

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
import glob
import os
import rpm
import sys

from rpmUtils.miscutils import splitFilename


def process_directory(directory, **kwargs):
    dir_rpms = glob.glob(os.path.join(directory, "*.rpm"))
    if not dir_rpms:
        raise Exception(
            "Directory {} does NOT contain any RPM files".format(
                directory
            )
        )
    process_rpms(dir_rpms, **kwargs)


def process_rpms(rpm_list, debug=False, dry_run=False, **kwargs):
    rpms = {}
    for rpm_file in rpm_list:
        rpm_entry = process_rpm(
            rpm_file,
            debug=debug,
            dry_run=dry_run,
            **kwargs
        )
        pkg_name = rpm_entry['pkg_name']
        if pkg_name not in rpms.keys():
            rpms[pkg_name] = rpm_entry
        else:
            if compare_rpm_entries(
                rpms[pkg_name],
                rpm_entry,
                debug=debug,
                dry_run=dry_run,
                **kwargs
            ) < 0:
                if debug:
                    print("Removing {} as found newer version {}".format(
                        rpms[pkg_name]['rpm_file'],
                        rpm_file,
                    ))
                if not dry_run:
                    os.remove(rpms[pkg_name]['rpm_file'])
                else:
                    print(rpms[pkg_name]['rpm_file'])
                rpms[pkg_name] = rpm_entry
            else:
                if debug:
                    print("Removing older {}".format(rpm_file))
                if not dry_run:
                    os.remove(rpm_file)
                else:
                    print(rpm_file)


def process_rpm(rpm_file, **kwargs):
    rpm_base_filename = os.path.basename(rpm_file)
    (
        pkg_name,
        version,
        release,
        epoch,
        arch
    ) = splitFilename(rpm_base_filename)
    rpm_entry = {}
    rpm_entry['rpm_file'] = rpm_file
    rpm_entry['rpm_base_filename'] = rpm_base_filename
    rpm_entry['pkg_name'] = pkg_name
    rpm_entry['version'] = version
    rpm_entry['release'] = release
    rpm_entry['epoch'] = epoch
    rpm_entry['arch'] = arch
    return rpm_entry


def compare_rpm_entries(current, new, **kwargs):
    return rpm.labelCompare(
        (
            current['epoch'],
            current['version'],
            current['release'],
        ),
        (
            new['epoch'],
            new['version'],
            new['release'],
        )
    )


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('directory', metavar='Dir',
                        help='Directory to remove duplicate RPMs from')
    parser.add_argument('--debug', action='store_true',
                        help='show extra debug information')
    parser.add_argument('--dry-run', action='store_true',
                        help='only show what files will be removed')
    args = parser.parse_args()

    try:
        process_directory(
            args.directory,
            debug=args.debug,
            dry_run=args.dry_run,
        )
        return 0
    except Exception as e:
        print(e)
        return 1


if __name__ == '__main__':
    sys.exit(main())

# vim: expandtab tabstop=4 shiftwidth=4
