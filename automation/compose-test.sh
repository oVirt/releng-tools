#!/bin/bash -xe
[[ -d exported-artifacts ]] || mkdir -p exported-artifacts
[[ -d compose-test ]] || mkdir -p compose-test

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
