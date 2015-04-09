#!/bin/bash -e

spectool --get-files --sources jasperreports-server.spec

# Build the source package:
rpmbuild \
    -bs \
    --define="_sourcedir ${PWD}" \
    --define="_srcrpmdir ${PWD}" \
    --define="_rpmdir ${PWD}" \
    "jasperreports-server.spec"
