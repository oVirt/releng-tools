#!/bin/sh -e

# The name, version and source of the package:
name="pthreading"
version="0.1.4"
release="1"
archive="${name}_${version}.orig.tar.gz"
url="https://github.com/oVirt/pthreading/archive/${version}.tar.gz#${name}-${version}.tar.gz"

# Download the source:
wget -O "${archive}" "${url}"
tar xzf "${archive}"

# included debian code is obsolete
rm -rf "${name}-${version}/debian"
cp -r debian "${name}-${version}/"

cd "${name}-${version}"
dpkg-source -b .

sudo -E /usr/sbin/pbuilder build --buildresult ../ ../*.dsc
cd ..
