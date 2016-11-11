#!/bin/sh -e

# The name, version and source of the package:
name="ovirt-engine-nodejs"
version="6.9.1"
src="node-v${version}-linux-x64.tar.xz"
url="https://nodejs.org/dist/v${version}/node-v${version}-linux-x64.tar.xz"

# Download the source:
if [ ! -f "${src}" ]
then
    wget -O "${src}" "${url}"
fi

# Generate the spec from the template:
sed \
    -e "s/@VERSION@/${version}/g" \
    -e "s/@SRC@/${src}/g" \
    < "${name}.spec.in" \
    > "${name}.spec"

# Build the source and binary packages:
rpmbuild \
    -ba \
    --define="_sourcedir ${PWD}" \
    --define="_srcrpmdir ${PWD}" \
    --define="_rpmdir ${PWD}" \
    "${name}.spec"
