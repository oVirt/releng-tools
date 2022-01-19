#!/bin/bash -xe
mkdir -p exported-artifacts

git show --pretty=format: --name-only

if git show --pretty="format:" --name-only | grep -E -q "^milestones/.*conf$"; then
    for config_file in $(git show --pretty="format:" --name-only | grep -E "^milestones/.*conf$")
    do
        if [[ -e "${config_file}" ]] ; then
            python3 automation/check-milestone-previous.py "${config_file}"
            release=$(basename "${config_file/.conf/}")
            ./release_notes_git.py --contrib-project-list "${release}" > "exported-artifacts/${release}_notes.md"
        else
            echo "Skipping ${config_file} since it has been removed."
        fi
    done
fi
