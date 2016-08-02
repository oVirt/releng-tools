#!/bin/sh -ex

# The name, version and source of the package:
name="ovirt-engine-nodejs-modules"

# Download the node binaries and extract them to a local directory:
node_version="4.4.6"
node_dir="node-v${node_version}-linux-x64"
node_tar="${node_dir}.tar"
node_url="https://nodejs.org/dist/v${node_version}/${node_tar}"
if [ ! -f "${node_tar}" ]
then
    wget -O "${node_tar}" "${node_url}"
fi
rm -rf "${node_dir}"
tar -xf "${node_tar}"

# Configure the path environment variable so that the node binaries
# installed in the previous step are always used before any other node
# installation that may be available in the system:
export PATH="${PWD}/${node_dir}/bin:${PATH}"

# Clean the local modules directory and run "npm install" to download
# all the dependencies listed in the "package.json" file:
modules_dir="node_modules"
rm -rf "${modules_dir}"
npm cache clean
npm install --no-optional

# Configure the path environment variable so that we can use the
# binaries provided by the modules installed in the previous step:
export PATH="${PWD}/${modules_dir}/.bin:${PATH}"

# Scan the downloaded modules and generate the LICENSES.csv file:
license-checker --csv --out LICENSES.csv

# Prune modules listed as devDependencies from modules directory:
npm prune --production

# Create a tar file out of the modules directory:
modules_tar="${modules_dir}.tar"
tar -cf "${modules_tar}" "${modules_dir}"

# Find the dependencies required by binaries and libraries. Usually this
# is done by RPM itself, but in our case we need to do it explicitly
# because the binaries and libraries aren't part of the %files section
# of the RPM, only the tarball containing them.
requires=$(
    find "${modules_dir}" -type f |
    egrep -v '\.(css|html|js|json|md|txt|yml)$' |
    /usr/lib/rpm/find-requires |
    egrep -v '^$' |
    sed 's|^|Requires: |'
)

# In order to use the calculated dependencies with the "s" command of
# sed, we need to add a backslash before each new line, except for
# the last one:
requires=$(
    echo "${requires}" |
    sed -e '$!s|$|\\|'
)

# Generate the spec from the template:
sed \
    -e "s|@TAR@|${modules_tar}|g" \
    -e "s|@REQUIRES@|${requires}|g" \
    < "${name}.spec.in" \
    > "${name}.spec"

# Build the source and binary packages:
rpmbuild \
    -ba \
    --define="_sourcedir ${PWD}" \
    --define="_srcrpmdir ${PWD}" \
    --define="_rpmdir ${PWD}" \
    "${name}.spec"
