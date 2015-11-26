#!/bin/sh -e

# The name, version and source of the package:
name="ioprocess"
version="0.15.0"
release="1"
archive="${name}_${version}.orig.tar.gz"
url="http://resources.ovirt.org/pub/src/${name}/${name}-${version}.tar.gz"


# Download the source:
wget -O "${archive}" "${url}"
tar xzf "${archive}"
cp -r debian "${name}-${version}/"

cd "${name}-${version}"
dpkg-source -b .

sudo -E /usr/sbin/pbuilder build --hookdir ../pbuilder-hooks --buildresult ../ ../*.dsc
cd ..
