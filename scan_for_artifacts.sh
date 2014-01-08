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
    --repository-path=REPO_PATH
    --artifacts-source=SRC_DIR
    --repository-version=REPO_VERSION
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
			--repository-version=*)
				REPO_VERSION=${v}
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
	[ -n "${REPO_VERSION}" ] || die "Please specify --repository-version"
	[ -d "${SRC_DIR}" ] || die "Directory ${SRC_DIR} does not exists"
	[ -d "${REPO_PATH}" ] || die "Directory ${REPO_PATH} does not exists"
}

scan_for_artifacts() {
	find "${SRC_DIR}" -maxdepth 1 -type d -name '*.ready' | while read dir; do
		"${SCRIPTDIR}/publish_artifacts.sh" --source-repository="${dir}" \
				--destination-repository="${REPO_PATH}/${REPO_VERSION}" \
				|| die "Cannot publish artifacts for ${dir}"

		[ "$(find "${SRC_DIR}" -type f | wc -l)" -eq 0 ] \
			|| die "We still have files under ${SRC_DIR}. Please recheck"
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
