
die() {
	local m="$1"
	echo "FATAL: ${m}" >&2
	exit 1
}

common_iterate() {
	local perconf="$1"
	local perfile="$2"

	find conf.d -name '*.conf' | sort | while read c; do
		(
			. "${c}"

			echo "${DESCRIPTION}" >&2

			${perconf}

			urlindex=0
			while true; do
				eval url="\${URL${urlindex}}"
				eval sha1sum="\${SHA1SUM${urlindex}}"
				eval extract="\${EXTRACT${urlindex}}"
				eval artifact="\${ARTIFACT${urlindex}}"
				[ -z "${url}" ] && break

				${perfile}

				urlindex="$((${urlindex}+1))"
			done
		) || exit 1
	done || exit 1
}

common_calc_sha1sum() {
	local f="$1"
	sha1sum "${f}" | sed 's/ .*//'
}

common_check_sha1sum() {
	local f="$1"
	local sha1sum="$2"

	[ "${sha1sum}" = "$(common_calc_sha1sum "${f}")" ]
}

common_void() {
	return 0
}
