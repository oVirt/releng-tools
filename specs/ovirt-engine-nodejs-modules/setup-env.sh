#!/bin/sh -ex

# This script can be used to set up Node.js environment
# and link npm dependencies to ./node_modules directory.

# To use this script, source it to ensure that exported
# environment variables take effect:
#   source /usr/share/ovirt-engine-nodejs-modules/setup-env.sh
# or using dot syntax:
#   . /usr/share/ovirt-engine-nodejs-modules/setup-env.sh

# Make sure that we use our Node.js installation:
export PATH="/usr/share/ovirt-engine-nodejs/bin:${PATH}"

# Link the Node.js dependencies to the local "node_modules" directory:
ln -s "/usr/share/ovirt-engine-nodejs-modules/node_modules"
export PATH="./node_modules/.bin:${PATH}"
