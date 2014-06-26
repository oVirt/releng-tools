#!/bin/sh -e

src="kexec-tools-2.0.4-32.el7.src.rpm"
url="http://buildlogs.centos.org/c7.00.04/kexec-tools/20140612172704/2.0.4-32.el7.x86_64/${src}"
patches="0001-Rename-FENCE_KDUMP_CONFIG-to-FENCE_KDUMP_CONFIG_FILE.patch \
         0002-Rename-FENCE_KDUMP_NODES-to-FENCE_KDUMP_NODES_FILE.patch \
         0003-Rename-is_fence_kdump-to-is_pcs_fence_kdump.patch \
         0004-Rename-kdump_check_fence_kdump-to-kdump_configure_fe.patch \
         0005-Rename-check_fence_kdump-to-check_pcs_fence_kdump.patch \
         0006-Add-get_option_value.patch \
         0007-Add-fence_kdump-support-for-generic-clusters.patch \
         0008-Update-spec.patch"

# Download the source RPM and extract it
if [ ! -f "${src}" ]
then
    wget -O "${src}" "${url}"
fi
rpm2cpio ${src} | cpio -idmv

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
