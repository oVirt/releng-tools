#!/bin/bash -xe
[[ -d exported-artifacts ]] || mkdir -p exported-artifacts
[[ -d compose-test ]] || mkdir -p compose-test

if git show --pretty="format:" --name-only | grep -E -q "^milestones/.*conf$"; then
    for config_file in $(git show --pretty="format:" --name-only | grep -E "^milestones/.*conf$")
    do
        if [[ -e "${config_file}" ]] ; then
            python3 automation/check-milestone-previous.py "${config_file}"
            release=$(basename "${config_file/.conf/}")
            ./release_notes_git.py "${release}" > "exported-artifacts/${release}_notes.md"
        else
            echo "Skipping ${config_file} since it has been removed."
        fi
    done
fi
