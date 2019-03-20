#!/bin/bash

## Copyright (C) 2014 Red Hat, Inc., Kiril Nesenko <knesenko@redhat.com>
## Copyright (C) 2015 Red Hat, Inc., Sandro Bonazzola <sbonazzo@redhat.com>
### This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.


#TODO:
# * use df to check space on the server
# * Implement:
#   - move rpms in a temp dir
#   - createrepo on the snapshot
#   - repoclosure on the snapshot
#   - if success, remove tempdir
#   - else: restore and send an email to infra.

die() {
	local m="${1}"
	echo "FATAL: ${m}" >&2
	exit 1
}

usage() {
	cat << __EOF__
    ${0} [options]
    --days=DAYS_TO_KEEP            days to keep

    Example:
    ${0} --days=4 /var/www/html/pub/ovirt-*-snapshot
__EOF__
}

get_opts() {
	while [ -n "${1}" ]; do
		opt="$1"
		v="${opt#*=}"
		case ${opt} in
			--days=*)
				DAYS_TO_KEEP="${v}"
				;;
			--help)
				usage
				exit 0
				;;
			--)
				break
				;;
			-*)
				die "Invalid usage"
				;;
			*)
				break
				;;
		esac
		shift
	done
	REPO_PATH=("${@}")
}

validate() {
	[ -n "${DAYS_TO_KEEP}" ] || die "Please specify --days"
}

clean_pkgs() {
	for snapshot in "${REPO_PATH[@]}"; do
		echo "Cleaning ${snapshot}"
		find "${snapshot}" -type f -mtime +"${DAYS_TO_KEEP}" ! -name "*.xml" -exec rm -f -v {} \;
		repoman "${snapshot}" createrepo || die "Cannot createrepo for ${snapshot}"
	done
}

main() {
	get_opts "${@}"
	validate

	clean_pkgs
}

main "${@}"
