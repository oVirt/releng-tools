#!/bin/sh -e

# The name, version and source of the package:
name="ioprocess"
version="0.15.0.4"
tag="0.15.0-4"
release="1"
archive="${name}_${version}.orig.tar.gz"
url="https://github.com/oVirt/${name}/archive/v${tag}.tar.gz"
# url="http://resources.ovirt.org/pub/src/${name}/${name}-${version}.tar.gz"


# Download the source:
wget -O "${archive}" "${url}"
tar xzf "${archive}"
rm -rf "${name}-${tag}/debian"
cp -r debian "${name}-${tag}/"

cd "${name}-${tag}"
dpkg-source -b .

sudo -E /usr/sbin/pbuilder build --hookdir ../pbuilder-hooks --buildresult ../ ../*.dsc
cd ..
