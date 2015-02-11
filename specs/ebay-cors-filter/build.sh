#!/bin/sh -e

# The name, version and source of the package:
name="ebay-cors-filter"
version="1.0.1"
src="cors-filter-${version}.tar.gz"
url="https://github.com/eBay/cors-filter/archive/${src}"
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
    -bs \
    --define="_sourcedir ${PWD}" \
    --define="_srcrpmdir ${PWD}" \
    --define="_rpmdir ${PWD}" \
    --define="_rpmfilename %{name}-%{version}-%{release}.%{arch}.rpm" \
    "${name}.spec"
