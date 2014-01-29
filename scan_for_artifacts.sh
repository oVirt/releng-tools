#!/bin/sh

SCRIPTDIR="$(dirname "$0")"

die() {
	local m="${1}"
	echo "FATAL: ${m}" >&2
	exit 1
}

usage() {
	cat << __EOF__
${0} [options]
    --repository-path=REPO_PATH    where to publish rpms
    --artifacts-source=SRC_DIR     from where to take rpms
__EOF__
}

get_opts() {
	while [ -n "${1}" ]; do
		opt="$1"
		v="${opt#*=}"
		shift
		case ${opt} in
			--repository-path=*)
				REPO_PATH=${v}
				;;
			--artifacts-source=*)
				SRC_DIR=${v}
				;;
			--help)
				usage
				exit 0
				;;
			*)
				usage
				die "Wrong option"
				;;
		esac
	done
}

validate() {
	[ -n "${REPO_PATH}" ] || die "Please specify --repository-path"
	[ -n "${SRC_DIR}" ] || die "Please specify --artifacts-source"
	[ -d "${SRC_DIR}" ] || die "Directory ${SRC_DIR} does not exists"
	[ -d "${REPO_PATH}" ] || die "Directory ${REPO_PATH} does not exists"
}

scan_for_artifacts() {
	find "${SRC_DIR}" -maxdepth 1 -mindepth 1 -type d -name '*.ready' | while read dir; do
		repo_version="$(basename "${dir}")"
		repo_version="${repo_version%.*}"
		"${SCRIPTDIR}/publish_artifacts.sh" --source-repository="${dir}" \
				--destination-repository="${REPO_PATH}/${repo_version}" \
				|| die "Cannot publish artifacts for ${dir}"

		[ "$(find "${dir}" -type f | wc -l)" -eq 0 ] \
			|| die "We still have files under ${dir}. Please recheck"
		rm -rf "${dir}"
	done || die "Failed inside the loop"
}

main() {
	get_opts "${@}"
	validate

	scan_for_artifacts

	return 0
}

main "${@}"
