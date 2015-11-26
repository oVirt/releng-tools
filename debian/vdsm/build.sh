#!/bin/sh -e

# The name, version and source of the package:
name="vdsm"
version="4.17.11"
release="1"
archive="${name}_${version}.orig.tar.gz"
url="http://resources.ovirt.org/pub/ovirt-3.6/src/${name}/${name}-${version}.tar.gz"

rm -rf vdsm-4.17.11

# Download the source:
wget -O "${archive}" "${url}"
tar xzf "${archive}"
cp -r debian "${name}-${version}/"

cd "${name}-${version}"
dpkg-source -b .

sudo -E /usr/sbin/pbuilder build --hookdir ../pbuilder-hooks --buildresult ../ ../*.dsc
cd ..
