#!/bin/bash -xe
[[ -d exported-artifacts ]] || mkdir -p exported-artifacts

if git show --pretty="format:" --name-only | egrep -q "^releases/.*conf$"; then
    for config_file in `git show --pretty="format:" --name-only | egrep "^releases/.*conf$"`
    do
        if [[ -e "${config_file}" ]] ; then
            repoman exported-artifacts add conf:"${config_file}"
            if [[ "${config_file}" =~ "alpha" ]] || [[ "${config_file}" =~ "beta" ]]; then
                echo "Skipping git hash test being pre-release compose"
            else
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
