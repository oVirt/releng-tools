#!/bin/bash -e
SUFFIX=".$(date -u +%Y%m%d%H%M)"
make dist
yum-builddep spagobi-dependencies.spec
rpmbuild \
    -bs \
    --define="_sourcedir ${PWD}" \
    --define="_srcrpmdir ${PWD}" \
    --define="_rpmdir ${PWD}" \
    --define="release_suffix ${SUFFIX}" \
    "spagobi-dependencies.spec"
