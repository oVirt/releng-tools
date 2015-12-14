#!/bin/sh -ex

# The name of the package:
name="rubygem-libxml-ruby"

# Download the sources:
spectool --get-files "${name}.spec"

# Build the source and binary packages:
rpmbuild \
    -bs \
    --define="_sourcedir ${PWD}" \
    --define="_srcrpmdir ${PWD}" \
    --define="_rpmdir ${PWD}" \
    --define="_rpmfilename %{name}-%{version}-%{release}.%{arch}.rpm" \
    "${name}.spec"
