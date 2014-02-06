#!/bin/sh -e

# The name, version and source of the package:
name="sos"
version="3.1"
src="${name}-${version}.tar.gz"
url="git://github.com/sosreport/sosreport.git"
githash="a96a5e8"

# Download the source:
if [ ! -f "${src}" ]
then
    git clone git://github.com/sosreport/sosreport.git
    pushd sosreport
    git checkout $githash
    make "${src}"
    cp  "dist-build/${src}" ../
    popd
fi

# Generate the spec from the template:
sed \
    -e "s/@VERSION@/${version}/g" \
    -e "s/@SRC@/${src}/g" \
    -e "s/@GITHASH@/${githash}/g" \
    < "${name}.spec.in" \
    > "${name}.spec"

# Build the source and binary packages:
rpmbuild \
    -ba \
    --define="_sourcedir ${PWD}" \
    --define="_srcrpmdir ${PWD}" \
    --define="_rpmdir ${PWD}" \
    --define="_rpmfilename %{name}-%{version}-%{release}.%{arch}.rpm" \
    "${name}.spec"
