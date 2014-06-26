#!/bin/sh -e

spectool --get-files --sources sos.spec
rpmbuild \
    -ba \
    --define="_sourcedir ${PWD}" \
    --define="_srcrpmdir ${PWD}" \
    --define="_rpmdir ${PWD}" \
    sos.spec
