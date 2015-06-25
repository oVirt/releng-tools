#!/bin/sh -e

# The name, version and source of the package:
name="mom"
version="0.5.1"
release="1"
archive="${name}_${version}.orig.tar.gz"
url="http://resources.ovirt.org/pub/src/${name}/${name}-${version}.tar.gz"

# Download the source:
wget -O "${archive}" "${url}"
tar xzf "${archive}"
cp -r debian "${name}-${version}/"

cd "${name}-${version}"
dpkg-source -b .

sudo -E /usr/sbin/pbuilder build --buildresult ../ ../*.dsc
cd ..
