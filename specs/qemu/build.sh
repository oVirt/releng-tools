#!/bin/bash -e
src="qemu-kvm-rhev-2.1.2-23.el7_1.9.src.rpm"
url="ftp://ftp.redhat.com/pub/redhat/linux/enterprise/7Server/en/RHEV/SRPMS/${src}"
patches=(
    "0001-qemu-kvm-spec-remove-branding.patch"
    "0002-fix-qemu-img-require.patch"
)
# Download the source RPM and extract it
if ! [[ -f "${src}.orig" ]]
then
    wget -O "${src}.orig" "${url}"
fi
rpm2cpio "${src}.orig" | cpio -idmv

cp qemu-kvm.spec qemu-kvm.spec.orig

# Apply patches for qemu re-branding
for patchset in "${patches[@]}" ; do
  patch -p1 < "${patchset}"
done


# Build the source and binary packages:
rpmbuild \
    -bs \
    --define="_sourcedir ${PWD}" \
    --define="_srcrpmdir ${PWD}" \
    --define="_rpmdir ${PWD}" \
    "qemu-kvm.spec"
