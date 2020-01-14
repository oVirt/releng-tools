#!/bin/bash -xe
[[ -d exported-artifacts ]] || mkdir -p exported-artifacts
[[ -d compose-test ]] || mkdir -p compose-test

if [[ ! "$(rpm --eval "%dist")" == ".el8" ]]; then
    # Repoman is missing on el8
    if git show --pretty="format:" --name-only | egrep -q "^releases/.*conf$"; then
        for config_file in `git show --pretty="format:" --name-only | egrep "^releases/.*conf$"`
        do
            if [[ -e "${config_file}" ]] ; then
                if [[ "${config_file}" =~ "alpha" ]] || [[ "${config_file}" =~ "beta" ]]; then
                    # Not archiving composed repository to save time during 4.3 mass import
                    repoman compose-test add conf:"${config_file}"
                    echo "Skipping git hash test being pre-release compose"
                else
                    repoman exported-artifacts add conf:"${config_file}"
                    if [[ -n `find exported-artifacts -name "*.git*.rpm"` ]] ; then
                        echo "RPMs with git hash in NVR are not allowed within releases" >&2
                        exit 1
                    fi
                fi
            else
                echo "Skipping ${config_file} since it has been removed."
            fi
        done
    fi
fi

if git show --pretty="format:" --name-only | egrep -q "^milestones/.*conf$"; then
    for config_file in `git show --pretty="format:" --name-only | egrep "^milestones/.*conf$"`
    do
        if [[ -e "${config_file}" ]] ; then
            python3 automation/check-milestone-previous.py ${config_file}
            release=`basename "${config_file/.conf/}"`
            ./release_notes_git.py "${release}" > "exported-artifacts/${release}_notes.md"
        else
            echo "Skipping ${config_file} since it has been removed."
        fi
    done
fi

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
