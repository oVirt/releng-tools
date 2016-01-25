#!/bin/sh

. ./common.sh

docmatrix() {
	cat >> "${TMPCOPYING}" << __EOF__
 - ${NAME}-${VERSION}
__EOF__
}

docconfig() {
	local title="${DESCRIPTION} (${NAME})"
	local dash="-------------------------------------------------------------------------------------------------"

	cat >> "${TMPCOPYING}" << __EOF__

${title}
$(expr substr "${dash}" 1 ${#title})
Site:      ${HOME}
License:   ${LICENSE}${COPYRIGHT:+
Copyright: ${COPYRIGHT}${COPYRIGHT_NOTE}}
Version:   ${VERSION}
Files:
__EOF__
}

docfile() {
	cat >> "${TMPCOPYING}" << __EOF__
    $(basename "${url}")
__EOF__
}

COPYING="$1"
[ -n "${COPYING}" ] || die "Invalid usage"
TMPCOPYING="${COPYING}.tmp"

rm -f "${COPYING}" "${TMPCOPYING}"
cat > "${TMPCOPYING}" << __EOF__
Spago BI 3rd party dependencies
===============================

spagobi-dependencies package is a bundle of 3rd party dependencies for SpagoBI.

Bundle contains the following components:
__EOF__
common_iterate docmatrix common_void
common_iterate docconfig docfile
mv "${TMPCOPYING}" "${COPYING}"
