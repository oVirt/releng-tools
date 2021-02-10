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


import koji


CENTOS_SERVER = 'http://cbs.centos.org/kojihub/'
FEDORA_SERVER = 'http://koji.fedoraproject.org/kojihub/'
FEDORA_STABLE = 'f22'
EPEL_STABLE = 'epel7'

centos_session = koji.ClientSession(CENTOS_SERVER)
fedora_session = koji.ClientSession(FEDORA_SERVER)
verbose = True
ignore_missing = False


def check_cbs_tag(cbs_tag):
    if verbose:
        print('checking %s' % cbs_tag)
    user_tables = centos_session.queryHistory(
        user='sbonazzo',
        tag_names=cbs_tag,
    )
    tag_packages = user_tables['tag_packages']

    for package in tag_packages:
        if package['revoke_event'] is not None:
            continue
        package_name = package['package.name']
        centos_package_version = ''
        centos_package_release = ''
        epel_package_version = ''
        epel_package_release = ''
        fedora_package_version = ''
        fedora_package_release = ''
        try:
            centos_tables = centos_session.queryHistory(package=package_name)
            for table in centos_tables:
                build = centos_tables[table]
                for x in build:
                    if 'build_id' in x and x['tag.name'] == cbs_tag:
                        build_info = centos_session.getBuild(x['build_id'])
                        if build_info is not None:
                            task_id = build_info['task_id']
                            task = centos_session.getTaskInfo(
                                task_id,
                                request=True
                            )
                            task_state = task['state']
                            if task_state == koji.TASK_STATES['CLOSED']:
                                # If CLOSED is true then the package finished
                                # building successfully
                                centos_package_version = x['version']
                                centos_package_release = x['release']
                                break
        except koji.GenericError as e:
            if not ignore_missing:
                print(e)
        try:
            epel_tables = fedora_session.queryHistory(
                package=package_name,
                tag_name=EPEL_STABLE,
                task_state=koji.TASK_STATES['CLOSED'],
            )
            for table in epel_tables:
                build = epel_tables[table]
                for x in build:
                    if 'build_id' in x and x['tag.name'] == EPEL_STABLE:
                        build_info = fedora_session.getBuild(x['build_id'])
                        if build_info is not None:
                            if (
                                build_info['state'] ==
                                koji.BUILD_STATES['COMPLETE']
                            ):
                                task_id = build_info['task_id']
                                task = fedora_session.getTaskInfo(
                                    task_id,
                                    request=True,
                                )
                                task_state = task['state']
                                if task_state == koji.TASK_STATES['CLOSED']:
                                    # If CLOSED is true then the package
                                    # finished building successfully
                                    epel_package_version = x['version']
                                    epel_package_release = x['release']
                                    break
        except koji.GenericError as e:
            if not ignore_missing:
                print(e)
        try:
            fedora_tables = fedora_session.queryHistory(
                package=package_name,
                tag_name=FEDORA_STABLE,
                task_state=koji.TASK_STATES['CLOSED'],
            )
            for table in fedora_tables:
                build = fedora_tables[table]
                for x in build:
                    if 'build_id' in x and x['tag.name'] == FEDORA_STABLE:
                        build_info = fedora_session.getBuild(x['build_id'])
                        if build_info is not None:
                            if (
                                build_info['state'] ==
                                koji.BUILD_STATES['COMPLETE']
                            ):
                                task_id = build_info['task_id']
                                task = fedora_session.getTaskInfo(
                                    task_id,
                                    request=True,
                                )
                                task_state = task['state']
                                if task_state == koji.TASK_STATES['CLOSED']:
                                    # If CLOSED is true then the package
                                    # finished building successfully
                                    fedora_package_version = x['version']
                                    fedora_package_release = x['release']
                                    break
        except koji.GenericError as e:
            if not ignore_missing:
                print(e)
        epel_nvr = (
            str(epel_package_version) +
            '-' +
            str(epel_package_release.split('.')[0])
        )
        fedora_nvr = (
            str(fedora_package_version) +
            '-' +
            str(fedora_package_release.split('.')[0])
        )
        centos_nvr = (
            str(centos_package_version) +
            '-' +
            str(centos_package_release.split('.')[0])
        )
        # if fedora_nvr > centos_nvr:
        # Let's ignore rpm releases for now... We've already enough to do.
        if (str(fedora_package_version) > str(centos_package_version)):
            print(
                '%s may need an update from %s to fedora %s within %s' % (
                    package_name,
                    centos_nvr,
                    fedora_nvr,
                    cbs_tag
                )
            )
        if (str(epel_package_version) > str(centos_package_version)):
            print(
                '%s need an update from %s to epel %s within %s' % (
                    package_name,
                    centos_nvr,
                    epel_nvr,
                    cbs_tag
                )
            )
        else:
            if not ignore_missing:
                if fedora_nvr == '-':
                    print('%s is missing in fedora' % package_name)
                if epel_nvr == '-':
                    print('%s is missing in epel' % package_name)
                if centos_nvr == '-':
                    print('%s is missing in centos' % package_name)
            if verbose and epel_nvr != '-' and centos_nvr != '-':
                print(
                    '%s is ok, we have %s and %s is available\n' % (
                        package_name, centos_nvr, epel_nvr
                    )
                )
            elif verbose and fedora_nvr != '-' and centos_nvr != '-':
                print(
                    '%s is ok, we have %s and %s is available\n' % (
                        package_name, centos_nvr, fedora_nvr
                    )
                )


for tag_to_check in (
    'virt7-ovirt-common-candidate',
    'virt7-ovirt-36-candidate',
    'virt7-ovirt-35-candidate',
    'virt7-kvm-common-candidate',
):
    check_cbs_tag(tag_to_check)
