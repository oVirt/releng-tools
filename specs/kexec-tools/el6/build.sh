#!/bin/sh -e

src="kexec-tools-2.0.0-273.el6.src.rpm"
url="http://vault.centos.org/6.5/os/Source/SPackages/${src}"
patches="0001-Add-function-is_pcs_fence_kdump.patch \
         0002-Add-function-get_pcs_cluster_nodes.patch \
         0003-Add-function-setup_cluster_nodes_and_options.patch \
         0004-Add-fence_kdump-support-for-generic-clusters.patch \
         0005-Update-spec.patch"

# Download the source RPM and extract it
if [ ! -f "${src}" ]
then
    wget -O "${src}.orig" "${url}"
fi
rpm2cpio "${src}.orig" | cpio -idmv

# Apply patches for fence_kdump support
for p in ${patches}; do
  patch -p1 < ${p}
done


# Build the source and binary packages:
rpmbuild \
    -bs \
    --define="_sourcedir ${PWD}" \
    --define="_srcrpmdir ${PWD}" \
    --define="_rpmdir ${PWD}" \
    "kexec-tools.spec"
