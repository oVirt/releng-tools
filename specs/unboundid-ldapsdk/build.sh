#!/bin/sh

die() {
	local m="$1"
	echo "FATAL: ${m}" >&2
	exit 1
}

NAME="unboundid-ldapsdk"
VERSION="2.3.7"
REVISION="530"
RPM_RELEASE="0.0.snap.r${REVISION}"
TARBALL="${NAME}-${VERSION}_snap_r${RELEASE}.tar.gz"

SCRIPTDIR="$(dir="$(readlink -f "$(dirname "$0")")" && cd "${dir}" && pwd)"
MYTMP="$(mktemp -d)"
cleanup() {
	[ -n "${MYTMP}" ] && rm -fr "${MYTMP}"
}
trap cleanup 0

rm -rf "${SCRIPTDIR}/noarch" "${SCRIPTDIR}"/*.rpm "${SCRIPTDIR}"/*.tar.*

sed \
	-e "s/@NAME@/${NAME}/g" \
	-e "s/@VERSION@/${VERSION}/g" \
	-e "s/@RPM_RELEASE@/${RPM_RELEASE}/g" \
	-e "s/@TARBALL@/${TARBALL}/g" \
	< "${SCRIPTDIR}/${NAME}.spec.in" \
	> "${MYTMP}/${NAME}.spec"

svn export http://svn.code.sf.net/p/ldap-sdk/code/trunk@530 "${MYTMP}/${NAME}" || die "svn export failed"
rm -fr "${MYTMP}/${NAME}/ext"
tar -C "${MYTMP}" -czf "${TARBALL}" "${NAME}/" || die "tar failed"

rpmbuild \
	-bs \
	--define="_sourcedir ${SCRIPTDIR}" \
	--define="_srcrpmdir ${SCRIPTDIR}" \
	--define="_rpmdir ${SCRIPTDIR}" \
	"${MYTMP}/${NAME}.spec" || die "rpmbuild failed"
