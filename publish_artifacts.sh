#!/bin/sh

LOCATIONS='src tar
iso iso'

die() {
	local m="${1}"
	echo "FATAL: ${m}" >&2
	exit 1
}

usage() {
	cat << __EOF__
${0} [options]
    --source-repository=SRC_REPO
    --destination-repository=DST_REPO
__EOF__
}

get_opts() {
	while [ -n "${1}" ]; do
		opt="$1"
		v="${opt#*=}"
		shift
		case ${opt} in
			--source-repository=*)
				SRC_REPO=${v}
				;;
			--destination-repository=*)
				DST_REPO=${v}
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
	[ -n "${SRC_REPO}" ] || die "Please specify --source-repository"
	[ -d "${SRC_REPO}" ] || die "Directory ${SRC_REPO} does not exists"
	[ -n "${DST_REPO}" ] || die "Please specify --destination-repository"
	[ "$(find "${SRC_REPO}" -type f | wc -l)" -ne 0 ] || die "Invalid source directory"
}

publish_artifacts() {
	local src_dir="${1}"
	local dst_dir="${2}"

	find "${src_dir}" -name '*.rpm' | while read pkg; do
		pkg_dst_dir="${dst_dir}"
		eval "$(
			rpm -qp --queryformat '
				arch="%{ARCH}"
				release="%{RELEASE}"
				sourcerpm="%{SOURCERPM}"
			' ${pkg}
		)"
		distro="$(echo "${release}" | sed -n 's/.*\.\([a-z][^.]*\)$/\1/gp')"
		if [ -z "${distro}" ]; then
			distro="any"
			pkg_dst_dir="${ANY_DIR}"
		fi

		if [ "${sourcerpm}" = "(none)" ]; then
			dir="${pkg_dst_dir}/rpm/${distro}/SRPMS"
		else
			dir="${pkg_dst_dir}/rpm/${distro}/${arch}"
		fi
		mkdir -p "${dir}"
		mv "${pkg}" "${dir}"
	done

	#
	# copy distro non-specific into all
	# distro repositories
	#
	if [ -d "${ANY_DIR}/rpm/any" ]; then
		for distro in "${dst_dir}/rpm/"*; do
			distro="$(basename "${distro}")"
			for dir in "${ANY_DIR}/rpm/any"/*; do
				arch="$(basename "${dir%*/}")"
				mkdir -p "${dst_dir}/rpm/${distro}/${arch}"
				cp "${ANY_DIR}/rpm/any/${arch}"/* "${dst_dir}/rpm/${distro}/${arch}"
			done
		done
	fi
	echo "${LOCATIONS}" | while IFS=" " read dir suffix; do
		mkdir -p "${dst_dir}/${dir}"
		find "${src_dir}" -regex ".*\.${suffix}\(\|\.gz\|\.bz2\|\.lzma\)$" \
			-exec mv "{}" "${dst_dir}/${dir}" \; || die "Failed to move files"
	done

	for repo in "${dst_dir}"/rpm/*; do
		createrepo -q "${repo}" || die "Cannot create repository under ${repo}"
	done
}

ANY_DIR=""
cleanup() {
	[ -n "${ANY_DIR}" ] && rm -fr "${ANY_DIR}"
}
trap cleanup 0

main() {
	get_opts "${@}"
	validate
	ANY_DIR="$(mktemp -d)"

	publish_artifacts "${SRC_REPO}" "${DST_REPO}"

	return 0
}

main "${@}"
