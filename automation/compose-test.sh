#!/bin/bash -xe
mkdir -p compose-test

if git show --pretty="format:" --name-only | grep -E -q "^releases/.*conf$"; then
    for config_file in $(git show --pretty="format:" --name-only | grep -E "^releases/.*conf$")
    do
        if [[ -e "${config_file}" ]] ; then
            if [[ "${config_file}" =~ "alpha" ]] || [[ "${config_file}" =~ "beta" ]]; then
                # Not archiving composed repository to save time during 4.3 mass import
                repoman compose-test add conf:"${config_file}"
                echo "Skipping git hash test being pre-release compose"
            else
                repoman compose-test add conf:"${config_file}"
                if [[ -n $(find compose-test -name "*.git*.rpm") ]] ; then
                    echo "RPMs with git hash in NVR are not allowed within releases" >&2
                    exit 1
                fi
            fi
        else
            echo "Skipping ${config_file} since it has been removed."
        fi
    done
fi
