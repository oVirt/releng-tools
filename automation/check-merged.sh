#!/bin/bash -xe
[[ -d exported-artifacts ]] || mkdir -p exported-artifacts

if git show --pretty="format:" --name-only | egrep -q "^specs/unboundid.*$"; then
    if [[ "$(rpm --eval "%dist")" == ".el8" ]]; then
        pushd specs/unboundid-ldapsdk
        spectool -g ./unboundid-ldapsdk.spec
        dnf builddep ./unboundid-ldapsdk.spec
        rpmbuild -ba \
            --define="_sourcedir ${PWD}" \
            --define="_srcrpmdir ${PWD}" \
            --define="_rpmdir ${PWD}" \
            "unboundid-ldapsdk.spec"
        popd
        mv specs/unboundid-ldapsdk/*.rpm specs/unboundid-ldapsdk/noarch/*.rpm exported-artifacts/
    fi
fi
