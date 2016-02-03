#!/bin/bash -e

make dist
yum-builddep spagobi-dependencies.spec
rpmbuild \
    -bs \
    --define="_sourcedir ${PWD}" \
    --define="_srcrpmdir ${PWD}" \
    --define="_rpmdir ${PWD}" \
    --define="_rpmfilename %{name}-%{version}-%{release}.%{arch}.rpm" \
    "spagobi-dependencies.spec"
