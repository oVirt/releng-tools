#!/bin/bash -xe
[[ -d exported-artifacts ]] || mkdir -p exported-artifacts

if git show --pretty="format:" --name-only | egrep -q "^releases/.*conf$"; then
    for config_file in `git show --pretty="format:" --name-only | egrep "^releases/.*conf$"`
    do
        repoman exported-artifacts add conf:"${config_file}"
    done
    if [[ -n `find exported-artifacts -name "*.git*.rpm" | grep -v ovirt-release` ]] ; then
        echo "RPMs with git hash in NVR are not allowed within releases" >&2
        exit 1
    fi
fi


if git show --pretty="format:" --name-only | egrep -q "^milestones/.*conf$"; then
    for config_file in `git show --pretty="format:" --name-only | egrep "^milestones/.*conf$"`
    do
        release=`basename "${config_file/.conf/}"`
        ./release_notes_git.py "${release}" > "exported-artifacts/${release}_notes.md"
    done
fi
