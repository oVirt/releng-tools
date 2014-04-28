#!/bin/bash

## Copyright (C) 2014 Red Hat, Inc., Kiril Nesenko <knesenko@redhat.com>
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

SCRIPTDIR="$(dirname "${0}")"
REPO_PATH="/var/www/html/pub"

die() {
	local msg="${1}"
	echo "FATAL: ${msg}"
	exit 1
}

usage() {
	cat << __EOF__
    ${0} [options]
    --conf-file=               - configuration file
    --output-directory=        - tmp directory where to download pkgs
    --destination-repository   - destination repository
    --sources-destination=     - destination for sources

    CONF_FILE
    The configuration file must be a plain text file with one package
    or url on each line.

    URL DEFINITION
    The url must be a canonical http/https url that must contain
    the links to the packages (not the link to the package directly).
    In the case of koji, the url can be a the first level task
    that links to to the tasks that created the packages (for example
    http://koji.fedoraproject.org/koji/taskinfo?taskID=6397141).


    PACKAGE DEFINITON
    The package definition is a reference to an already existing
    package on previous repository, from the ones under $REPO_PATH
    For example:

    3.3:ovirt-engine-3.3.0-1

    that will get all the packages that have ovirt-engine-3.3.0-1
    on their name from $REPO_PATH/3.3 and add them to the new repo.


    CONFIGURATION EXAMPLE
    http://jenkins.ovirt.org/job/manual-build-tarball/130/
    http://jenkins.ovirt.org/job/manual-build-tarball/130/
    http://koji.fedoraproject.org/koji/taskinfo?taskID=6279142
    3.3:ovirt-engine-3.3.0-1
__EOF__
}

get_opts() {
	while [[ -n "${1}" ]]; do
		opt="${1}"
		val="${opt#*=}"
		shift
		case "${opt}" in
			--conf-file=*)
				CONF_FILE="${val}"
				;;
			--output-directory=*)
				OUTPUT_DIR="${val}"
				;;
			--destination-repository=*)
				DST_REPO="${val}"
				;;
			--sources-destination=*)
				SOURCES_DST="${val}"
				;;
			--help|-h)
				usage
				exit 0
				;;
			*)
				die "Wrong option"
				;;
		esac
	done
	return 0
}

validation() {
	[[ -n "${CONF_FILE}" ]] || die "Please specify --conf-file= option"
	[[ -f "${CONF_FILE}" ]] || die "Cannot find configuration file"
	[[ -n "${OUTPUT_DIR}" ]] || die "Please specify --output-directory= option"
	[[ "${OUTPUT_DIR}" != "/" ]] || die "--output-directory= can not be /"
	[[ -n "${DST_REPO}" ]] || die "Please specify --destination-repository= option"
	[[ -e "${OUTPUT_DIR}" ]] && die "${OUTPUT_DIR} should not exist"
	[[ -e "${OUTPUT_DIR}" ]] || mkdir -p "${OUTPUT_DIR}"
	return 0
}

get_packages_from_koji_2lvl() {
	local url="${1?}"
	local builds=($(wget -q -O - "${url}" \
                    | grep -Po '(?<=href=")[^"]+(?=.*(buildArch|buildSRPM))' \
                    | sort | uniq))
	local path_url="${url#*//*/koji/}"
	local base_url="${url:0:$((${#url}-${#path_url}))}"
	for build in "${builds[@]}"; do
		for package in $(wget -q -O - "${base_url}${build}" \
							| grep -Po '(?<=href=")[^"]+\.(iso|rpm|tar.gz)' \
							| sort | uniq); do
			echo "${package}"
		done
	done
}

get_packages_from_jenkins_2lvl() {
	local url="${1?}"
	local builds json_data parse_json
	json_data="$(wget -q -O - "${url}/api/json?pretty=true")"
	parse_json="
import json
import sys
def get_parents(run):
    parents=[]
    for action in run['actions']:
        if 'causes' in action:
            for cause in action['causes']:
                if 'upstreamBuild' in cause:
                    parents.append(cause['upstreamBuild'])
    return parents
res=json.loads(sys.stdin.read())
for run in res['runs']:
    url=run['url']
    if res['number'] not in get_parents(run):
        continue
    for artifact in run['artifacts']:
        print '%s/artifact/%s' % (url, artifact['relativePath'])
"
	echo "${json_data}" | python -c "${parse_json}"
}

download_package() {
	local url="${1?}"
	local dst_dir="${2?}"
	local failed=false
	local packages package labels
	echo
	echo "Downloading packages from ${url} to ${dst_dir}"

	pushd "${dst_dir}" >& /dev/null

	#
	# Handle jenkins builds with configuration (labels)
	#

	packages=($(wget -q -O - "${url}" | grep -Po '(?<=href=")[^"]+\.(iso|rpm|tar.gz)' | sort | uniq))

	#
	# Handle koji 2level pages
	#
	if [[ "${#packages[@]}" -eq 0 ]]; then
		case "${url}" in
			*koji*)
				packages=($(get_packages_from_koji_2lvl "${url}"))
				;;
			*jenkins*)
				packages=($(get_packages_from_jenkins_2lvl "${url}"))
				;;
		esac
	fi

	for package in "${packages[@]}"; do
		## handle relative links
		[[ "${package}" =~ ^http.*$ ]] \
			|| package="${url}/${package}"
		wget -qnc "${package}" || die "Cannot download pkgs ${package}"
		echo "Got package ${package}"
	done

	popd >& /dev/null
}

copy_pkg() {
	local conf_param="${1?}"
	local output_dir="${2?}"
	local pkg_dir="${conf_param%%:*}"
	local pkg_name="${conf_param#*:}"

	find "${pkg_dir}" -type f -name "${pkg_name}*" | while read pkg; do
		cp "${pkg}" "${output_dir}/${pkg##*/}"
	done
}

download_pkgs() {
	cat "${CONF_FILE}" | while read url; do
		if [[ "${url}" =~ ^http ]]; then
			download_package "${url}" "${OUTPUT_DIR}"
		else
			copy_pkg "${url}" "${OUTPUT_DIR}"
		fi
	done
}

publish_artifacts() {
	local src_dir="${1?}"
	local dst_dir="${2?}"

	local opts="--source-repository=${src_dir} --destination-repository=${dst_dir}"
	[[ -z "${SOURCES_DST}" ]] || opts="${opts} --sources-destination=${SOURCES_DST}"
	"${SCRIPTDIR}/publish_artifacts.sh" ${opts}
}

clean() {
	rm -rf "${OUTPUT_DIR}"
}

main() {
	get_opts "${@}"
	validation

	download_pkgs
	publish_artifacts "${OUTPUT_DIR}" "${DST_REPO}"

	clean
}

main "${@}"
