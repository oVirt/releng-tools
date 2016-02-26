#!/bin/bash -e
make dist
yum-builddep spagobi-dependencies.spec
rpmbuild \
    -bs \
    --define="_sourcedir ${PWD}" \
    --define="_srcrpmdir ${PWD}" \
    --define="_rpmdir ${PWD}" \
    "spagobi-dependencies.spec"
