#!/bin/sh

. ./common.sh

installartifact() {
	local dst="${DOWNLOADS}/$(basename "${url}")"
	local out

	common_check_sha1sum "${dst}" "${sha1sum}" || die "Invalid sha1sum ${dst}"
	if [ -n "${extract}" ]; then
		set ${extract}
		if [ "$2" = "->" ]; then
			extract="$1"
			out="${JAVADIR}/$3"
		else
			out="${JAVADIR}/$(basename "$1")"
		fi
		if [ "${dst%.zip}" != "${dst}" ]; then
			unzip -p "${dst}" "${extract}" > "${out}" || die "Cannot extract '${extract}'"
		else
			tar -xf "${dst}" --to-stdout "${extract}" > "${out}" || die "Cannot extract '${extract}'"
		fi
		chmod 0644 "${out}"
	else
        filename="$(basename "${dst}")"

        if [ ${filename: -4} == ".pom" ] ; then
            out="${POMDIR}/$(basename "${dst}")"
        else
            out="${JAVADIR}/$(basename "${dst}")"
		fi
		install -m 0644 "${dst}" "${out}" || die "Cannot install '${dst}'"
	fi
	local v
	for v in ${SPAGOBI_VERSIONS}; do
		install -m 0755 -d "${JAVADIR}/${v}" || die "Cannot create version directory '${v}'"
		if [ "${artifact: -4}" == ".jar" ] ; then
            rm -f "${JAVADIR}/${v}/${artifact}"
            ln -s "../$(basename "${out}")" "${JAVADIR}/${v}/${artifact}" || die "Cannot link '${artifact}'"
        fi
	done
}

DOWNLOADS="$1"
JAVADIR="$2"
POMDIR="$3"
[ -n "${JAVADIR}" ] || die "Invalid usage"
[ -n "${POMDIR}" ] || die "Invalid usage"
install -m 0755 -d "${JAVADIR}"
common_iterate common_void installartifact
