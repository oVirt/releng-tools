#!/bin/sh -e

# The name, version and source of the package:
name="ovirt-engine-jboss-as"
version="7.1.1"
src="jboss-as-${version}.Final.zip"
url="http://download.jboss.org/jbossas/7.1/jboss-as-${version}.Final/${src}"

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
    --define="_rpmfilename %{name}-%{version}-%{release}.%{arch}.rpm" \
    "${name}.spec"
