#!/bin/sh -e

# The name, version and source of the package:
name="safelease"
version="1.0"
release="1"
archive="${name}_${version}.orig.tar.gz"
url="https://bronhaim.fedorapeople.org/${name}-${version}.tar.gz"


# Download the source:
wget -O "${archive}" "${url}"
tar xzf "${archive}"
cp -r debian "${name}-${version}/"

cd "${name}-${version}"
dpkg-source -b .

sudo -E /usr/sbin/pbuilder build --buildresult ../ ../*.dsc
cd ..
