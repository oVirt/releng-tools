#!/bin/sh

. ./common.sh

download() {
	local dst="${DOWNLOADS}/$(basename "${url}")"
	echo "${dst}" >> "${TMPDOWNLOADS_LIST}"

	if ! [ -e "${dst}" ] || ! common_check_sha1sum "${dst}" "${sha1sum}"; then
		curl -L "${url}" > "${dst}" || die "Cannot download ${url}"
		common_check_sha1sum "${dst}" "${sha1sum}" || die "Invalid sha1sum ${dst} $(common_calc_sha1sum "${dst}")"
	fi
}

DOWNLOADS="$1"
DOWNLOADS_LIST="${DOWNLOADS}/downloads.list"
[ -n "${DOWNLOADS}" ] || die "Invalid usage"
TMPDOWNLOADS_LIST="${DOWNLOADS_LIST}.tmp"

mkdir -p "${DOWNLOADS}"
rm -f "${DOWNLOADS_LIST}" "${TMPDOWNLOADS_LIST}"
common_iterate common_void download
mv "${TMPDOWNLOADS_LIST}" "${DOWNLOADS_LIST}"
