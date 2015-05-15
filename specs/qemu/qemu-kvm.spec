# Build time setting
%define rhev 1

%if %{rhev}
    %bcond_with     guest_agent     # disabled
%else
    %bcond_without  guest_agent     # enabled
%endif

%global SLOF_gittagdate 20140630

%global have_usbredir 1
%global have_spice    1
%global have_fdt      0
%global have_gluster  1
%global have_kvm_setup 0

%ifarch %{ix86} x86_64
    %global have_seccomp 1
%else
    %global have_usbredir 0
    %global have_seccomp 0
%endif

%ifnarch s390 s390x
    %global have_librdma 1
%endif

%ifarch %{ix86}
    %global kvm_target    i386
%endif
%ifarch x86_64
    %global kvm_target    x86_64
%else
    %global have_spice   0
    %global have_gluster 0
%endif
%ifarch %{power64}
    %global kvm_target    ppc64
    %global have_fdt     1
    %global have_kvm_setup 1
%endif
%ifarch s390x s390
    %global kvm_target    s390x
%endif
%ifarch ppc
    %global kvm_target    ppc
    %global have_fdt     1
%endif
%ifarch aarch64
    %global kvm_target    aarch64
    %global have_fdt     1
%endif

#Versions of various parts:

%define pkgname qemu-kvm
%define rhel_suffix -rhel
%define rhev_suffix -rhev

# Setup for RHEL/RHEV package handling
# We need to define tree suffixes:
# - pkgsuffix:             used for package name
# - extra_provides_suffix: used for dependency checking of other packages
# - conflicts_suffix:      used to prevent installation of both RHEL and RHEV

%if %{rhev}
    %global pkgsuffix %{rhev_suffix}
    %global extra_provides_suffix %{nil}
    %global conflicts_suffix %{rhel_suffix}
    %global obsoletes_version 15:0-0
%else
    %global pkgsuffix %{nil}
    %global extra_provides_suffix %{rhel_suffix}
    %global conflicts_suffix %{rhev_suffix}
%endif

# Macro to properly setup RHEL/RHEV conflict handling
%define rhel_rhev_conflicts()                                         \
Conflicts: %1%{conflicts_suffix}                                      \
Provides: %1%{extra_provides_suffix} = %{epoch}:%{version}-%{release} \
    %if 0%{?obsoletes_version:1}                                          \
Obsoletes: %1 < %{obsoletes_version}                                      \
    %endif

Summary: QEMU is a FAST! processor emulator
Name: %{pkgname}%{?pkgsuffix}
Version: 2.1.2
Release: 23%{?dist}_1.3
# Epoch because we pushed a qemu-1.0 package. AIUI this can't ever be dropped
Epoch: 10
License: GPLv2+ and LGPLv2+ and BSD
Group: Development/Tools
URL: http://www.qemu.org/
# RHEV will build Qemu only on x86_64:
%if %{rhev}
ExclusiveArch: x86_64 %{power64} aarch64
%endif
%ifarch %{ix86} x86_64
Requires: seabios-bin >= 1.7.5-1
Requires: sgabios-bin
%endif
%ifnarch aarch64
Requires: seavgabios-bin
%endif
%ifarch %{power64}
Requires: SLOF = 20140630
%endif
Requires: ipxe-roms-qemu
Requires: %{pkgname}-common%{?pkgsuffix} = %{epoch}:%{version}-%{release}
        %if 0%{have_seccomp}
Requires: libseccomp >= 1.0.0
        %endif
# For compressed guest memory dumps
Requires: lzo snappy
%if 0%{have_gluster}
Requires: glusterfs-api >= 3.6.0
%endif
%if 0%{have_kvm_setup}
Requires(post): systemd-units
    %ifarch %{power64}
Requires: powerpc-utils
    %endif
%endif

# OOM killer breaks builds with parallel make on s390(x)
%ifarch s390 s390x
    %define _smp_mflags %{nil}
%endif

Source0: http://wiki.qemu.org/download/qemu-%{version}.tar.bz2

Source1: qemu.binfmt
# Loads kvm kernel modules at boot
# Not needed anymore - required only for kvm on non i86 archs 
# where we do not ubuild kvm
# Source2: kvm.modules
# Creates /dev/kvm
Source3: 80-kvm.rules
# KSM control scripts
Source4: ksm.service
Source5: ksm.sysconfig
Source6: ksmctl.c
Source7: ksmtuned.service
Source8: ksmtuned
Source9: ksmtuned.conf
Source10: qemu-guest-agent.service
Source11: 99-qemu-guest-agent.rules
Source12: bridge.conf
Source13: qemu-ga.sysconfig
Source14: rhel6-virtio.rom
Source15: rhel6-pcnet.rom
Source16: rhel6-rtl8139.rom
Source17: rhel6-ne2k_pci.rom
Source18: bios-256k.bin
Source19: README.rhel6-gpxe-source
Source20: rhel6-e1000.rom
Source21: kvm-setup
Source22: kvm-setup.service
Source23: 85-kvm.preset

# For bz#903914 - Disable or remove usb related devices that we will not support
Patch1: kvm-Disable-unsupported-usb-devices.patch
# For bz#903918 - Disable or remove emulated SCSI devices we will not support
Patch2: kvm-Disable-unsupported-emulated-SCSI-devices.patch
# For bz#921971 - Disable or remove other emulated devices that we will not support
Patch3: kvm-Disable-various-unsupported-devices.patch
# For bz#921974 - Disable or remove emulated audio devices that we will not support
Patch4: kvm-Disable-unsupported-audio-devices.patch
# For bz#921974 - Disable or remove emulated audio devices that we will not support
Patch5: kvm-Disable-unsupported-emulated-network-devices.patch
# For bz#906185 - kvm is not enabled by default on rhel7 qemu-kvm, but it is on rhel6 one otherwise
Patch6: kvm-Use-kvm-by-default.patch
# For bz#947441 - HPET device must be disabled
Patch7: kvm-Disable-HPET-device.patch
# For bz#893318 - 'man qemu' should be replaced by "man qemu-kvm"
Patch8: kvm-Rename-man-page-qemu-1-to-qemu-kvm-1.patch
Patch9: kvm-Change-qemu-to-qemu-kvm.patch
# For bz#977864 - Add RHEL7.0 machine types in QEMU
Patch10: kvm-pc-Replace-upstream-machine-types-by-RHEL-7-types.patch
# For bz#983991 - Provide RHEL-6 machine types
Patch11: kvm-qemu-kvm-Fix-migration-from-older-version-due-to-i82.patch
# For bz#983991 - Provide RHEL-6 machine types
Patch12: kvm-pc-Add-machine-type-rhel6.0.0.patch
# For bz#983991 - Provide RHEL-6 machine types
Patch13: kvm-pc-Drop-superfluous-RHEL-6-compat_props.patch
# For bz#983991 - Provide RHEL-6 machine types
Patch14: kvm-vga-Default-.vram_size_mb-to-16-like-prior-versions-.patch
# For bz#983991 - Provide RHEL-6 machine types
Patch15: kvm-pc-Drop-RHEL-6-USB-device-compat_prop-full-path.patch
# For bz#983991 - Provide RHEL-6 machine types
Patch16: kvm-pc-Drop-RHEL-6-compat_props-virtio-serial-pci.-max_p.patch
# For bz#983991 - Provide RHEL-6 machine types
Patch17: kvm-pc-Drop-RHEL-6-compat_props-apic-kvm-apic-.vapic.patch
# For bz#983991 - Provide RHEL-6 machine types
Patch18: kvm-qxl-set-revision-to-1-for-rhel6.0.0.patch
# For bz#983991 - Provide RHEL-6 machine types
Patch19: kvm-pc-Give-rhel6.0.0-a-kvmclock.patch
# For bz#983991 - Provide RHEL-6 machine types
Patch20: kvm-pc-Add-machine-type-rhel6.1.0.patch
# For bz#983991 - Provide RHEL-6 machine types
Patch21: kvm-pc-Add-machine-type-rhel6.2.0.patch
# For bz#983991 - Provide RHEL-6 machine types
Patch22: kvm-pc-Add-machine-type-rhel6.3.0.patch
# For bz#983991 - Provide RHEL-6 machine types
Patch23: kvm-pc-Add-machine-type-rhel6.4.0.patch
# For bz#983991 - Provide RHEL-6 machine types
Patch24: kvm-pc-Add-machine-type-rhel6.5.0.patch
# For bz#983991 - Provide RHEL-6 machine types
Patch25: kvm-e1000-Keep-capabilities-list-bit-on-for-older-RHEL-m.patch
# For bz#980840 - Change s3/s4 default to "disable".
Patch26: kvm-disable-s3-s4-by-default.patch
# For bz#980840 - Change s3/s4 default to "disable".
Patch27: kvm-pc-rhel6-compat-enable-S3-S4-for-6.1-and-lower-machi.patch
# For bz#962563 - disable (for now) EFI-enabled roms
Patch28: kvm-Disable-EFI-enabled-roms.patch
# For bz#853101 - qemu-kvm "vPMU passthrough" mode breaks migration, shouldn't be enabled by default
Patch29: kvm-pc-set-compat-pmu-property-for-rhel6.x-machine-types.patch
# For bz#969942 - update qemu-ga config & init script in RHEL7 wrt. fsfreeze hooks
Patch30: kvm-qga-fsfreeze-main-hook-adapt-to-RHEL-7-RH-only.patch
# For bz#903910 - RHEL7 does not have equivalent functionality for __com.redhat_qxl_screendump
Patch31: kvm-add-qxl_screendump-monitor-command.patch
# For bz#960216 - SEP flag behavior for CPU models of RHEL6 machine types should be compatible
Patch32: kvm-pc_piix-disable-CPUID_SEP-for-6.4.0-machine-types-an.patch
# For bz#918907 - provide backwards-compatible RHEL specific machine types in QEMU - CPU features
Patch33: kvm-pc-set-level-xlevel-correctly-on-486-qemu32-CPU-mode.patch
# For bz#918907 - provide backwards-compatible RHEL specific machine types in QEMU - CPU features
Patch34: kvm-pc-Remove-incorrect-rhel6.x-compat-model-value-for-C.patch
# For bz#918907 - provide backwards-compatible RHEL specific machine types in QEMU - CPU features
Patch35: kvm-pc-rhel6.x-has-x2apic-present-on-Conroe-Penryn-Nehal.patch
# For bz#918907 - provide backwards-compatible RHEL specific machine types in QEMU - CPU features
Patch36: kvm-pc-set-compat-CPUID-0x80000001-.EDX-bits-on-Westmere.patch
# For bz#918907 - provide backwards-compatible RHEL specific machine types in QEMU - CPU features
Patch37: kvm-pc-Remove-PCLMULQDQ-from-Westmere-on-rhel6.x-machine.patch
# For bz#918907 - provide backwards-compatible RHEL specific machine types in QEMU - CPU features
Patch38: kvm-pc-SandyBridge-rhel6.x-compat-fixes.patch
# For bz#918907 - provide backwards-compatible RHEL specific machine types in QEMU - CPU features
Patch39: kvm-pc-Haswell-doesn-t-have-rdtscp-on-rhel6.x.patch
# For bz#1006959 - qemu-iotests false positives
Patch40: kvm-qemu-iotests-Remove-lsi53c895a-tests-from-051.patch
# For bz#921983 - Disable or remove emulated network devices that we will not support
Patch41: kvm-Remove-i82550-network-card-emulation.patch
# For bz#903914 - Disable or remove usb related devices that we will not support
Patch42: kvm-Remove-usb-wacom-tablet.patch
# For bz#903914 - Disable or remove usb related devices that we will not support
Patch43: kvm-Disable-usb-uas.patch
# For bz#947441 - HPET device must be disabled
Patch44: kvm-Remove-no-hpet-option.patch
# For bz#1002286 - Disable or remove device isa-parallel
Patch45: kvm-Disable-isa-parallel.patch
# For bz#953304 - Serial number of some USB devices must be fixed for older RHEL machine types
Patch46: kvm-rhel6-compat-usb-serial-numbers.patch
# For bz#1009491 - move qga logfiles to new /var/log/qemu-ga/ directory [RHEL-7]
Patch47: kvm-qga-move-logfiles-to-new-directory-for-easier-SELinu.patch
# For bz#918907 - provide backwards-compatible RHEL specific machine types in QEMU - CPU features
Patch48: kvm-target-i386-add-cpu64-rhel6-CPU-model.patch
# For bz#918907 - provide backwards-compatible RHEL specific machine types in QEMU - CPU features
Patch49: kvm-pc-rhel6-doesn-t-have-APIC-on-pentium-CPU-models.patch
# For bz#918907 - provide backwards-compatible RHEL specific machine types in QEMU - CPU features
Patch50: kvm-pc-RHEL-6-had-x2apic-set-on-Opteron_G-123.patch
# For bz#918907 - provide backwards-compatible RHEL specific machine types in QEMU - CPU features
Patch51: kvm-pc-RHEL-6-don-t-have-RDTSCP.patch
# For bz#954195 - RHEL machines <=6.4 should not use mixemu
Patch52: kvm-pc_piix-disable-mixer-for-6.4.0-machine-types-and-be.patch
# For bz#1019474 - RHEL-7 can't load piix4_pm migration section from RHEL-6.5
Patch53: kvm-acpi-piix4-Enable-qemu-kvm-compatibility-mode.patch
# For bz#1004743 - XSAVE migration format not compatible between RHEL6 and RHEL7
Patch54: kvm-target-i386-support-loading-of-cpu-xsave-subsection.patch
# For bz#989608 - [7.0 FEAT] qemu runtime support for librbd backend (ceph)
Patch55: kvm-rbd-link-and-load-librbd-dynamically.patch
# For bz#989608 - [7.0 FEAT] qemu runtime support for librbd backend (ceph)
Patch56: kvm-rbd-Only-look-for-qemu-specific-copy-of-librbd.so.1.patch
# For bz#989677 - [HP 7.0 FEAT]: Increase KVM guest supported memory to 4TiB
Patch57: kvm-seabios-paravirt-allow-more-than-1TB-in-x86-guest.patch
# For bz#787463 - disable ivshmem (was: [Hitachi 7.0 FEAT] Support ivshmem (Inter-VM Shared Memory))
Patch58: kvm-rhel-Drop-ivshmem-device.patch
# For bz#997702 - Migration from RHEL6.5 host to RHEL7.0 host is failed due to iPXE ROM size mismatch
Patch59: kvm-Fix-migration-from-rhel6.5-to-rhel7-with-ipxe.patch
# For bz#1001076 - Disable or remove other block devices we won't support
Patch60: kvm-rhel-Revert-downstream-changes-to-unused-default-con.patch
# For bz#1001076 - Disable or remove other block devices we won't support
Patch61: kvm-rhel-Drop-cfi.pflash01-and-isa-ide-device.patch
# For bz#1001088 - Disable or remove display devices we won't support
Patch62: kvm-rhel-Drop-isa-vga-device.patch
# For bz#1001088 - Disable or remove display devices we won't support
Patch63: kvm-rhel-Make-isa-cirrus-vga-device-unavailable.patch
# For bz#1001123 - Disable or remove device ccid-card-emulated
Patch64: kvm-rhel-Make-ccid-card-emulated-device-unavailable.patch
# For bz#1032346 - basic OVMF support (non-volatile UEFI variables in flash, and fixup for ACPI tables)
Patch65: kvm-Partially-revert-rhel-Drop-cfi.pflash01-and-isa-ide-.patch
Patch66: kvm-Partial-commit-of-87123eabfa1ee7cef51066fd7fd8e7d5ec.patch
# For bz#1022392 - Disable live-storage-migration in qemu-kvm (migrate -b/-i)
Patch67: kvm-migration-disable-live-block-migration-b-i-for-rhel-.patch
# For bz#987583 - Initial Virtualization Differentiation for RHEL7 (Ceph enablement)
Patch68: kvm-Build-ceph-rbd-only-for-rhev.patch
# For bz#1001180 - Disable or remove devices pci-serial-2x, pci-serial-4x
Patch69: kvm-rhel-Make-pci-serial-2x-and-pci-serial-4x-device-una.patch
# For bz#1010858 - Disable unused human monitor commands
Patch70: kvm-monitor-Remove-pci_add-command-for-Red-Hat-Enterpris.patch
# For bz#1010858 - Disable unused human monitor commands
Patch71: kvm-monitor-Remove-pci_del-command-for-Red-Hat-Enterpris.patch
# For bz#1010858 - Disable unused human monitor commands
Patch72: kvm-monitor-Remove-usb_add-del-commands-for-Red-Hat-Ente.patch
# For bz#1010858 - Disable unused human monitor commands
Patch73: kvm-monitor-Remove-host_net_add-remove-for-Red-Hat-Enter.patch
# For bz#1005039 - add compat property to disable ctrl_mac_addr feature
Patch74: kvm-don-t-disable-ctrl_mac_addr-feature-for-6.5-machine-.patch
# For bz#1029539 - Machine type rhel6.1.0 and  balloon device cause migration fail from RHEL6.5 host to RHEL7.0 host
Patch75: kvm-pc-drop-virtio-balloon-pci-event_idx-compat-property.patch
# For bz#971933 - QMP: add RHEL's vendor extension prefix
Patch76: kvm-introduce-RFQDN_REDHAT-RHEL-6-7-fwd.patch
# For bz#1036537 - Cross version migration from RHEL6.5 host to RHEL7.0 host with sound device failed.
Patch77: kvm-fix-intel-hda-live-migration.patch
# For bz#678368 - RFE: Support more than 8 assigned devices
Patch78: kvm-pci-assign-cap-number-of-devices-that-can-be-assigne.patch
# For bz#678368 - RFE: Support more than 8 assigned devices
Patch79: kvm-vfio-cap-number-of-devices-that-can-be-assigned.patch
# For bz#889051 - Commands "__com.redhat_drive_add/del" don' t exist in RHEL7.0
Patch80: kvm-QMP-Forward-port-__com.redhat_drive_del-from-RHEL-6.patch
# For bz#889051 - Commands "__com.redhat_drive_add/del" don' t exist in RHEL7.0
Patch81: kvm-QMP-Forward-port-__com.redhat_drive_add-from-RHEL-6.patch
# For bz#889051 - Commands "__com.redhat_drive_add/del" don' t exist in RHEL7.0
Patch82: kvm-HMP-Forward-port-__com.redhat_drive_add-from-RHEL-6.patch
# For bz#889051 - Commands "__com.redhat_drive_add/del" don' t exist in RHEL7.0
Patch83: kvm-QMP-Document-throttling-parameters-of-__com.redhat_d.patch
# For bz#972773 - RHEL7: Clarify support statement in KVM help
Patch84: kvm-Add-support-statement-to-help-output.patch
# For bz#903910 - RHEL7 does not have equivalent functionality for __com.redhat_qxl_screendump
Patch85: kvm-__com.redhat_qxl_screendump-add-docs.patch
# For bz#999836 - -m 1 crashes
Patch86: kvm-vl-Round-memory-sizes-below-2MiB-up-to-2MiB.patch
# For bz#1052340 - pvticketlocks: default on
Patch87: kvm-enable-pvticketlocks-by-default.patch
# For bz#918907 - provide backwards-compatible RHEL specific machine types in QEMU - CPU features
Patch88: kvm-pc-Fix-rhel6.-3dnow-3dnowext-compat-bits.patch
# For bz#1038603 - make seabios 256k for rhel7 machine types
Patch89: kvm-switch-rhel7-machine-types-to-big-bios.patch
# For bz#1044742 - Cannot create guest on remote RHEL7 host using F20 virt-manager, libvirt's qemu -no-hpet detection is broken
Patch90: kvm-Add-back-no-hpet-but-ignore-it.patch
# For bz#998708 - qemu-kvm: maximum vcpu should be recommended maximum
Patch91: kvm-use-recommended-max-vcpu-count.patch
# For bz#1049706 - MIss CPUID_EXT_X2APIC in Westmere cpu model
Patch92: kvm-pc-Create-pc_compat_rhel-functions.patch
# For bz#1049706 - MIss CPUID_EXT_X2APIC in Westmere cpu model
Patch93: kvm-pc-Enable-x2apic-by-default-on-more-recent-CPU-model.patch
# For bz#918907 - provide backwards-compatible RHEL specific machine types in QEMU - CPU features
Patch94: kvm-pc-Disable-RDTSCP-unconditionally-on-rhel6.-machine-.patch
# For bz#1056428 - "rdtscp" flag defined on Opteron_G5 model and cann't be exposed to guest
# For bz#874400 - "rdtscp" flag defined on Opteron_G5 model and cann't be exposed to guest
Patch95: kvm-pc-Disable-RDTSCP-on-AMD-CPU-models.patch
# For bz#1039530 - add support for microsoft os descriptors
Patch96: kvm-usb-add-microsoft-os-descriptors-compat-property.patch
# For bz#1044182 - Relax qemu-kvm stack protection to -fstack-protector-strong
Patch97: kvm-configure-add-option-to-disable-fstack-protect.patch
# For bz#989677 - [HP 7.0 FEAT]: Increase KVM guest supported memory to 4TiB
Patch98: kvm-fix-guest-physical-bits-to-match-host-to-go-beyond-1.patch
# For bz#1057471 - fail to do hot-plug with "discard = on" with "Invalid parameter 'discard'" error
Patch99: kvm-QMP-Relax-__com.redhat_drive_add-parameter-checking.patch
# For bz#1073774 - e1000 ROM cause migrate fail  from RHEL6.5 host to RHEL7.0 host
Patch100: kvm-pc-Add-RHEL6-e1000-gPXE-image.patch
# For bz#1078809 - can not boot qemu-kvm-rhev with rbd image
Patch101: kvm-configure-Fix-bugs-preventing-Ceph-inclusion.patch
# For bz#1080170 - Default CPU model for rhel6.* machine-types is different from RHEL-6
Patch102: kvm-pc-Use-cpu64-rhel6-CPU-model-by-default-on-rhel6-mac.patch
# For bz#1078607 - intel 82576 VF not work in windows 2008 x86 - Code 12 [TestOnly]
# For bz#1080170 - Default CPU model for rhel6.* machine-types is different from RHEL-6
Patch103: kvm-target-i386-Copy-cpu64-rhel6-definition-into-qemu64.patch
# For bz#1093411 - Hot unplug CPU not working for RHEL7 host
Patch104: kvm-pc-add-hot_add_cpu-callback-to-all-machine-types.patch
Patch105: kvm-Remove-CONFIG_NE2000_ISA-from-all-config-files.patch
# For bz#1085950 - Migration/virtio-net: 7.0->vp-2.0-rc2: Mix of migration issues
Patch106: kvm-RHEL7-RHEV7.1-2.0-migration-compatibility.patch
# For bz#1085950 - Migration/virtio-net: 7.0->vp-2.0-rc2: Mix of migration issues
Patch107: kvm-remove-superfluous-.hot_add_cpu-and-.max_cpus-initia.patch
# For bz#1085950 - Migration/virtio-net: 7.0->vp-2.0-rc2: Mix of migration issues
Patch108: kvm-set-model-in-PC_RHEL6_5_COMPAT-for-qemu32-VCPU-RHEV-.patch
# For bz#1085950 - Migration/virtio-net: 7.0->vp-2.0-rc2: Mix of migration issues
Patch109: kvm-Undo-Enable-x2apic-by-default-for-compatibility.patch
# For bz#1027565 - fail to reboot guest after migration from RHEL6.5 host to RHEL7.0 host
# For bz#1103579 - fail to reboot guest after migration from RHEL6.5 host to RHEL7.0 host
Patch110: kvm-qemu_loadvm_state-shadow-SeaBIOS-for-VM-incoming-fro.patch
# For bz#994490 - Set per-machine-type SMBIOS strings
Patch111: kvm-rhel-SMBIOS-type-1-branding.patch
Patch112: kvm-Use-legacy-SMBIOS-for-rhel-machine-types.patch
Patch113: kvm-Disable-new-devices-in-qemu-2.1.patch
# For bz#1116772 - QMP: forward port rhel-only error reason to BLOCK_IO_ERROR event
Patch114: kvm-scripts-qapi-event.py-support-vendor-extension.patch
# For bz#1116772 - QMP: forward port rhel-only error reason to BLOCK_IO_ERROR event
Patch115: kvm-qmp-add-error-reason-to-the-BLOCK_IO_ERROR-event.patch
# For bz#1116772 - QMP: forward port rhel-only error reason to BLOCK_IO_ERROR event
Patch116: kvm-qmp-improve-debuggability-of-BLOCK_IO_ERROR-event.patch
# For bz#1085701 - Guest hits call trace migrate from RHEL6.5 to RHEL7.0 host with -M 6.1 & balloon & uhci device
# For bz#1103581 - Guest hits call trace migrate from RHEL6.5 to RHEL7.0 host with -M 6.1 & balloon & uhci device
Patch117: kvm-uhci-UNfix-irq-routing-for-RHEL-6-machtypes-RHEL-onl.patch
Patch118: kvm-Include-OHCI-device-for-ppc64.patch
Patch119: kvm-arm64-64K-pages-and-1024MB-guest.patch
# For bz#1076326 - qemu-kvm does not quit when booting guest w/ 161 vcpus and "-no-kvm"
# For bz#1118665 - Migration: rhel7.0->rhev7.1
Patch120: kvm-exit-when-no-kvm-and-vcpu-count-160.patch
# For bz#1118665 - Migration: rhel7.0->rhev7.1
Patch121: kvm-Revert-Use-legacy-SMBIOS-for-rhel-machine-types.patch
# For bz#1118665 - Migration: rhel7.0->rhev7.1
Patch122: kvm-rhel-Use-SMBIOS-legacy-mode-for-machine-types-7.0.patch
# For bz#1118665 - Migration: rhel7.0->rhev7.1
Patch123: kvm-rhel-Suppress-hotplug-memory-address-space-for-machi.patch
# For bz#1118665 - Migration: rhel7.0->rhev7.1
Patch124: kvm-rhel-Fix-ACPI-table-size-for-machine-types-7.0.patch
# For bz#1118665 - Migration: rhel7.0->rhev7.1
Patch125: kvm-rhel-Fix-missing-pc-q35-rhel7.0.0-compatibility-prop.patch
# For bz#1118665 - Migration: rhel7.0->rhev7.1
Patch126: kvm-rhel-virtio-scsi-pci.any_layout-off-for-machine-type.patch
# For bz#1118665 - Migration: rhel7.0->rhev7.1
Patch127: kvm-rhel-PIIX4_PM.memory-hotplug-support-off-for-machine.patch
# For bz#1118665 - Migration: rhel7.0->rhev7.1
Patch128: kvm-rhel-apic.version-0x11-for-machine-types-7.0.patch
# For bz#1118665 - Migration: rhel7.0->rhev7.1
Patch129: kvm-rhel-nec-usb-xhci.superspeed-ports-first-off-for-mac.patch
# For bz#1118665 - Migration: rhel7.0->rhev7.1
Patch130: kvm-rhel-pci-serial.prog_if-0-for-machine-types-7.0.patch
# For bz#1118665 - Migration: rhel7.0->rhev7.1
Patch131: kvm-rhel-virtio-net-pci.guest_announce-off-for-machine-t.patch
# For bz#1118665 - Migration: rhel7.0->rhev7.1
Patch132: kvm-rhel-ICH9-LPC.memory-hotplug-support-off-for-machine.patch
# For bz#1118665 - Migration: rhel7.0->rhev7.1
Patch133: kvm-rhel-.power_controller_present-off-for-machine-types.patch
# For bz#1118665 - Migration: rhel7.0->rhev7.1
Patch134: kvm-rhel-virtio-net-pci.ctrl_guest_offloads-off-for-mach.patch
# For bz#1118665 - Migration: rhel7.0->rhev7.1
Patch135: kvm-pc-q35-rhel7.0.0-Disable-x2apic-default.patch
# For bz#1003432 - qemu-kvm should not allow different virtio serial port use the same name
Patch136: kvm-virtio-serial-create-a-linked-list-of-all-active-dev.patch
# For bz#1003432 - qemu-kvm should not allow different virtio serial port use the same name
Patch137: kvm-virtio-serial-search-for-duplicate-port-names-before.patch
# For bz#1111351 - RHEL-6.6 migration compatibility: CPU models
Patch138: kvm-pc-RHEL-6-CPUID-compat-code-for-Broadwell-CPU-model.patch
# For bz#1129259 - Add traces to virtio-rng device
Patch139: kvm-virtio-rng-add-some-trace-events.patch
# For bz#1126976 - VHDX image format does not work on PPC64 (Endian issues)
Patch140: kvm-block-vhdx-add-error-check.patch
# For bz#1126976 - VHDX image format does not work on PPC64 (Endian issues)
Patch141: kvm-block-VHDX-endian-fixes.patch
# Patch included upstream
# For bz#1133736 - qemu should provide iothread and x-data-plane properties for /usr/libexec/qemu-kvm -device virtio-blk-pci,?
#Patch142: kvm-qdev-monitor-include-QOM-properties-in-device-FOO-he.patch
# For bz#1136752 - virtio-blk dataplane support for block_resize and hot unplug
Patch143: kvm-block-acquire-AioContext-in-qmp_block_resize.patch
# For bz#1136752 - virtio-blk dataplane support for block_resize and hot unplug
Patch144: kvm-virtio-blk-allow-block_resize-with-dataplane.patch
# For bz#1136752 - virtio-blk dataplane support for block_resize and hot unplug
Patch145: kvm-block-acquire-AioContext-in-do_drive_del.patch
# For bz#1136752 - virtio-blk dataplane support for block_resize and hot unplug
Patch146: kvm-virtio-blk-allow-drive_del-with-dataplane.patch
# For bz#1093023 - provide RHEL-specific machine types in QEMU
Patch147: kvm-rhel-Add-rhel7.1.0-machine-types.patch
# For bz#1136512 - rhel7.0.0 machtype compat after CVE-2014-5263 vmstate_xhci_event: fix unterminated field list
Patch148: kvm-vmstate_xhci_event-bug-compat-for-rhel7.0.0-machine-.patch
# For bz#1139706 - pflash (UEFI varstore) migration shortcut for libvirt [RHEV]
Patch149: kvm-pflash_cfi01-fixup-stale-DPRINTF-calls.patch
# For bz#1139706 - pflash (UEFI varstore) migration shortcut for libvirt [RHEV]
Patch150: kvm-pflash_cfi01-write-flash-contents-to-bdrv-on-incomin.patch
# For bz#1140145 - qemu-kvm crashed when doing iofuzz testing
Patch151: kvm-ide-Fix-segfault-when-flushing-a-device-that-doesn-t.patch
# For bz#1138579 - Migration failed with nec-usb-xhci from RHEL7. 0 to RHEL7.1
Patch152: kvm-xhci-PCIe-endpoint-migration-compatibility-fix.patch
# For bz#1138579 - Migration failed with nec-usb-xhci from RHEL7. 0 to RHEL7.1
Patch153: kvm-rh-machine-types-xhci-PCIe-endpoint-migration-compat.patch
# For bz#1055532 - QEMU should abort when invalid CPU flag name is used
Patch154: kvm-target-i386-Reject-invalid-CPU-feature-names-on-the-.patch
# For bz#1113998 - RHEL Power/KVM (qemu-kvm-rhev)
Patch155: kvm-target-ppc-virtex-ml507-machine-type-should-depend-o.patch
# For bz#1113998 - RHEL Power/KVM (qemu-kvm-rhev)
Patch156: kvm-RHEL-only-Disable-tests-that-don-t-work-with-RHEL-bu.patch
# For bz#1113998 - RHEL Power/KVM (qemu-kvm-rhev)
Patch157: kvm-RHEL-onlyy-Disable-unused-ppc-machine-types.patch
Patch158: kvm-RHEL-only-Remove-unneeded-devices-from-ppc64-qemu-kv.patch
Patch159: kvm-RHEL-only-Replace-upstream-pseries-machine-types-wit.patch
# For bz#1123349 - [FJ7.0 Bug] SCSI command issued from KVM guest doesn't reach target device
Patch160: kvm-scsi-bus-prepare-scsi_req_new-for-introduction-of-pa.patch
# For bz#1123349 - [FJ7.0 Bug] SCSI command issued from KVM guest doesn't reach target device
Patch161: kvm-scsi-bus-introduce-parse_cdb-in-SCSIDeviceClass-and-.patch
# For bz#1123349 - [FJ7.0 Bug] SCSI command issued from KVM guest doesn't reach target device
Patch162: kvm-scsi-block-extract-scsi_block_is_passthrough.patch
# For bz#1123349 - [FJ7.0 Bug] SCSI command issued from KVM guest doesn't reach target device
Patch163: kvm-scsi-block-scsi-generic-implement-parse_cdb.patch
# For bz#1123349 - [FJ7.0 Bug] SCSI command issued from KVM guest doesn't reach target device
Patch164: kvm-virtio-scsi-implement-parse_cdb.patch
# For bz#1135893 - qemu-kvm should report an error message when host's freehugepage memory < domain's memory
Patch165: kvm-exec-file_ram_alloc-print-error-when-prealloc-fails.patch
# For bz#1144089 - [HP 7.1 FEAT] Increase qemu-kvm-rhev's VCPU limit to 240
Patch166: kvm-pc-increase-maximal-VCPU-count-to-240.patch
# For bz#1132569 - RFE: Enable curl driver in qemu-kvm-rhev: https only
Patch167: kvm-block.curl-adding-timeout-option.patch
# For bz#1132569 - RFE: Enable curl driver in qemu-kvm-rhev: https only
Patch168: kvm-curl-Allow-a-cookie-or-cookies-to-be-sent-with-http-.patch
# For bz#1132569 - RFE: Enable curl driver in qemu-kvm-rhev: https only
Patch169: kvm-curl-Don-t-deref-NULL-pointer-in-call-to-aio_poll.patch
# For bz#1143054 - kvmclock: Ensure time in migration never goes backward (backport)
Patch170: kvm-Introduce-cpu_clean_all_dirty.patch
# For bz#1143054 - kvmclock: Ensure time in migration never goes backward (backport)
Patch171: kvm-kvmclock-Ensure-proper-env-tsc-value-for-kvmclock_cu.patch
# For bz#1143054 - kvmclock: Ensure time in migration never goes backward (backport)
Patch172: kvm-kvmclock-Ensure-time-in-migration-never-goes-backwar.patch
# For bz#852348 - fail to block_resize local data disk with IDE/AHCI disk_interface
Patch173: kvm-IDE-Fill-the-IDENTIFY-request-consistently.patch
# For bz#852348 - fail to block_resize local data disk with IDE/AHCI disk_interface
Patch174: kvm-ide-Add-resize-callback-to-ide-core.patch
# For bz#1140997 - guest is stuck when setting balloon memory with large guest-stats-polling-interval
Patch175: kvm-virtio-balloon-fix-integer-overflow-in-memory-stats-.patch
# For bz#1117445 - QMP: extend block events with error information
Patch176: kvm-block-extend-BLOCK_IO_ERROR-event-with-nospace-indic.patch
# For bz#1117445 - QMP: extend block events with error information
Patch177: kvm-block-extend-BLOCK_IO_ERROR-with-reason-string.patch
# For bz#1108040 - Enable make check for qemu-kvm-rhev 2.0 and newer
Patch178: kvm-Disable-tests-for-removed-features.patch
# For bz#1108040 - Enable make check for qemu-kvm-rhev 2.0 and newer
Patch179: kvm-Disable-arm-board-types-using-lsi53c895a.patch
# For bz#1108040 - Enable make check for qemu-kvm-rhev 2.0 and newer
Patch180: kvm-libqtest-launch-QEMU-with-QEMU_AUDIO_DRV-none.patch
# For bz#1126704 - BUG: When use '-sandbox on'+'vnc'+'hda' and quit, qemu-kvm hang
Patch181: kvm-seccomp-add-semctl-to-the-syscall-whitelist.patch
# For bz#1140001 - data-plane hotplug should be refused to start if device is already in use (drive-mirror job)
Patch182: kvm-dataplane-fix-virtio_blk_data_plane_create-op-blocke.patch
# For bz#1123908 - block.c: multiwrite_merge() truncates overlapping requests
Patch183: kvm-block-fix-overlapping-multiwrite-requests.patch
# For bz#1123908 - block.c: multiwrite_merge() truncates overlapping requests
Patch184: kvm-qemu-iotests-add-multiwrite-test-cases.patch
# For bz#946993 - Q35 does not honor -drive if=ide,... and its sugared forms -cdrom, -hda, ...
Patch185: kvm-blockdev-Orphaned-drive-search.patch
# For bz#946993 - Q35 does not honor -drive if=ide,... and its sugared forms -cdrom, -hda, ...
Patch186: kvm-blockdev-Allow-overriding-if_max_dev-property.patch
# For bz#946993 - Q35 does not honor -drive if=ide,... and its sugared forms -cdrom, -hda, ...
Patch187: kvm-pc-vl-Add-units-per-default-bus-property.patch
# For bz#946993 - Q35 does not honor -drive if=ide,... and its sugared forms -cdrom, -hda, ...
Patch188: kvm-ide-Update-ide_drive_get-to-be-HBA-agnostic.patch
# For bz#946993 - Q35 does not honor -drive if=ide,... and its sugared forms -cdrom, -hda, ...
Patch189: kvm-qtest-bios-tables-Correct-Q35-command-line.patch
# For bz#946993 - Q35 does not honor -drive if=ide,... and its sugared forms -cdrom, -hda, ...
Patch190: kvm-q35-ahci-Pick-up-cdrom-and-hda-options.patch
# For bz#1144325 - Can not probe  "qemu.kvm.virtio_blk_data_plane_complete_request"
Patch191: kvm-trace-events-drop-orphan-virtio_blk_data_plane_compl.patch
# For bz#1144325 - Can not probe  "qemu.kvm.virtio_blk_data_plane_complete_request"
Patch192: kvm-trace-events-drop-orphan-usb_mtp_data_out.patch
# For bz#1144325 - Can not probe  "qemu.kvm.virtio_blk_data_plane_complete_request"
Patch193: kvm-trace-events-drop-orphan-iscsi-trace-events.patch
# For bz#1144325 - Can not probe  "qemu.kvm.virtio_blk_data_plane_complete_request"
Patch194: kvm-cleanup-trace-events.pl-Tighten-search-for-trace-eve.patch
# For bz#1144325 - Can not probe  "qemu.kvm.virtio_blk_data_plane_complete_request"
Patch195: kvm-trace-events-Drop-unused-megasas-trace-event.patch
# For bz#1144325 - Can not probe  "qemu.kvm.virtio_blk_data_plane_complete_request"
Patch196: kvm-trace-events-Drop-orphaned-monitor-trace-event.patch
# For bz#1144325 - Can not probe  "qemu.kvm.virtio_blk_data_plane_complete_request"
Patch197: kvm-trace-events-Fix-comments-pointing-to-source-files.patch
# For bz#1155015 - [Fujitsu 7.1 FEAT]:QEMU: capturing trace data all the time using ftrace-based tracing
Patch198: kvm-simpletrace-add-simpletrace.py-no-header-option.patch
# For bz#1155015 - [Fujitsu 7.1 FEAT]:QEMU: capturing trace data all the time using ftrace-based tracing
Patch199: kvm-trace-extract-stap_escape-function-for-reuse.patch
# For bz#1155015 - [Fujitsu 7.1 FEAT]:QEMU: capturing trace data all the time using ftrace-based tracing
Patch200: kvm-trace-add-tracetool-simpletrace_stap-format.patch
# For bz#1155015 - [Fujitsu 7.1 FEAT]:QEMU: capturing trace data all the time using ftrace-based tracing
Patch201: kvm-trace-install-simpletrace-SystemTap-tapset.patch
# For bz#1155015 - [Fujitsu 7.1 FEAT]:QEMU: capturing trace data all the time using ftrace-based tracing
Patch202: kvm-trace-install-trace-events-file.patch
# For bz#1155015 - [Fujitsu 7.1 FEAT]:QEMU: capturing trace data all the time using ftrace-based tracing
Patch203: kvm-trace-add-SystemTap-init-scripts-for-simpletrace-bri.patch
# For bz#1155015 - [Fujitsu 7.1 FEAT]:QEMU: capturing trace data all the time using ftrace-based tracing
Patch204: kvm-trace-add-systemtap-initscript-README-file-to-RPM.patch
# For bz#1104063 - [RHEL7.1 Feat] Enable qemu-kvm Inter VM Shared Memory (IVSHM) feature
Patch205: kvm-ivshmem-use-error_report.patch
# For bz#1104063 - [RHEL7.1 Feat] Enable qemu-kvm Inter VM Shared Memory (IVSHM) feature
Patch206: kvm-ivshmem-RHEL-only-remove-unsupported-code.patch
# For bz#1104063 - [RHEL7.1 Feat] Enable qemu-kvm Inter VM Shared Memory (IVSHM) feature
Patch207: kvm-ivshmem-RHEL-only-explicitly-remove-dead-code.patch
# For bz#1104063 - [RHEL7.1 Feat] Enable qemu-kvm Inter VM Shared Memory (IVSHM) feature
Patch208: kvm-Revert-rhel-Drop-ivshmem-device.patch
# For bz#1135844 - [virtio-win]communication ports were marked with a  yellow exclamation after hotplug pci-serial,pci-serial-2x,pci-serial-4x
Patch209: kvm-serial-reset-state-at-startup.patch
# For bz#1140975 - fail to login spice session with password + expire time
Patch210: kvm-spice-call-qemu_spice_set_passwd-during-init.patch
# For bz#1145028 - send-key does not crash windows guest even when it should
# For bz#1146801 - sendkey: releasing order of combined keys was wrongly converse
Patch211: kvm-input-fix-send-key-monitor-command-release-event-ord.patch
# For bz#1152830 - Fix sense buffer in virtio-scsi LUN passthrough
Patch212: kvm-virtio-scsi-sense-in-virtio_scsi_command_complete.patch
# For bz#1141666 - Qemu crashed if reboot guest after hot remove AC97 sound device
Patch213: kvm-ac97-register-reset-via-qom.patch
# For bz#1146573 - qemu core dump when boot guest with smp(num)<cores(num)
Patch214: kvm-smbios-Fix-assertion-on-socket-count-calculation.patch
# For bz#1152922 - smbios uuid mismatched
Patch215: kvm-smbios-Encode-UUID-according-to-SMBIOS-specification.patch
# For bz#1146826 - QEMU will not reject invalid number of queues (num_queues = 0) specified for virtio-scsi
Patch216: kvm-virtio-scsi-Report-error-if-num_queues-is-0-or-too-l.patch
# For bz#1146826 - QEMU will not reject invalid number of queues (num_queues = 0) specified for virtio-scsi
Patch217: kvm-virtio-scsi-Fix-memory-leak-when-realize-failed.patch
# For bz#1146826 - QEMU will not reject invalid number of queues (num_queues = 0) specified for virtio-scsi
Patch218: kvm-virtio-scsi-Fix-num_queue-input-validation.patch
# For bz#1153590 - Improve error message on huge page preallocation
Patch219: kvm-util-Improve-os_mem_prealloc-error-message.patch
# For bz#1160120 - qemu-kvm-rhev shouldn't include non supported devices for POWER
Patch220: kvm-Downstream-only-remove-uneeded-PCI-devices-for-POWER.patch
# For bz#1160120 - qemu-kvm-rhev shouldn't include non supported devices for POWER
Patch221: kvm-Downstream-only-Remove-assorted-unneeded-devices-for.patch
# For bz#1160120 - qemu-kvm-rhev shouldn't include non supported devices for POWER
Patch222: kvm-Downstream-only-Remove-ISA-bus-and-device-support-fo.patch
# For bz#1145042 - The output of "/usr/libexec/qemu-kvm -M ?" should be ordered.
Patch223: kvm-well-defined-listing-order-for-machine-types.patch
# For bz#1145042 - The output of "/usr/libexec/qemu-kvm -M ?" should be ordered.
Patch224: kvm-i386-pc-add-piix-and-q35-machtypes-to-sorting-famili.patch
# For bz#1145042 - The output of "/usr/libexec/qemu-kvm -M ?" should be ordered.
Patch225: kvm-i386-pc-add-RHEL-machtypes-to-sorting-families-for-M.patch
# For bz#1150820 - fail to specify wwn for virtual IDE CD-ROM
Patch226: kvm-ide-Add-wwn-support-to-IDE-ATAPI-drive.patch
# For bz#1147354 - Qemu core dump when boot up a guest on a non-existent hugepage path
Patch227: kvm-exec-report-error-when-memory-hpagesize.patch
# For bz#1147354 - Qemu core dump when boot up a guest on a non-existent hugepage path
Patch228: kvm-exec-add-parameter-errp-to-gethugepagesize.patch
# For bz#1152901 - block/curl: Fix type safety of s->timeout
Patch229: kvm-block-curl-Improve-type-safety-of-s-timeout.patch
# For bz#1151947 - virtconsole causes qemu-kvm core dump
Patch230: kvm-virtio-serial-avoid-crash-when-port-has-no-name.patch
# For bz#1160325 - arm64: support aavmf
Patch231: kvm-aarch64-raise-max_cpus-to-8.patch
# For bz#1160325 - arm64: support aavmf
Patch232: kvm-hw-arm-virt-add-linux-stdout-path-to-chosen-DT-node.patch
# For bz#1160325 - arm64: support aavmf
Patch233: kvm-hw-arm-virt-Provide-flash-devices-for-boot-ROMs.patch
# For bz#1160325 - arm64: support aavmf
Patch234: kvm-hw-arm-boot-load-DTB-as-a-ROM-image.patch
# For bz#1160325 - arm64: support aavmf
Patch235: kvm-hw-arm-boot-pass-an-address-limit-to-and-return-size.patch
# For bz#1160325 - arm64: support aavmf
Patch236: kvm-hw-arm-boot-load-device-tree-to-base-of-DRAM-if-no-k.patch
# For bz#1160325 - arm64: support aavmf
Patch237: kvm-hw-arm-boot-enable-DTB-support-when-booting-ELF-imag.patch
# For bz#1160325 - arm64: support aavmf
Patch238: kvm-hw-arm-virt-mark-timer-in-fdt-as-v8-compatible.patch
# For bz#1160325 - arm64: support aavmf
Patch239: kvm-hw-arm-boot-register-cpu-reset-handlers-if-using-bio.patch
# For bz#1160325 - arm64: support aavmf
Patch240: kvm-Downstream-only-Declare-ARM-kernel-support-read-only.patch
# For bz#1150510 - kernel ignores ACPI memory devices (PNP0C80) present at boot time
# For bz#1163735 - -device pc-dimm fails to initialize on non-NUMA configs
Patch241: kvm-pc-dimm-Don-t-check-dimm-node-when-there-is-non-NUMA.patch
# For bz#1146809 - Incorrect colours on virtual VGA with ppc64le guest under ppc64 host
Patch242: kvm-vga-Start-cutting-out-non-32bpp-conversion-support.patch
# For bz#1146809 - Incorrect colours on virtual VGA with ppc64le guest under ppc64 host
Patch243: kvm-vga-Remove-remainder-of-old-conversion-cruft.patch
# For bz#1146809 - Incorrect colours on virtual VGA with ppc64le guest under ppc64 host
Patch244: kvm-vga-Separate-LE-and-BE-conversion-functions.patch
# For bz#1146809 - Incorrect colours on virtual VGA with ppc64le guest under ppc64 host
Patch245: kvm-vga-Remove-rgb_to_pixel-indirection.patch
# For bz#1146809 - Incorrect colours on virtual VGA with ppc64le guest under ppc64 host
Patch246: kvm-vga-Simplify-vga_draw_blank-a-bit.patch
# For bz#1146809 - Incorrect colours on virtual VGA with ppc64le guest under ppc64 host
Patch247: kvm-cirrus-Remove-non-32bpp-cursor-drawing.patch
# For bz#1146809 - Incorrect colours on virtual VGA with ppc64le guest under ppc64 host
Patch248: kvm-vga-Remove-some-should-be-done-in-BIOS-comments.patch
# For bz#1146809 - Incorrect colours on virtual VGA with ppc64le guest under ppc64 host
Patch249: kvm-vga-Rename-vga_template.h-to-vga-helpers.h.patch
# For bz#1146809 - Incorrect colours on virtual VGA with ppc64le guest under ppc64 host
Patch250: kvm-vga-Make-fb-endian-a-common-state-variable.patch
# For bz#1146809 - Incorrect colours on virtual VGA with ppc64le guest under ppc64 host
Patch251: kvm-vga-Add-endian-to-vmstate.patch
# For bz#1146809 - Incorrect colours on virtual VGA with ppc64le guest under ppc64 host
Patch252: kvm-vga-pci-add-qext-region-to-mmio.patch
# For bz#1123812 - Reboot guest and guest's virtio-scsi disk will be lost after forwards migration (from RHEL6.6 host to RHEL7.1 host)
Patch253: kvm-virtio-scsi-work-around-bug-in-old-BIOSes.patch
# For bz#1132385 - qemu-img convert rate about 100k/second from qcow2/raw to vmdk format on nfs system file
Patch254: kvm-block-New-bdrv_nb_sectors.patch
# For bz#1132385 - qemu-img convert rate about 100k/second from qcow2/raw to vmdk format on nfs system file
Patch255: kvm-vmdk-Optimize-cluster-allocation.patch
# For bz#1132385 - qemu-img convert rate about 100k/second from qcow2/raw to vmdk format on nfs system file
Patch256: kvm-vmdk-Handle-failure-for-potentially-large-allocation.patch
# For bz#1132385 - qemu-img convert rate about 100k/second from qcow2/raw to vmdk format on nfs system file
Patch257: kvm-vmdk-Use-bdrv_nb_sectors-where-sectors-not-bytes-are.patch
# For bz#1132385 - qemu-img convert rate about 100k/second from qcow2/raw to vmdk format on nfs system file
Patch258: kvm-vmdk-fix-vmdk_parse_extents-extent_file-leaks.patch
# For bz#1132385 - qemu-img convert rate about 100k/second from qcow2/raw to vmdk format on nfs system file
Patch259: kvm-vmdk-fix-buf-leak-in-vmdk_parse_extents.patch
# For bz#1132385 - qemu-img convert rate about 100k/second from qcow2/raw to vmdk format on nfs system file
Patch260: kvm-vmdk-Fix-integer-overflow-in-offset-calculation.patch
# For bz#1140744 - Enable native support for Ceph
Patch261: kvm-Revert-Build-ceph-rbd-only-for-rhev.patch
# For bz#1140744 - Enable native support for Ceph
Patch262: kvm-Revert-rbd-Only-look-for-qemu-specific-copy-of-librb.patch
# For bz#1140744 - Enable native support for Ceph
Patch263: kvm-Revert-rbd-link-and-load-librbd-dynamically.patch
# For bz#1140620 - Should replace "qemu-system-i386" by "/usr/libexec/qemu-kvm" in manpage of qemu-kvm for our official qemu-kvm build
Patch264: kvm-Use-qemu-kvm-in-documentation-instead-of-qemu-system.patch
# For bz#1024599 - Windows7 x86 guest with ahci backend hit BSOD when do "hibernate"
Patch265: kvm-ide-stash-aiocb-for-flushes.patch
# For bz#1024599 - Windows7 x86 guest with ahci backend hit BSOD when do "hibernate"
Patch266: kvm-ide-simplify-reset-callbacks.patch
# For bz#1024599 - Windows7 x86 guest with ahci backend hit BSOD when do "hibernate"
Patch267: kvm-ide-simplify-set_inactive-callbacks.patch
# For bz#1024599 - Windows7 x86 guest with ahci backend hit BSOD when do "hibernate"
Patch268: kvm-ide-simplify-async_cmd_done-callbacks.patch
# For bz#1024599 - Windows7 x86 guest with ahci backend hit BSOD when do "hibernate"
Patch269: kvm-ide-simplify-start_transfer-callbacks.patch
# For bz#1024599 - Windows7 x86 guest with ahci backend hit BSOD when do "hibernate"
Patch270: kvm-ide-wrap-start_dma-callback.patch
# For bz#1024599 - Windows7 x86 guest with ahci backend hit BSOD when do "hibernate"
Patch271: kvm-ide-remove-wrong-setting-of-BM_STATUS_INT.patch
# For bz#1024599 - Windows7 x86 guest with ahci backend hit BSOD when do "hibernate"
Patch272: kvm-ide-fold-add_status-callback-into-set_inactive.patch
# For bz#1024599 - Windows7 x86 guest with ahci backend hit BSOD when do "hibernate"
Patch273: kvm-ide-move-BM_STATUS-bits-to-pci.-ch.patch
# For bz#1024599 - Windows7 x86 guest with ahci backend hit BSOD when do "hibernate"
Patch274: kvm-ide-move-retry-constants-out-of-BM_STATUS_-namespace.patch
# For bz#1024599 - Windows7 x86 guest with ahci backend hit BSOD when do "hibernate"
Patch275: kvm-ahci-remove-duplicate-PORT_IRQ_-constants.patch
# For bz#1024599 - Windows7 x86 guest with ahci backend hit BSOD when do "hibernate"
Patch276: kvm-ide-stop-PIO-transfer-on-errors.patch
# For bz#1024599 - Windows7 x86 guest with ahci backend hit BSOD when do "hibernate"
Patch277: kvm-ide-make-all-commands-go-through-cmd_done.patch
# For bz#1024599 - Windows7 x86 guest with ahci backend hit BSOD when do "hibernate"
Patch278: kvm-ide-atapi-Mark-non-data-commands-as-complete.patch
# For bz#1024599 - Windows7 x86 guest with ahci backend hit BSOD when do "hibernate"
Patch279: kvm-ahci-construct-PIO-Setup-FIS-for-PIO-commands.patch
# For bz#1024599 - Windows7 x86 guest with ahci backend hit BSOD when do "hibernate"
Patch280: kvm-ahci-properly-shadow-the-TFD-register.patch
# For bz#1024599 - Windows7 x86 guest with ahci backend hit BSOD when do "hibernate"
Patch281: kvm-ahci-Correct-PIO-D2H-FIS-responses.patch
# For bz#1024599 - Windows7 x86 guest with ahci backend hit BSOD when do "hibernate"
Patch282: kvm-ahci-Update-byte-count-after-DMA-completion.patch
# For bz#1024599 - Windows7 x86 guest with ahci backend hit BSOD when do "hibernate"
Patch283: kvm-ahci-Fix-byte-count-regression-for-ATAPI-PIO.patch
# For bz#1024599 - Windows7 x86 guest with ahci backend hit BSOD when do "hibernate"
Patch284: kvm-ahci-Fix-SDB-FIS-Construction.patch
# For bz#1159710 - vhost-user:Bad ram offset
Patch285: kvm-vhost-user-fix-mmap-offset-calculation.patch
# For bz#1160102 - opening read-only iscsi lun as read-write should fail
Patch286: kvm-iscsi-Refuse-to-open-as-writable-if-the-LUN-is-write.patch
# For bz#1157646 - CVE-2014-7815 qemu-kvm-rhev: qemu: vnc: insufficient bits_per_pixel from the client sanitization [rhel-7.1]
Patch287: kvm-vnc-sanitize-bits_per_pixel-from-the-client.patch
# For bz#1160504 - guest can not show usb device after adding some usb controllers and redirdevs.
Patch288: kvm-usb-host-fix-usb_host_speed_compat-tyops.patch
# For bz#1142331 - qemu-img convert intermittently corrupts output images
Patch289: kvm-block-raw-posix-Fix-disk-corruption-in-try_fiemap.patch
# For bz#1142331 - qemu-img convert intermittently corrupts output images
Patch290: kvm-block-raw-posix-use-seek_hole-ahead-of-fiemap.patch
# For bz#1142331 - qemu-img convert intermittently corrupts output images
Patch291: kvm-raw-posix-Fix-raw_co_get_block_status-after-EOF.patch
# For bz#1142331 - qemu-img convert intermittently corrupts output images
Patch292: kvm-raw-posix-raw_co_get_block_status-return-value.patch
# For bz#1142331 - qemu-img convert intermittently corrupts output images
Patch293: kvm-raw-posix-SEEK_HOLE-suffices-get-rid-of-FIEMAP.patch
# For bz#1142331 - qemu-img convert intermittently corrupts output images
Patch294: kvm-raw-posix-The-SEEK_HOLE-code-is-flawed-rewrite-it.patch
# For bz#1164759 - Handle multipage ranges in invalidate_and_set_dirty()
Patch295: kvm-exec-Handle-multipage-ranges-in-invalidate_and_set_d.patch
# For bz#1166501 - Migration "expected downtime" does not refresh after reset to a new value
Patch296: kvm-migration-static-variables-will-not-be-reset-at-seco.patch
# For bz#1166067 - qemu-kvm aborted when hot plug PCI device to guest with romfile and rombar=0
Patch297: kvm-hw-pci-fixed-error-flow-in-pci_qdev_init.patch
# For bz#1166067 - qemu-kvm aborted when hot plug PCI device to guest with romfile and rombar=0
Patch298: kvm-hw-pci-fixed-hotplug-crash-when-using-rombar-0-with-.patch
# For bz#1161397 - qemu core dump when install a RHEL.7 guest(xhci) with migration
Patch299: kvm-xhci-add-sanity-checks-to-xhci_lookup_uport.patch
# For bz#1166481 - Allow qemu-img to bypass the host cache (check, compare, convert, rebase, amend)
Patch300: kvm-qemu-img-Allow-source-cache-mode-specification.patch
# For bz#1166481 - Allow qemu-img to bypass the host cache (check, compare, convert, rebase, amend)
Patch301: kvm-qemu-img-Allow-cache-mode-specification-for-amend.patch
# For bz#1166481 - Allow qemu-img to bypass the host cache (check, compare, convert, rebase, amend)
Patch302: kvm-qemu-img-fix-img_compare-flags-error-path.patch
# For bz#1166481 - Allow qemu-img to bypass the host cache (check, compare, convert, rebase, amend)
Patch303: kvm-qemu-img-clarify-src_cache-option-documentation.patch
# For bz#1166481 - Allow qemu-img to bypass the host cache (check, compare, convert, rebase, amend)
Patch304: kvm-qemu-img-fix-rebase-src_cache-option-documentation.patch
# For bz#1141656 - Virtio-scsi: performance degradation from 1.5.3 to 2.1.0
Patch305: kvm-scsi-Optimize-scsi_req_alloc.patch
# For bz#1141656 - Virtio-scsi: performance degradation from 1.5.3 to 2.1.0
Patch306: kvm-virtio-scsi-Optimize-virtio_scsi_init_req.patch
# For bz#1141656 - Virtio-scsi: performance degradation from 1.5.3 to 2.1.0
Patch307: kvm-virtio-scsi-Fix-comment-for-VirtIOSCSIReq.patch
# For bz#1169589 - test case 051 071 and 087 of qemu-iotests fail for qcow2 with qemu-kvm-rhev-2.1.2-14.el7
Patch308: kvm-qemu-iotests-Fix-broken-test-cases.patch
# For bz#1165087 - QEMU core dumped for the destination guest when do migating guest to file
Patch309: kvm-Fix-for-crash-after-migration-in-virtio-rng-on-bi-en.patch
# For bz#1169847 - only support mach-virt
Patch310: kvm-Downstream-only-remove-unsupported-machines-from-AAr.patch
# For bz#1170093 - guest NUMA failed to migrate when machine is rhel6.5.0
Patch311: kvm-numa-Don-t-allow-memdev-on-RHEL-6-machine-types.patch
# For bz#1136381 - RFE: Supporting creating vdi/vpc format disk with protocols (glusterfs) for qemu-kvm-rhev-2.1.x
Patch312: kvm-block-allow-bdrv_unref-to-be-passed-NULL-pointers.patch
# For bz#1136381 - RFE: Supporting creating vdi/vpc format disk with protocols (glusterfs) for qemu-kvm-rhev-2.1.x
Patch313: kvm-block-vdi-use-block-layer-ops-in-vdi_create-instead-.patch
# For bz#1136381 - RFE: Supporting creating vdi/vpc format disk with protocols (glusterfs) for qemu-kvm-rhev-2.1.x
Patch314: kvm-block-use-the-standard-ret-instead-of-result.patch
# For bz#1136381 - RFE: Supporting creating vdi/vpc format disk with protocols (glusterfs) for qemu-kvm-rhev-2.1.x
Patch315: kvm-block-vpc-use-block-layer-ops-in-vpc_create-instead-.patch
# For bz#1136381 - RFE: Supporting creating vdi/vpc format disk with protocols (glusterfs) for qemu-kvm-rhev-2.1.x
Patch316: kvm-block-iotest-update-084-to-test-static-VDI-image-cre.patch
# For bz#1136381 - RFE: Supporting creating vdi/vpc format disk with protocols (glusterfs) for qemu-kvm-rhev-2.1.x
Patch317: kvm-block-remove-BLOCK_OPT_NOCOW-from-vdi_create_opts.patch
# For bz#1136381 - RFE: Supporting creating vdi/vpc format disk with protocols (glusterfs) for qemu-kvm-rhev-2.1.x
Patch318: kvm-block-remove-BLOCK_OPT_NOCOW-from-vpc_create_opts.patch
# For bz#1163079 - CVE-2014-7840 qemu-kvm-rhev: qemu: insufficient parameter validation during ram load [rhel-7.1]
Patch319: kvm-migration-fix-parameter-validation-on-ram-load-CVE-2.patch
# For bz#1169280 - Segfault while query device properties (ics, icp)
Patch320: kvm-qdev-monitor-fix-segmentation-fault-on-qdev_device_h.patch
# For bz#1171552 - Storage vm migration failed when running BurnInTes
Patch321: kvm-block-migration-Disable-cache-invalidate-for-incomin.patch
# For bz#1173167 - Corrupted ACPI tables in some configurations using pc-i440fx-rhel7.0.0
Patch322: kvm-acpi-Use-apic_id_limit-when-calculating-legacy-ACPI-.patch
# For bz#1173394 - numa_smaps doesn't respect bind policy with huge page
Patch323: kvm-vl-Adjust-the-place-of-calling-mlockall-to-speedup-V.patch
# For bz#1175841 - Delete cow block driver
Patch324: kvm-block-delete-cow-block-driver.patch
# For bz#1179165 - [SVVP]smbios HCT job failed with  Unspecified error  with -M pc-i440fx-rhel7.1.0
Patch325: kvm-smbios-Fix-dimm-size-calculation-when-RAM-is-multipl.patch
# For bz#1177127 - [SVVP]smbios HCT job failed with  'Processor Max Speed cannot be Unknown' with -M pc-i440fx-rhel7.1.0
Patch326: kvm-smbios-Don-t-report-unknown-CPU-speed-fix-SVVP-regre.patch
# For bz#1182233 - Machine type rhel6.5.0 does not use kvmclock due to typo
Patch327: kvm-pc-fix-usage-of-x86_cpu_compat_disable_kvm_features.patch
# For bz#1182494 - BUG: qemu-kvm hang when enabled both sandbox and mlock
Patch328: kvm-seccomp-add-mlockall-to-whitelist.patch
# For bz#1172473 - BUG: seccomp filter failure with "-object memory-backend-ram"
Patch329: kvm-seccomp-add-mbind-to-the-syscall-whitelist.patch
# For bz#1170533 - Should disalbe S3/S4 in default  under Q35 machine type in rhel7
Patch330: kvm-ich9-add-disable_s3-disable_s4-s4_val-properties.patch
# For bz#1170533 - Should disalbe S3/S4 in default  under Q35 machine type in rhel7
Patch331: kvm-q35-disable-s3-s4-by-default.patch
# For bz#1170871 - qemu core dumped when unhotplug gpu card assigned to guest
Patch332: kvm-vfio-pci-Fix-interrupt-disabling.patch
# For bz#1169457 - CVE-2014-8106 qemu-kvm-rhev: qemu: cirrus: insufficient blit region checks [rhel-7.1]
Patch333: kvm-cirrus-fix-blit-region-check.patch
# For bz#1169457 - CVE-2014-8106 qemu-kvm-rhev: qemu: cirrus: insufficient blit region checks [rhel-7.1]
Patch334: kvm-cirrus-don-t-overflow-CirrusVGAState-cirrus_bltbuf.patch
# For bz#1117170 - RHEV: Cannot start VMs that have more than 23 snapshots.
Patch335: kvm-block-qapi-move-string-allocation-from-stack-to-the-.patch
# For bz#1117170 - RHEV: Cannot start VMs that have more than 23 snapshots.
Patch336: kvm-block-remove-unused-variable-in-bdrv_commit.patch
# For bz#1117170 - RHEV: Cannot start VMs that have more than 23 snapshots.
Patch337: kvm-block-mirror-change-string-allocation-to-2-bytes.patch
# For bz#1117170 - RHEV: Cannot start VMs that have more than 23 snapshots.
Patch338: kvm-block-update-string-sizes-for-filename-backing_file-.patch
# For bz#1191385 - "-numa node" option cause windows guest can not online hot-added CPUs
Patch339: kvm-pc-acpi-mark-all-possible-CPUs-as-enabled-in-SRAT.patch
# For bz#1194552 - Add rhel-6.6.0 machine type to RHEL 7.1.z to support RHEL 6.6 to RHEL 7.1 live migration
Patch340: kvm-pc-add-rhel6.6.0-machine-type.patch
# For bz#1203543 - bdrv_make_zero() passes a too large nb_sectors value to bdrv_write_zeroes()
Patch341: kvm-block-Fix-max-nb_sectors-in-bdrv_make_zero.patch
# For bz#1219271 - 
Patch342: kvm-fdc-force-the-fifo-access-to-be-in-bounds-of-the-all.patch

BuildRequires: zlib-devel
BuildRequires: SDL-devel
BuildRequires: which
BuildRequires: texi2html
BuildRequires: gnutls-devel
BuildRequires: cyrus-sasl-devel
BuildRequires: libtool
BuildRequires: libaio-devel
BuildRequires: rsync
BuildRequires: python
BuildRequires: pciutils-devel
BuildRequires: pulseaudio-libs-devel
BuildRequires: libiscsi-devel
BuildRequires: ncurses-devel
BuildRequires: libattr-devel
BuildRequires: libusbx-devel
%if 0%{have_usbredir}
BuildRequires: usbredir-devel >= 0.6
%endif
BuildRequires: texinfo
%if 0%{have_spice}
BuildRequires: spice-protocol >= 0.12.2
BuildRequires: spice-server-devel >= 0.12.0
%endif
%if 0%{have_seccomp}
BuildRequires: libseccomp-devel >= 1.0.0
%endif
# For network block driver
BuildRequires: libcurl-devel
BuildRequires: libssh2-devel
%ifarch x86_64
BuildRequires: librados2-devel
BuildRequires: librbd1-devel
%endif
%if 0%{have_gluster}
# For gluster block driver
BuildRequires: glusterfs-api-devel >= 3.6.0
BuildRequires: glusterfs-devel
%endif
# We need both because the 'stap' binary is probed for by configure
BuildRequires: systemtap
BuildRequires: systemtap-sdt-devel
# For smartcard NSS support
BuildRequires: nss-devel
# For XFS discard support in raw-posix.c
# For VNC JPEG support
BuildRequires: libjpeg-devel
# For VNC PNG support
BuildRequires: libpng-devel
# For uuid generation
BuildRequires: libuuid-devel
# For BlueZ device support
BuildRequires: bluez-libs-devel
# For Braille device support
BuildRequires: brlapi-devel
# For test suite
BuildRequires: check-devel
# For virtfs
BuildRequires: libcap-devel
# Hard requirement for version >= 1.3
BuildRequires: pixman-devel
# Documentation requirement
BuildRequires: perl-podlators
BuildRequires: texinfo
# For rdma
%if 0%{?have_librdma:1}
BuildRequires: librdmacm-devel
%endif
%if 0%{have_fdt}
BuildRequires: libfdt-devel
%endif
# iasl and cpp for acpi generation (not a hard requirement as we can use
# pre-compiled files, but it's better to use this)
%ifarch %{ix86} x86_64
BuildRequires: iasl
BuildRequires: cpp
%endif
# For compressed guest memory dumps
BuildRequires: lzo-devel snappy-devel
# For NUMA memory binding
BuildRequires: numactl-devel


Requires: qemu-img%{?pkgsuffix} = %{epoch}:%{version}-%{release}

# RHEV-specific changes:
# We provide special suffix for qemu-kvm so the conflit is easy
# In addition, RHEV version should obsolete all RHEL version in case both
# RHEL and RHEV channels are used
%rhel_rhev_conflicts qemu-kvm


%define qemudocdir %{_docdir}/%{pkgname}

%description
qemu-kvm is an open source virtualizer that provides hardware emulation for
the KVM hypervisor. qemu-kvm acts as a virtual machine monitor together with
the KVM kernel modules, and emulates the hardware for a full system such as
a PC and its assocated peripherals.

As qemu-kvm requires no host kernel patches to run, it is safe and easy to use.

%if %{rhev}
%package -n qemu-img%{?pkgsuffix}
Summary: QEMU command line tool for manipulating disk images
Group: Development/Tools

%rhel_rhev_conflicts qemu-img

%description -n qemu-img%{?pkgsuffix}
This package provides a command line tool for manipulating disk images.

%package -n qemu-kvm-common%{?pkgsuffix}
Summary: QEMU common files needed by all QEMU targets
Group: Development/Tools
Requires(post): /usr/bin/getent
Requires(post): /usr/sbin/groupadd
Requires(post): /usr/sbin/useradd
Requires(post): systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units

%rhel_rhev_conflicts qemu-kvm-common

%description -n qemu-kvm-common%{?pkgsuffix}
qemu-kvm is an open source virtualizer that provides hardware emulation for
the KVM hypervisor. 

This package provides documentation and auxiliary programs used with qemu-kvm.

%endif

%if %{with guest_agent}
%package -n qemu-guest-agent
Summary: QEMU guest agent
Group: System Environment/Daemons
Requires(post): systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units

%description -n qemu-guest-agent
qemu-kvm is an open source virtualizer that provides hardware emulation for
the KVM hypervisor. 

This package provides an agent to run inside guests, which communicates
with the host over a virtio-serial channel named "org.qemu.guest_agent.0"

This package does not need to be installed on the host OS.

%post -n qemu-guest-agent
%systemd_post qemu-guest-agent.service

%preun -n qemu-guest-agent
%systemd_preun qemu-guest-agent.service

%postun -n qemu-guest-agent
%systemd_postun_with_restart qemu-guest-agent.service

%endif

%if %{rhev}
%package -n qemu-kvm-tools%{?pkgsuffix}
Summary: KVM debugging and diagnostics tools
Group: Development/Tools

%rhel_rhev_conflicts qemu-kvm-tools

%description -n qemu-kvm-tools%{?pkgsuffix}
This package contains some diagnostics and debugging tools for KVM,
such as kvm_stat.

%package -n libcacard%{?pkgsuffix}
Summary:        Common Access Card (CAC) Emulation
Group:          Development/Libraries

%rhel_rhev_conflicts libcacard

%description -n libcacard%{?pkgsuffix}
Common Access Card (CAC) emulation library.

%package -n libcacard-tools%{?pkgsuffix}
Summary:        CAC Emulation tools
Group:          Development/Libraries
Requires:       libcacard%{?pkgsuffix} = %{epoch}:%{version}-%{release}
# older qemu-img has vscclient which is now in libcacard-tools
Requires:       qemu-img >= 3:1.3.0-5

%rhel_rhev_conflicts libcacard-tools

%description -n libcacard-tools%{?pkgsuffix}
CAC emulation tools.

%package -n libcacard-devel%{?pkgsuffix}
Summary:        CAC Emulation devel
Group:          Development/Libraries
Requires:       libcacard%{?pkgsuffix} = %{epoch}:%{version}-%{release}

%rhel_rhev_conflicts libcacard-devel

%description -n libcacard-devel%{?pkgsuffix}
CAC emulation development files.
%endif

%prep
%setup -q -n qemu-%{version}

# Copy bios files to allow 'make check' pass
cp %{SOURCE18} pc-bios 
cp %{SOURCE20} pc-bios

%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p1
%patch8 -p1
%patch9 -p1
%patch10 -p1
%patch11 -p1
%patch12 -p1
%patch13 -p1
%patch14 -p1
%patch15 -p1
%patch16 -p1
%patch17 -p1
%patch18 -p1
%patch19 -p1
%patch20 -p1
%patch21 -p1
%patch22 -p1
%patch23 -p1
%patch24 -p1
%patch25 -p1
%patch26 -p1
%patch27 -p1
%patch28 -p1
%patch29 -p1
%patch30 -p1
%patch31 -p1
%patch32 -p1
%patch33 -p1
%patch34 -p1
%patch35 -p1
%patch36 -p1
%patch37 -p1
%patch38 -p1
%patch39 -p1
%patch40 -p1
%patch41 -p1
%patch42 -p1
%patch43 -p1
%patch44 -p1
%patch45 -p1
%patch46 -p1
%patch47 -p1
%patch48 -p1
%patch49 -p1
%patch50 -p1
%patch51 -p1
%patch52 -p1
%patch53 -p1
%patch54 -p1
%patch55 -p1
%patch56 -p1
%patch57 -p1
%patch58 -p1
%patch59 -p1
%patch60 -p1
%patch61 -p1
%patch62 -p1
%patch63 -p1
%patch64 -p1
%patch65 -p1
%patch66 -p1
%patch67 -p1
%patch68 -p1
%patch69 -p1
%patch70 -p1
%patch71 -p1
%patch72 -p1
%patch73 -p1
%patch74 -p1
%patch75 -p1
%patch76 -p1
%patch77 -p1
%patch78 -p1
%patch79 -p1
%patch80 -p1
%patch81 -p1
%patch82 -p1
%patch83 -p1
%patch84 -p1
%patch85 -p1
%patch86 -p1
%patch87 -p1
%patch88 -p1
%patch89 -p1
%patch90 -p1
%patch91 -p1
%patch92 -p1
%patch93 -p1
%patch94 -p1
%patch95 -p1
%patch96 -p1
%patch97 -p1
%patch98 -p1
%patch99 -p1
%patch100 -p1
%patch101 -p1
%patch102 -p1
%patch103 -p1
%patch104 -p1
%patch105 -p1
%patch106 -p1
%patch107 -p1
%patch108 -p1
%patch109 -p1
%patch110 -p1
%patch111 -p1
%patch112 -p1
%patch113 -p1
%patch114 -p1
%patch115 -p1
%patch116 -p1
%patch117 -p1
%patch118 -p1
%patch119 -p1
%patch120 -p1
%patch121 -p1
%patch122 -p1
%patch123 -p1
%patch124 -p1
%patch125 -p1
%patch126 -p1
%patch127 -p1
%patch128 -p1
%patch129 -p1
%patch130 -p1
%patch131 -p1
%patch132 -p1
%patch133 -p1
%patch134 -p1
%patch135 -p1
%patch136 -p1
%patch137 -p1
%patch138 -p1
%patch139 -p1
%patch140 -p1
%patch141 -p1
#%patch142 -p1
%patch143 -p1
%patch144 -p1
%patch145 -p1
%patch146 -p1
%patch147 -p1
%patch148 -p1
%patch149 -p1
%patch150 -p1
%patch151 -p1
%patch152 -p1
%patch153 -p1
%patch154 -p1
%patch155 -p1
%patch156 -p1
%patch157 -p1
%patch158 -p1
%patch159 -p1
%patch160 -p1
%patch161 -p1
%patch162 -p1
%patch163 -p1
%patch164 -p1
%patch165 -p1
%patch166 -p1
%patch167 -p1
%patch168 -p1
%patch169 -p1
%patch170 -p1
%patch171 -p1
%patch172 -p1
%patch173 -p1
%patch174 -p1
%patch175 -p1
%patch176 -p1
%patch177 -p1
%patch178 -p1
%patch179 -p1
%patch180 -p1
%patch181 -p1
%patch182 -p1
%patch183 -p1
%patch184 -p1
%patch185 -p1
%patch186 -p1
%patch187 -p1
%patch188 -p1
%patch189 -p1
%patch190 -p1
%patch191 -p1
%patch192 -p1
%patch193 -p1
%patch194 -p1
%patch195 -p1
%patch196 -p1
%patch197 -p1
%patch198 -p1
%patch199 -p1
%patch200 -p1
%patch201 -p1
%patch202 -p1
%patch203 -p1
%patch204 -p1
%patch205 -p1
%patch206 -p1
%patch207 -p1
%patch208 -p1
%patch209 -p1
%patch210 -p1
%patch211 -p1
%patch212 -p1
%patch213 -p1
%patch214 -p1
%patch215 -p1
%patch216 -p1
%patch217 -p1
%patch218 -p1
%patch219 -p1
%patch220 -p1
%patch221 -p1
%patch222 -p1
%patch223 -p1
%patch224 -p1
%patch225 -p1
%patch226 -p1
%patch227 -p1
%patch228 -p1
%patch229 -p1
%patch230 -p1
%patch231 -p1
%patch232 -p1
%patch233 -p1
%patch234 -p1
%patch235 -p1
%patch236 -p1
%patch237 -p1
%patch238 -p1
%patch239 -p1
%patch240 -p1
%patch241 -p1
%patch242 -p1
%patch243 -p1
%patch244 -p1
%patch245 -p1
%patch246 -p1
%patch247 -p1
%patch248 -p1
%patch249 -p1
%patch250 -p1
%patch251 -p1
%patch252 -p1
%patch253 -p1
%patch254 -p1
%patch255 -p1
%patch256 -p1
%patch257 -p1
%patch258 -p1
%patch259 -p1
%patch260 -p1
%patch261 -p1
%patch262 -p1
%patch263 -p1
%patch264 -p1
%patch265 -p1
%patch266 -p1
%patch267 -p1
%patch268 -p1
%patch269 -p1
%patch270 -p1
%patch271 -p1
%patch272 -p1
%patch273 -p1
%patch274 -p1
%patch275 -p1
%patch276 -p1
%patch277 -p1
%patch278 -p1
%patch279 -p1
%patch280 -p1
%patch281 -p1
%patch282 -p1
%patch283 -p1
%patch284 -p1
%patch285 -p1
%patch286 -p1
%patch287 -p1
%patch288 -p1
%patch289 -p1
%patch290 -p1
%patch291 -p1
%patch292 -p1
%patch293 -p1
%patch294 -p1
%patch295 -p1
%patch296 -p1
%patch297 -p1
%patch298 -p1
%patch299 -p1
%patch300 -p1
%patch301 -p1
%patch302 -p1
%patch303 -p1
%patch304 -p1
%patch305 -p1
%patch306 -p1
%patch307 -p1
%patch308 -p1
%patch309 -p1
%patch310 -p1
%patch311 -p1
%patch312 -p1
%patch313 -p1
%patch314 -p1
%patch315 -p1
%patch316 -p1
%patch317 -p1
%patch318 -p1
%patch319 -p1
%patch320 -p1
%patch321 -p1
%patch322 -p1
%patch323 -p1
%patch324 -p1
%patch325 -p1
%patch326 -p1
%patch327 -p1
%patch328 -p1
%patch329 -p1
%patch330 -p1
%patch331 -p1
%patch332 -p1
%patch333 -p1
%patch334 -p1
%patch335 -p1
%patch336 -p1
%patch337 -p1
%patch338 -p1
%patch339 -p1
%patch340 -p1
%patch341 -p1
%patch342 -p1

%build
buildarch="%{kvm_target}-softmmu"

# --build-id option is used for giving info to the debug packages.
extraldflags="-Wl,--build-id";
buildldflags="VL_LDFLAGS=-Wl,--build-id"

%ifarch s390
    # drop -g flag to prevent memory exhaustion by linker
    %global optflags %(echo %{optflags} | sed 's/-g//')
    sed -i.debug 's/"-g $CFLAGS"/"$CFLAGS"/g' configure
%endif

dobuild() {
    ./configure \
%if %{rhev}
        --prefix=%{_prefix} \
        --libdir=%{_libdir} \
        --sysconfdir=%{_sysconfdir} \
        --interp-prefix=%{_prefix}/qemu-%%M \
        --audio-drv-list=pa,alsa \
        --with-confsuffix=/%{pkgname} \
        --localstatedir=%{_localstatedir} \
        --libexecdir=%{_libexecdir} \
        --with-pkgversion=%{name}-%{version}-%{release} \
        --disable-strip \
        --disable-qom-cast-debug \
        --extra-ldflags="$extraldflags -pie -Wl,-z,relro -Wl,-z,now" \
        --extra-cflags="%{optflags} -fPIE -DPIE" \
        --enable-trace-backend=dtrace \
        --enable-werror \
        --disable-xen \
        --disable-virtfs \
        --enable-kvm \
        --enable-curl \
        --enable-libusb \
%if 0%{have_spice}
        --enable-spice \
%else
        --disable-spice \
%endif
%if 0%{have_seccomp}
        --enable-seccomp \
%else
        --disable-seccomp \
%endif
%if 0%{have_fdt}
        --enable-fdt \
%else
        --disable-fdt \
%endif
        --enable-docs \
        --disable-sdl \
        --disable-debug-tcg \
        --disable-sparse \
        --disable-brlapi \
        --disable-bluez \
        --disable-vde \
        --disable-curses \
        --enable-vnc-tls \
        --enable-vnc-sasl \
        --enable-linux-aio \
        --enable-smartcard-nss \
        --enable-lzo \
        --enable-snappy \
%if 0%{have_usbredir}
        --enable-usb-redir \
%else
        --disable-usb-redir \
%endif
        --enable-vnc-png \
        --disable-vnc-jpeg \
        --enable-vnc-ws \
        --enable-uuid \
        --disable-vhost-scsi \
%if %{with guest_agent}
        --enable-guest-agent \
%else
        --disable-guest-agent \
%endif
        --disable-tpm \
        --enable-live-block-ops \
        --disable-live-block-migration \
%ifarch x86_64
        --enable-rbd \
%endif
%if 0%{have_gluster}
        --enable-glusterfs \
        --block-drv-rw-whitelist=qcow2,raw,file,host_device,nbd,iscsi,gluster,rbd,blkdebug \
%else
        --disable-glusterfs \
        --block-drv-rw-whitelist=qcow2,raw,file,host_device,nbd,iscsi,rbd,blkdebug \
%endif
        --block-drv-ro-whitelist=vmdk,vhdx,vpc,https,ssh \
        --enable-numa \
        "$@"

    echo "config-host.mak contents:"
    echo "==="
    cat config-host.mak
    echo "==="

    make V=1 %{?_smp_mflags} $buildldflags
%else
        --prefix=%{_prefix} \
        --libdir=%{_libdir} \
        --localstatedir=%{_localstatedir} \
        --with-pkgversion=%{name}-%{version}-%{release} \
        --disable-guest-agent \
        --target-list= --cpu=%{_arch}

   make qemu-ga %{?_smp_mflags} $buildldflags
%endif
}

dobuild --target-list="$buildarch"

%if %{rhev}
        # Setup back compat qemu-kvm binary
        ./scripts/tracetool.py --backend dtrace --format stap \
          --binary %{_libexecdir}/qemu-kvm --target-name %{kvm_target} \
          --target-type system --probe-prefix \
          qemu.kvm < ./trace-events > qemu-kvm.stp

        ./scripts/tracetool.py --backend dtrace --format simpletrace-stap \
          --binary %{_libexecdir}/qemu-kvm --target-name %{kvm_target} \
          --target-type system --probe-prefix \
          qemu.kvm < ./trace-events > qemu-kvm-simpletrace.stp

        cp -a %{kvm_target}-softmmu/qemu-system-%{kvm_target} qemu-kvm


    gcc %{SOURCE6} -O2 -g -o ksmctl
%endif

%install
%define _udevdir %(pkg-config --variable=udevdir udev)/rules.d

%if %{rhev}
    install -D -p -m 0644 %{SOURCE4} $RPM_BUILD_ROOT%{_unitdir}/ksm.service
    install -D -p -m 0644 %{SOURCE5} $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/ksm
    install -D -p -m 0755 ksmctl $RPM_BUILD_ROOT%{_libexecdir}/ksmctl

    install -D -p -m 0644 %{SOURCE7} $RPM_BUILD_ROOT%{_unitdir}/ksmtuned.service
    install -D -p -m 0755 %{SOURCE8} $RPM_BUILD_ROOT%{_sbindir}/ksmtuned
    install -D -p -m 0644 %{SOURCE9} $RPM_BUILD_ROOT%{_sysconfdir}/ksmtuned.conf

    mkdir -p $RPM_BUILD_ROOT%{_bindir}/
    mkdir -p $RPM_BUILD_ROOT%{_udevdir}

    install -m 0755 scripts/kvm/kvm_stat $RPM_BUILD_ROOT%{_bindir}/
    install -m 0644 %{SOURCE3} $RPM_BUILD_ROOT%{_udevdir}

    make DESTDIR=$RPM_BUILD_ROOT \
        sharedir="%{_datadir}/%{pkgname}" \
        datadir="%{_datadir}/%{pkgname}" \
        install

    mkdir -p $RPM_BUILD_ROOT%{_datadir}/%{pkgname}
    mkdir -p $RPM_BUILD_ROOT%{_datadir}/systemtap/tapset

    # Install compatibility roms
    install %{SOURCE14} $RPM_BUILD_ROOT%{_datadir}/%{pkgname}/
    install %{SOURCE15} $RPM_BUILD_ROOT%{_datadir}/%{pkgname}/
    install %{SOURCE16} $RPM_BUILD_ROOT%{_datadir}/%{pkgname}/
    install %{SOURCE17} $RPM_BUILD_ROOT%{_datadir}/%{pkgname}/
    install %{SOURCE20} $RPM_BUILD_ROOT%{_datadir}/%{pkgname}/

    install -m 0755 qemu-kvm $RPM_BUILD_ROOT%{_libexecdir}/
    install -m 0644 qemu-kvm.stp $RPM_BUILD_ROOT%{_datadir}/systemtap/tapset/
    install -m 0644 qemu-kvm-simpletrace.stp $RPM_BUILD_ROOT%{_datadir}/systemtap/tapset/

    rm $RPM_BUILD_ROOT%{_bindir}/qemu-system-%{kvm_target}
    rm $RPM_BUILD_ROOT%{_datadir}/systemtap/tapset/qemu-system-%{kvm_target}.stp
    rm $RPM_BUILD_ROOT%{_datadir}/systemtap/tapset/qemu-system-%{kvm_target}-simpletrace.stp

    # Install simpletrace
    install -m 0755 scripts/simpletrace.py $RPM_BUILD_ROOT%{_datadir}/%{pkgname}/simpletrace.py
    mkdir -p $RPM_BUILD_ROOT%{_datadir}/%{pkgname}/tracetool
    install -m 0644 -t $RPM_BUILD_ROOT%{_datadir}/%{pkgname}/tracetool scripts/tracetool/*.py
    mkdir -p $RPM_BUILD_ROOT%{_datadir}/%{pkgname}/tracetool/backend
    install -m 0644 -t $RPM_BUILD_ROOT%{_datadir}/%{pkgname}/tracetool/backend scripts/tracetool/backend/*.py
    mkdir -p $RPM_BUILD_ROOT%{_datadir}/%{pkgname}/tracetool/format
    install -m 0644 -t $RPM_BUILD_ROOT%{_datadir}/%{pkgname}/tracetool/format scripts/tracetool/format/*.py

    mkdir -p $RPM_BUILD_ROOT%{qemudocdir}
    install -p -m 0644 -t ${RPM_BUILD_ROOT}%{qemudocdir} Changelog README README.systemtap COPYING COPYING.LIB LICENSE %{SOURCE19}
    mv ${RPM_BUILD_ROOT}%{_docdir}/qemu/qemu-doc.html $RPM_BUILD_ROOT%{qemudocdir}
    mv ${RPM_BUILD_ROOT}%{_docdir}/qemu/qemu-tech.html $RPM_BUILD_ROOT%{qemudocdir}
    mv ${RPM_BUILD_ROOT}%{_docdir}/qemu/qmp-commands.txt $RPM_BUILD_ROOT%{qemudocdir}
    chmod -x ${RPM_BUILD_ROOT}%{_mandir}/man1/*
    chmod -x ${RPM_BUILD_ROOT}%{_mandir}/man8/*

    install -D -p -m 0644 qemu.sasl $RPM_BUILD_ROOT%{_sysconfdir}/sasl2/qemu-kvm.conf

    # Provided by package openbios
    rm -rf ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/openbios-ppc
    rm -rf ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/openbios-sparc32
    rm -rf ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/openbios-sparc64
    # Provided by package SLOF
    rm -rf ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/slof.bin

    # Remove unpackaged files.
    rm -rf ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/palcode-clipper
    rm -rf ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/petalogix*.dtb
    rm -f ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/bamboo.dtb
    rm -f ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/ppc_rom.bin
    rm -rf ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/s390-zipl.rom
    rm -rf ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/s390-ccw.img

    %ifnarch %{power64}
        rm -f ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/spapr-rtas.bin
        rm -f ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/u-boot.e500
    %endif

    %ifnarch x86_64
        rm -rf ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/acpi-dsdt.aml
        rm -rf ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/kvmvapic.bin
        rm -rf ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/linuxboot.bin
        rm -rf ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/multiboot.bin
        rm -rf ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/q35-acpi-dsdt.aml
    %endif

    # Remove sparc files
    rm -rf ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/QEMU,tcx.bin
    rm -rf ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/QEMU,cgthree.bin

    # Remove efi roms
    rm -rf ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/efi*.rom

    # Provided by package ipxe
    rm -rf ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/pxe*rom
    # Provided by package vgabios
    rm -rf ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/vgabios*bin
    # Provided by package seabios
    rm -rf ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/bios*.bin
    # Provided by package sgabios
    rm -rf ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/sgabios.bin

    # the pxe gpxe images will be symlinks to the images on
    # /usr/share/ipxe, as QEMU doesn't know how to look
    # for other paths, yet.
    pxe_link() {
        ln -s ../ipxe/$2.rom %{buildroot}%{_datadir}/%{pkgname}/pxe-$1.rom
    }

    pxe_link e1000 8086100e
    pxe_link ne2k_pci 10ec8029
    pxe_link pcnet 10222000
    pxe_link rtl8139 10ec8139
    pxe_link virtio 1af41000

    rom_link() {
        ln -s $1 %{buildroot}%{_datadir}/%{pkgname}/$2
    }

    %ifnarch aarch64
      rom_link ../seavgabios/vgabios-isavga.bin vgabios.bin
      rom_link ../seavgabios/vgabios-cirrus.bin vgabios-cirrus.bin
      rom_link ../seavgabios/vgabios-qxl.bin vgabios-qxl.bin
      rom_link ../seavgabios/vgabios-stdvga.bin vgabios-stdvga.bin
      rom_link ../seavgabios/vgabios-vmware.bin vgabios-vmware.bin
    %endif
    %ifarch x86_64
      rom_link ../seabios/bios.bin bios.bin
      rom_link ../seabios/bios-256k.bin bios-256k.bin
    %endif
    rom_link ../sgabios/sgabios.bin sgabios.bin

    %if 0%{have_kvm_setup}
        install -D -p -m 755 %{SOURCE21} $RPM_BUILD_ROOT%{_prefix}/lib/systemd/kvm-setup
	install -D -p -m 644 %{SOURCE22} $RPM_BUILD_ROOT%{_unitdir}/kvm-setup.service
	install -D -p -m 644 %{SOURCE23} $RPM_BUILD_ROOT%{_presetdir}/85-kvm.preset
    %endif
%endif

%if %{with guest_agent}
    # For the qemu-guest-agent subpackage, install:
    # - the systemd service file and the udev rules:
    mkdir -p $RPM_BUILD_ROOT%{_unitdir}
    mkdir -p $RPM_BUILD_ROOT%{_udevdir}
    install -m 0644 %{SOURCE10} $RPM_BUILD_ROOT%{_unitdir}
    install -m 0644 %{SOURCE11} $RPM_BUILD_ROOT%{_udevdir}

    # - the environment file for the systemd service:
    install -D -p -m 0644 %{SOURCE13} \
      $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/qemu-ga

    # - the fsfreeze hook script:
    install -D --preserve-timestamps \
      scripts/qemu-guest-agent/fsfreeze-hook \
      $RPM_BUILD_ROOT%{_sysconfdir}/qemu-ga/fsfreeze-hook

    # - the directory for user scripts:
    mkdir $RPM_BUILD_ROOT%{_sysconfdir}/qemu-ga/fsfreeze-hook.d

    # - and the fsfreeze script samples:
    mkdir --parents $RPM_BUILD_ROOT%{_datadir}/%{name}/qemu-ga/fsfreeze-hook.d/
    install --preserve-timestamps --mode=0644 \
      scripts/qemu-guest-agent/fsfreeze-hook.d/*.sample \
      $RPM_BUILD_ROOT%{_datadir}/%{name}/qemu-ga/fsfreeze-hook.d/

    # - Install dedicated log directory:
    mkdir -p -v $RPM_BUILD_ROOT%{_localstatedir}/log/qemu-ga/
%endif

%if %{rhev}
    # Install rules to use the bridge helper with libvirt's virbr0
    install -m 0644 %{SOURCE12} $RPM_BUILD_ROOT%{_sysconfdir}/%{pkgname}

make %{?_smp_mflags} $buildldflags DESTDIR=$RPM_BUILD_ROOT install-libcacard
find $RPM_BUILD_ROOT -name "libcacard.so*" -exec chmod +x \{\} \;

find $RPM_BUILD_ROOT -name '*.la' -or -name '*.a' | xargs rm -f
%endif

%if %{with guest_agent}
    mkdir -p $RPM_BUILD_ROOT%{_bindir}
    install -c -m 0755  qemu-ga ${RPM_BUILD_ROOT}%{_bindir}/qemu-ga
%endif

%check
make check

%post
# load kvm modules now, so we can make sure no reboot is needed.
# If there's already a kvm module installed, we don't mess with it
%if %{rhev}
sh %{_sysconfdir}/sysconfig/modules/kvm.modules &> /dev/null || :
    udevadm trigger --subsystem-match=misc --sysname-match=kvm --action=add || :
%if 0%{have_kvm_setup}
    systemctl daemon-reload # Make sure it sees the new presets and unitfile
    %systemd_post kvm-setup.service
    if systemctl is-enabled kvm-setup.service > /dev/null; then
        systemctl start kvm-setup.service
    fi
%endif

%post -n qemu-kvm-common%{?pkgsuffix}
    %systemd_post ksm.service
    %systemd_post ksmtuned.service

    getent group kvm >/dev/null || groupadd -g 36 -r kvm
    getent group qemu >/dev/null || groupadd -g 107 -r qemu
    getent passwd qemu >/dev/null || \
       useradd -r -u 107 -g qemu -G kvm -d / -s /sbin/nologin \
       -c "qemu user" qemu

%preun -n qemu-kvm-common%{?pkgsuffix}
    %systemd_preun ksm.service
    %systemd_preun ksmtuned.service

%postun -n qemu-kvm-common%{?pkgsuffix}
    %systemd_postun_with_restart ksm.service
    %systemd_postun_with_restart ksmtuned.service
%endif

%global kvm_files \
%{_udevdir}/80-kvm.rules

%global qemu_kvm_files \
%{_libexecdir}/qemu-kvm \
%{_datadir}/systemtap/tapset/qemu-kvm.stp \
%{_datadir}/systemtap/tapset/qemu-kvm-simpletrace.stp \
%{_datadir}/%{pkgname}/trace-events \
%{_datadir}/%{pkgname}/systemtap/script.d/qemu_kvm.stp \
%{_datadir}/%{pkgname}/systemtap/conf.d/qemu_kvm.conf

%if %{rhev}
%files -n qemu-kvm-common%{?pkgsuffix}
    %defattr(-,root,root)
    %dir %{qemudocdir}
    %doc %{qemudocdir}/Changelog
    %doc %{qemudocdir}/README
    %doc %{qemudocdir}/qemu-doc.html
    %doc %{qemudocdir}/qemu-tech.html
    %doc %{qemudocdir}/qmp-commands.txt
    %doc %{qemudocdir}/COPYING
    %doc %{qemudocdir}/COPYING.LIB
    %doc %{qemudocdir}/LICENSE
    %doc %{qemudocdir}/README.rhel6-gpxe-source
    %doc %{qemudocdir}/README.systemtap
    %dir %{_datadir}/%{pkgname}/
    %{_datadir}/%{pkgname}/keymaps/
    %{_mandir}/man1/%{pkgname}.1*
    %attr(4755, -, -) %{_libexecdir}/qemu-bridge-helper
    %config(noreplace) %{_sysconfdir}/sasl2/%{pkgname}.conf
    %{_unitdir}/ksm.service
    %{_libexecdir}/ksmctl
    %config(noreplace) %{_sysconfdir}/sysconfig/ksm
    %{_unitdir}/ksmtuned.service
    %{_sbindir}/ksmtuned
    %config(noreplace) %{_sysconfdir}/ksmtuned.conf
    %dir %{_sysconfdir}/%{pkgname}
    %config(noreplace) %{_sysconfdir}/%{pkgname}/bridge.conf
    %{_datadir}/%{pkgname}/simpletrace.py*
    %{_datadir}/%{pkgname}/tracetool/*.py*
    %{_datadir}/%{pkgname}/tracetool/backend/*.py*
    %{_datadir}/%{pkgname}/tracetool/format/*.py*
%endif

%if %{with guest_agent}
%files -n qemu-guest-agent
    %defattr(-,root,root,-)
    %doc COPYING README
    %{_bindir}/qemu-ga
    %{_unitdir}/qemu-guest-agent.service
    %{_udevdir}/99-qemu-guest-agent.rules
    %{_sysconfdir}/sysconfig/qemu-ga
    %{_sysconfdir}/qemu-ga
    %{_datadir}/%{name}/qemu-ga
    %dir %{_localstatedir}/log/qemu-ga
%endif

%if %{rhev}
%files
    %defattr(-,root,root)
    %ifarch x86_64
        %{_datadir}/%{pkgname}/acpi-dsdt.aml
        %{_datadir}/%{pkgname}/q35-acpi-dsdt.aml
        %{_datadir}/%{pkgname}/bios.bin
        %{_datadir}/%{pkgname}/bios-256k.bin
        %{_datadir}/%{pkgname}/linuxboot.bin
        %{_datadir}/%{pkgname}/multiboot.bin
        %{_datadir}/%{pkgname}/kvmvapic.bin
    %endif
    %{_datadir}/%{pkgname}/sgabios.bin
    %ifnarch aarch64
        %{_datadir}/%{pkgname}/vgabios.bin
        %{_datadir}/%{pkgname}/vgabios-cirrus.bin
        %{_datadir}/%{pkgname}/vgabios-qxl.bin
        %{_datadir}/%{pkgname}/vgabios-stdvga.bin
        %{_datadir}/%{pkgname}/vgabios-vmware.bin
    %endif
    %{_datadir}/%{pkgname}/pxe-e1000.rom
    %{_datadir}/%{pkgname}/pxe-virtio.rom
    %{_datadir}/%{pkgname}/pxe-pcnet.rom
    %{_datadir}/%{pkgname}/pxe-rtl8139.rom
    %{_datadir}/%{pkgname}/pxe-ne2k_pci.rom
    %{_datadir}/%{pkgname}/qemu-icon.bmp
    %{_datadir}/%{pkgname}/qemu_logo_no_text.svg
    %{_datadir}/%{pkgname}/rhel6-virtio.rom
    %{_datadir}/%{pkgname}/rhel6-pcnet.rom
    %{_datadir}/%{pkgname}/rhel6-rtl8139.rom
    %{_datadir}/%{pkgname}/rhel6-ne2k_pci.rom
    %{_datadir}/%{pkgname}/rhel6-e1000.rom
    %ifarch %{power64}
        %{_datadir}/%{pkgname}/spapr-rtas.bin
        %{_datadir}/%{pkgname}/u-boot.e500
    %endif
    %config(noreplace) %{_sysconfdir}/%{pkgname}/target-x86_64.conf
    %{?kvm_files:}
    %{?qemu_kvm_files:}
    %if 0%{have_kvm_setup}
        %{_prefix}/lib/systemd/kvm-setup
	%{_unitdir}/kvm-setup.service
	%{_presetdir}/85-kvm.preset
    %endif

%files -n qemu-kvm-tools%{?pkgsuffix}
    %defattr(-,root,root,-)
    %{_bindir}/kvm_stat

%files -n qemu-img%{?pkgsuffix}
%defattr(-,root,root)
%{_bindir}/qemu-img
%{_bindir}/qemu-io
%{_bindir}/qemu-nbd
%{_mandir}/man1/qemu-img.1*
%{_mandir}/man8/qemu-nbd.8*

%files -n libcacard%{?pkgsuffix}
%defattr(-,root,root,-)
%{_libdir}/libcacard.so.*

%files -n libcacard-tools%{?pkgsuffix}
%defattr(-,root,root,-)
%{_bindir}/vscclient

%files -n libcacard-devel%{?pkgsuffix}
%defattr(-,root,root,-)
%{_includedir}/cacard
%{_libdir}/libcacard.so
%{_libdir}/pkgconfig/libcacard.pc
%endif

%changelog
* Fri May 08 2015 Miroslav Rezanina <mrezanin@redhat.com> - rhev-2.1.2-23.el7_1.3
- kvm-fdc-force-the-fifo-access-to-be-in-bounds-of-the-all.patch [bz#1219271]
- Resolves: bz#1219271
  (CVE-2015-3456 qemu-kvm-rhev: qemu: floppy disk controller flaw [rhel-7.1.z])

* Tue Apr 21 2015 Miroslav Rezanina <mrezanin@redhat.com> - rhev-2.1.2-23.el7_1_1.2
- kvm-block-Fix-max-nb_sectors-in-bdrv_make_zero.patch [bz#1203543]
- Resolves: bz#1203543
  (bdrv_make_zero() passes a too large nb_sectors value to bdrv_write_zeroes())

* Fri Feb 20 2015 Miroslav Rezanina <mrezanin@redhat.com> - rhev-2.1.2-23.el7_1.1
- kvm-pc-acpi-mark-all-possible-CPUs-as-enabled-in-SRAT.patch [bz#1191385]
- kvm-pc-add-rhel6.6.0-machine-type.patch [bz#1194552]
- Resolves: bz#1191385
  ("-numa node" option cause windows guest can not online hot-added CPUs)
- Resolves: bz#1194552
  (Add rhel-6.6.0 machine type to RHEL 7.1.z to support RHEL 6.6 to RHEL 7.1 live migration)

* Tue Jan 27 2015 Miroslav Rezanina <mrezanin@redhat.com> - rhev-2.1.2-23.el7
- kvm-block-qapi-move-string-allocation-from-stack-to-the-.patch [bz#1117170]
- kvm-block-remove-unused-variable-in-bdrv_commit.patch [bz#1117170]
- kvm-block-mirror-change-string-allocation-to-2-bytes.patch [bz#1117170]
- kvm-block-update-string-sizes-for-filename-backing_file-.patch [bz#1117170]
- Resolves: bz#1117170
  (RHEV: Cannot start VMs that have more than 23 snapshots.)

* Mon Jan 26 2015 Miroslav Rezanina <mrezanin@redhat.com> - rhev-2.1.2-22.el7
- kvm-vfio-pci-Fix-interrupt-disabling.patch [bz#1170871]
- kvm-cirrus-fix-blit-region-check.patch [bz#1169457]
- kvm-cirrus-don-t-overflow-CirrusVGAState-cirrus_bltbuf.patch [bz#1169457]
- Resolves: bz#1169457
  (CVE-2014-8106 qemu-kvm-rhev: qemu: cirrus: insufficient blit region checks [rhel-7.1])
- Resolves: bz#1170871
  (qemu core dumped when unhotplug gpu card assigned to guest)

* Fri Jan 23 2015 Jeff E. Nelson <jen@redhat.com> - rhev-2.1.2-21.el7
- kvm-seccomp-add-mlockall-to-whitelist.patch [bz#1182494]
- kvm-seccomp-add-mbind-to-the-syscall-whitelist.patch [bz#1172473]
- kvm-ich9-add-disable_s3-disable_s4-s4_val-properties.patch [bz#1170533]
- kvm-q35-disable-s3-s4-by-default.patch [bz#1170533]
- Resolves: bz#1170533
  (Should disalbe S3/S4 in default  under Q35 machine type in rhel7)
- Resolves: bz#1172473
  (BUG: seccomp filter failure with "-object memory-backend-ram")
- Resolves: bz#1182494
  (BUG: qemu-kvm hang when enabled both sandbox and mlock)

* Thu Jan 15 2015 Miroslav Rezanina <mrezanin@redhat.com> - rhev-2.1.2-20.el7
- kvm-pc-fix-usage-of-x86_cpu_compat_disable_kvm_features.patch [bz#1182233]
- Resolves: bz#1182233
  (Machine type rhel6.5.0 does not use kvmclock due to typo)

* Tue Jan 13 2015 Miroslav Rezanina <mrezanin@redhat.com> - rhev-2.1.2-19.el7
- kvm-smbios-Fix-dimm-size-calculation-when-RAM-is-multipl.patch [bz#1179165]
- kvm-smbios-Don-t-report-unknown-CPU-speed-fix-SVVP-regre.patch [bz#1177127]
- Resolves: bz#1177127
  ([SVVP]smbios HCT job failed with  'Processor Max Speed cannot be Unknown' with -M pc-i440fx-rhel7.1.0)
- Resolves: bz#1179165
  ([SVVP]smbios HCT job failed with  Unspecified error  with -M pc-i440fx-rhel7.1.0)

* Thu Jan 08 2015 Miroslav Rezanina <mrezanin@redhat.com> - rhev-2.1.2-18.el7
- kvm-vl-Adjust-the-place-of-calling-mlockall-to-speedup-V.patch [bz#1173394]
- kvm-block-delete-cow-block-driver.patch [bz#1175841]
- Resolves: bz#1173394
  (numa_smaps doesn't respect bind policy with huge page)
- Resolves: bz#1175841
  (Delete cow block driver)

* Tue Dec 16 2014 Jeff E. Nelson <jen@redhat.com> - rhev-2.1.2-17.el7
- kvm-numa-Don-t-allow-memdev-on-RHEL-6-machine-types.patch [bz#1170093]
- kvm-block-allow-bdrv_unref-to-be-passed-NULL-pointers.patch [bz#1136381]
- kvm-block-vdi-use-block-layer-ops-in-vdi_create-instead-.patch [bz#1136381]
- kvm-block-use-the-standard-ret-instead-of-result.patch [bz#1136381]
- kvm-block-vpc-use-block-layer-ops-in-vpc_create-instead-.patch [bz#1136381]
- kvm-block-iotest-update-084-to-test-static-VDI-image-cre.patch [bz#1136381]
- kvm-block-remove-BLOCK_OPT_NOCOW-from-vdi_create_opts.patch [bz#1136381]
- kvm-block-remove-BLOCK_OPT_NOCOW-from-vpc_create_opts.patch [bz#1136381]
- kvm-migration-fix-parameter-validation-on-ram-load-CVE-2.patch [bz#1163079]
- kvm-qdev-monitor-fix-segmentation-fault-on-qdev_device_h.patch [bz#1169280]
- kvm-block-migration-Disable-cache-invalidate-for-incomin.patch [bz#1171552]
- kvm-acpi-Use-apic_id_limit-when-calculating-legacy-ACPI-.patch [bz#1173167]
- Resolves: bz#1136381
  (RFE: Supporting creating vdi/vpc format disk with protocols (glusterfs) for qemu-kvm-rhev-2.1.x)
- Resolves: bz#1163079
  (CVE-2014-7840 qemu-kvm-rhev: qemu: insufficient parameter validation during ram load [rhel-7.1])
- Resolves: bz#1169280
  (Segfault while query device properties (ics, icp))
- Resolves: bz#1170093
  (guest NUMA failed to migrate when machine is rhel6.5.0)
- Resolves: bz#1171552
  (Storage vm migration failed when running BurnInTes)
- Resolves: bz#1173167
  (Corrupted ACPI tables in some configurations using pc-i440fx-rhel7.0.0)

* Fri Dec 05 2014 Miroslav Rezanina <mrezanin@redhat.com> - rhev-2.1.2-16.el7
- kvm-qemu-iotests-Fix-broken-test-cases.patch [bz#1169589]
- kvm-Fix-for-crash-after-migration-in-virtio-rng-on-bi-en.patch [bz#1165087]
- kvm-Downstream-only-remove-unsupported-machines-from-AAr.patch [bz#1169847]
- Resolves: bz#1165087
  (QEMU core dumped for the destination guest when do migating guest to file)
- Resolves: bz#1169589
  (test case 051 071 and 087 of qemu-iotests fail for qcow2 with qemu-kvm-rhev-2.1.2-14.el7)
- Resolves: bz#1169847
  (only support mach-virt)

* Tue Dec 02 2014 Miroslav Rezanina <mrezanin@redhat.com> - rhev-2.1.2-15.el7
- kvm-scsi-Optimize-scsi_req_alloc.patch [bz#1141656]
- kvm-virtio-scsi-Optimize-virtio_scsi_init_req.patch [bz#1141656]
- kvm-virtio-scsi-Fix-comment-for-VirtIOSCSIReq.patch [bz#1141656]
- kvm-Downstream-only-Move-daemon-reload-to-make-sure-new-.patch [bz#1168085]
- Resolves: bz#1141656
  (Virtio-scsi: performance degradation from 1.5.3 to 2.1.0)
- Resolves: bz#1168085
  (qemu-kvm-rhev install scripts sometimes don't recognize newly installed systemd presets)

* Thu Nov 27 2014 Miroslav Rezanina <mrezanin@redhat.com> - rhev-2.1.2-14.el7
- kvm-xhci-add-sanity-checks-to-xhci_lookup_uport.patch [bz#1161397]
- kvm-qemu-img-Allow-source-cache-mode-specification.patch [bz#1166481]
- kvm-qemu-img-Allow-cache-mode-specification-for-amend.patch [bz#1166481]
- kvm-qemu-img-fix-img_compare-flags-error-path.patch [bz#1166481]
- kvm-qemu-img-clarify-src_cache-option-documentation.patch [bz#1166481]
- kvm-qemu-img-fix-rebase-src_cache-option-documentation.patch [bz#1166481]
- Resolves: bz#1161397
  (qemu core dump when install a RHEL.7 guest(xhci) with migration)
- Resolves: bz#1166481
  (Allow qemu-img to bypass the host cache (check, compare, convert, rebase, amend))

* Tue Nov 25 2014 Miroslav Rezanina <mrezanin@redhat.com> - rhev-2.1.2-13.el7
- kvm-hw-pci-fixed-error-flow-in-pci_qdev_init.patch [bz#1166067]
- kvm-hw-pci-fixed-hotplug-crash-when-using-rombar-0-with-.patch [bz#1166067]
- Resolves: bz#1166067
  (qemu-kvm aborted when hot plug PCI device to guest with romfile and rombar=0)

* Fri Nov 21 2014 Miroslav Rezanina <mrezanin@redhat.com> - rhev-2.1.2-12.el7
- kvm-migration-static-variables-will-not-be-reset-at-seco.patch [bz#1166501]
- Resolves: bz#1166501
  (Migration "expected downtime" does not refresh after reset to a new value)

* Fri Nov 21 2014 Miroslav Rezanina <mrezanin@redhat.com> - rhev-2.1.2-11.el7
- kvm-iscsi-Refuse-to-open-as-writable-if-the-LUN-is-write.patch [bz#1160102]
- kvm-vnc-sanitize-bits_per_pixel-from-the-client.patch [bz#1157646]
- kvm-usb-host-fix-usb_host_speed_compat-tyops.patch [bz#1160504]
- kvm-block-raw-posix-Fix-disk-corruption-in-try_fiemap.patch [bz#1142331]
- kvm-block-raw-posix-use-seek_hole-ahead-of-fiemap.patch [bz#1142331]
- kvm-raw-posix-Fix-raw_co_get_block_status-after-EOF.patch [bz#1142331]
- kvm-raw-posix-raw_co_get_block_status-return-value.patch [bz#1142331]
- kvm-raw-posix-SEEK_HOLE-suffices-get-rid-of-FIEMAP.patch [bz#1142331]
- kvm-raw-posix-The-SEEK_HOLE-code-is-flawed-rewrite-it.patch [bz#1142331]
- kvm-exec-Handle-multipage-ranges-in-invalidate_and_set_d.patch [bz#1164759]
- Resolves: bz#1142331
  (qemu-img convert intermittently corrupts output images)
- Resolves: bz#1157646
  (CVE-2014-7815 qemu-kvm-rhev: qemu: vnc: insufficient bits_per_pixel from the client sanitization [rhel-7.1])
- Resolves: bz#1160102
  (opening read-only iscsi lun as read-write should fail)
- Resolves: bz#1160504
  (guest can not show usb device after adding some usb controllers and redirdevs.)
- Resolves: bz#1164759
  (Handle multipage ranges in invalidate_and_set_dirty())

* Thu Nov 20 2014 Miroslav Rezanina <mrezanin@redhat.com> - rhev-2.1.2-10.el7
- kvm-pc-dimm-Don-t-check-dimm-node-when-there-is-non-NUMA.patch [bz#1150510 bz#1163735]
- kvm-vga-Start-cutting-out-non-32bpp-conversion-support.patch [bz#1146809]
- kvm-vga-Remove-remainder-of-old-conversion-cruft.patch [bz#1146809]
- kvm-vga-Separate-LE-and-BE-conversion-functions.patch [bz#1146809]
- kvm-vga-Remove-rgb_to_pixel-indirection.patch [bz#1146809]
- kvm-vga-Simplify-vga_draw_blank-a-bit.patch [bz#1146809]
- kvm-cirrus-Remove-non-32bpp-cursor-drawing.patch [bz#1146809]
- kvm-vga-Remove-some-should-be-done-in-BIOS-comments.patch [bz#1146809]
- kvm-vga-Rename-vga_template.h-to-vga-helpers.h.patch [bz#1146809]
- kvm-vga-Make-fb-endian-a-common-state-variable.patch [bz#1146809]
- kvm-vga-Add-endian-to-vmstate.patch [bz#1146809]
- kvm-vga-pci-add-qext-region-to-mmio.patch [bz#1146809]
- kvm-virtio-scsi-work-around-bug-in-old-BIOSes.patch [bz#1123812]
- kvm-Revert-Downstream-only-Add-script-to-autoload-KVM-mo.patch [bz#1158250 bz#1159706]
- kvm-Downstream-only-add-script-on-powerpc-to-configure-C.patch [bz#1158250 bz#1158251 bz#1159706]
- kvm-block-New-bdrv_nb_sectors.patch [bz#1132385]
- kvm-vmdk-Optimize-cluster-allocation.patch [bz#1132385]
- kvm-vmdk-Handle-failure-for-potentially-large-allocation.patch [bz#1132385]
- kvm-vmdk-Use-bdrv_nb_sectors-where-sectors-not-bytes-are.patch [bz#1132385]
- kvm-vmdk-fix-vmdk_parse_extents-extent_file-leaks.patch [bz#1132385]
- kvm-vmdk-fix-buf-leak-in-vmdk_parse_extents.patch [bz#1132385]
- kvm-vmdk-Fix-integer-overflow-in-offset-calculation.patch [bz#1132385]
- kvm-Revert-Build-ceph-rbd-only-for-rhev.patch [bz#1140744]
- kvm-Revert-rbd-Only-look-for-qemu-specific-copy-of-librb.patch [bz#1140744]
- kvm-Revert-rbd-link-and-load-librbd-dynamically.patch [bz#1140744]
- kvm-spec-Enable-rbd-driver-add-dependency.patch [bz#1140744]
- kvm-Use-qemu-kvm-in-documentation-instead-of-qemu-system.patch [bz#1140620]
- kvm-ide-stash-aiocb-for-flushes.patch [bz#1024599]
- kvm-ide-simplify-reset-callbacks.patch [bz#1024599]
- kvm-ide-simplify-set_inactive-callbacks.patch [bz#1024599]
- kvm-ide-simplify-async_cmd_done-callbacks.patch [bz#1024599]
- kvm-ide-simplify-start_transfer-callbacks.patch [bz#1024599]
- kvm-ide-wrap-start_dma-callback.patch [bz#1024599]
- kvm-ide-remove-wrong-setting-of-BM_STATUS_INT.patch [bz#1024599]
- kvm-ide-fold-add_status-callback-into-set_inactive.patch [bz#1024599]
- kvm-ide-move-BM_STATUS-bits-to-pci.-ch.patch [bz#1024599]
- kvm-ide-move-retry-constants-out-of-BM_STATUS_-namespace.patch [bz#1024599]
- kvm-ahci-remove-duplicate-PORT_IRQ_-constants.patch [bz#1024599]
- kvm-ide-stop-PIO-transfer-on-errors.patch [bz#1024599]
- kvm-ide-make-all-commands-go-through-cmd_done.patch [bz#1024599]
- kvm-ide-atapi-Mark-non-data-commands-as-complete.patch [bz#1024599]
- kvm-ahci-construct-PIO-Setup-FIS-for-PIO-commands.patch [bz#1024599]
- kvm-ahci-properly-shadow-the-TFD-register.patch [bz#1024599]
- kvm-ahci-Correct-PIO-D2H-FIS-responses.patch [bz#1024599]
- kvm-ahci-Update-byte-count-after-DMA-completion.patch [bz#1024599]
- kvm-ahci-Fix-byte-count-regression-for-ATAPI-PIO.patch [bz#1024599]
- kvm-ahci-Fix-SDB-FIS-Construction.patch [bz#1024599]
- kvm-vhost-user-fix-mmap-offset-calculation.patch [bz#1159710]
- Resolves: bz#1024599
  (Windows7 x86 guest with ahci backend hit BSOD when do "hibernate")
- Resolves: bz#1123812
  (Reboot guest and guest's virtio-scsi disk will be lost after forwards migration (from RHEL6.6 host to RHEL7.1 host))
- Resolves: bz#1132385
  (qemu-img convert rate about 100k/second from qcow2/raw to vmdk format on nfs system file)
- Resolves: bz#1140620
  (Should replace "qemu-system-i386" by "/usr/libexec/qemu-kvm" in manpage of qemu-kvm for our official qemu-kvm build)
- Resolves: bz#1140744
  (Enable native support for Ceph)
- Resolves: bz#1146809
  (Incorrect colours on virtual VGA with ppc64le guest under ppc64 host)
- Resolves: bz#1150510
  (kernel ignores ACPI memory devices (PNP0C80) present at boot time)
- Resolves: bz#1158250
  (KVM modules are not autoloaded on POWER hosts)
- Resolves: bz#1158251
  (POWER KVM host starts by default with threads enabled, which prevents running guests)
- Resolves: bz#1159706
  (Need means to configure subcore mode for RHEL POWER8 hosts)
- Resolves: bz#1159710
  (vhost-user:Bad ram offset)
- Resolves: bz#1163735
  (-device pc-dimm fails to initialize on non-NUMA configs)

* Wed Nov 19 2014 Miroslav Rezanina <mrezanin@redhat.com> - rhev-2.1.2-9.el7
- kvm-aarch64-raise-max_cpus-to-8.patch [bz#1160325]
- kvm-hw-arm-virt-add-linux-stdout-path-to-chosen-DT-node.patch [bz#1160325]
- kvm-hw-arm-virt-Provide-flash-devices-for-boot-ROMs.patch [bz#1160325]
- kvm-hw-arm-boot-load-DTB-as-a-ROM-image.patch [bz#1160325]
- kvm-hw-arm-boot-pass-an-address-limit-to-and-return-size.patch [bz#1160325]
- kvm-hw-arm-boot-load-device-tree-to-base-of-DRAM-if-no-k.patch [bz#1160325]
- kvm-hw-arm-boot-enable-DTB-support-when-booting-ELF-imag.patch [bz#1160325]
- kvm-hw-arm-virt-mark-timer-in-fdt-as-v8-compatible.patch [bz#1160325]
- kvm-hw-arm-boot-register-cpu-reset-handlers-if-using-bio.patch [bz#1160325]
- kvm-Downstream-only-Declare-ARM-kernel-support-read-only.patch [bz#1160325]
- Resolves: bz#1160325
  (arm64: support aavmf)

* Thu Nov 13 2014 Miroslav Rezanina <mrezanin@redhat.com> - rhev-2.1.2-8.el7
- kvm-ide-Add-wwn-support-to-IDE-ATAPI-drive.patch [bz#1150820]
- kvm-exec-report-error-when-memory-hpagesize.patch [bz#1147354]
- kvm-exec-add-parameter-errp-to-gethugepagesize.patch [bz#1147354]
- kvm-block-curl-Improve-type-safety-of-s-timeout.patch [bz#1152901]
- kvm-virtio-serial-avoid-crash-when-port-has-no-name.patch [bz#1151947]
- Resolves: bz#1147354
  (Qemu core dump when boot up a guest on a non-existent hugepage path)
- Resolves: bz#1150820
  (fail to specify wwn for virtual IDE CD-ROM)
- Resolves: bz#1151947
  (virtconsole causes qemu-kvm core dump)
- Resolves: bz#1152901
  (block/curl: Fix type safety of s->timeout)

* Thu Nov 06 2014 Miroslav Rezanina <mrezanin@redhat.com> - rhev-2.1.2-7.el7
- kvm-ac97-register-reset-via-qom.patch [bz#1141666]
- kvm-specfile-Require-glusterfs-api-3.6.patch [bz#1157329]
- kvm-smbios-Fix-assertion-on-socket-count-calculation.patch [bz#1146573]
- kvm-smbios-Encode-UUID-according-to-SMBIOS-specification.patch [bz#1152922]
- kvm-virtio-scsi-Report-error-if-num_queues-is-0-or-too-l.patch [bz#1146826]
- kvm-virtio-scsi-Fix-memory-leak-when-realize-failed.patch [bz#1146826]
- kvm-virtio-scsi-Fix-num_queue-input-validation.patch [bz#1146826]
- kvm-util-Improve-os_mem_prealloc-error-message.patch [bz#1153590]
- kvm-Downstream-only-Add-script-to-autoload-KVM-modules-o.patch [bz#1158250]
- kvm-Downstream-only-remove-uneeded-PCI-devices-for-POWER.patch [bz#1160120]
- kvm-Downstream-only-Remove-assorted-unneeded-devices-for.patch [bz#1160120]
- kvm-Downstream-only-Remove-ISA-bus-and-device-support-fo.patch [bz#1160120]
- kvm-well-defined-listing-order-for-machine-types.patch [bz#1145042]
- kvm-i386-pc-add-piix-and-q35-machtypes-to-sorting-famili.patch [bz#1145042]
- kvm-i386-pc-add-RHEL-machtypes-to-sorting-families-for-M.patch [bz#1145042]
- Resolves: bz#1141666
  (Qemu crashed if reboot guest after hot remove AC97 sound device)
- Resolves: bz#1145042
  (The output of "/usr/libexec/qemu-kvm -M ?" should be ordered.)
- Resolves: bz#1146573
  (qemu core dump when boot guest with smp(num)<cores(num))
- Resolves: bz#1146826
  (QEMU will not reject invalid number of queues (num_queues = 0) specified for virtio-scsi)
- Resolves: bz#1152922
  (smbios uuid mismatched)
- Resolves: bz#1153590
  (Improve error message on huge page preallocation)
- Resolves: bz#1157329
  (qemu-kvm: undefined symbol: glfs_discard_async)
- Resolves: bz#1158250
  (KVM modules are not autoloaded on POWER hosts)
- Resolves: bz#1160120
  (qemu-kvm-rhev shouldn't include non supported devices for POWER)

* Tue Nov 04 2014 Miroslav Rezanina <mrezanin@redhat.com> - rhev-2.1.2-6.el7
- kvm-ivshmem-use-error_report.patch [bz#1104063]
- kvm-ivshmem-RHEL-only-remove-unsupported-code.patch [bz#1104063]
- kvm-ivshmem-RHEL-only-explicitly-remove-dead-code.patch [bz#1104063]
- kvm-Revert-rhel-Drop-ivshmem-device.patch [bz#1104063]
- kvm-serial-reset-state-at-startup.patch [bz#1135844]
- kvm-spice-call-qemu_spice_set_passwd-during-init.patch [bz#1140975]
- kvm-input-fix-send-key-monitor-command-release-event-ord.patch [bz#1145028 bz#1146801]
- kvm-virtio-scsi-sense-in-virtio_scsi_command_complete.patch [bz#1152830]
- Resolves: bz#1104063
  ([RHEL7.1 Feat] Enable qemu-kvm Inter VM Shared Memory (IVSHM) feature)
- Resolves: bz#1135844
  ([virtio-win]communication ports were marked with a  yellow exclamation after hotplug pci-serial,pci-serial-2x,pci-serial-4x)
- Resolves: bz#1140975
  (fail to login spice session with password + expire time)
- Resolves: bz#1145028
  (send-key does not crash windows guest even when it should)
- Resolves: bz#1146801
  (sendkey: releasing order of combined keys was wrongly converse)
- Resolves: bz#1152830
  (Fix sense buffer in virtio-scsi LUN passthrough)

* Fri Oct 24 2014 Miroslav Rezanina <mrezanin@redhat.com> - rhev-2.1.2-5.el7
- kvm-blockdev-Orphaned-drive-search.patch [bz#946993]
- kvm-blockdev-Allow-overriding-if_max_dev-property.patch [bz#946993]
- kvm-pc-vl-Add-units-per-default-bus-property.patch [bz#946993]
- kvm-ide-Update-ide_drive_get-to-be-HBA-agnostic.patch [bz#946993]
- kvm-qtest-bios-tables-Correct-Q35-command-line.patch [bz#946993]
- kvm-q35-ahci-Pick-up-cdrom-and-hda-options.patch [bz#946993]
- kvm-trace-events-drop-orphan-virtio_blk_data_plane_compl.patch [bz#1144325]
- kvm-trace-events-drop-orphan-usb_mtp_data_out.patch [bz#1144325]
- kvm-trace-events-drop-orphan-iscsi-trace-events.patch [bz#1144325]
- kvm-cleanup-trace-events.pl-Tighten-search-for-trace-eve.patch [bz#1144325]
- kvm-trace-events-Drop-unused-megasas-trace-event.patch [bz#1144325]
- kvm-trace-events-Drop-orphaned-monitor-trace-event.patch [bz#1144325]
- kvm-trace-events-Fix-comments-pointing-to-source-files.patch [bz#1144325]
- kvm-simpletrace-add-simpletrace.py-no-header-option.patch [bz#1155015]
- kvm-trace-extract-stap_escape-function-for-reuse.patch [bz#1155015]
- kvm-trace-add-tracetool-simpletrace_stap-format.patch [bz#1155015]
- kvm-trace-install-simpletrace-SystemTap-tapset.patch [bz#1155015]
- kvm-trace-install-trace-events-file.patch [bz#1155015]
- kvm-trace-add-SystemTap-init-scripts-for-simpletrace-bri.patch [bz#1155015]
- kvm-simpletrace-install-simpletrace.py.patch [bz#1155015]
- kvm-trace-add-systemtap-initscript-README-file-to-RPM.patch [bz#1155015]
- Resolves: bz#1144325
  (Can not probe  "qemu.kvm.virtio_blk_data_plane_complete_request")
- Resolves: bz#1155015
  ([Fujitsu 7.1 FEAT]:QEMU: capturing trace data all the time using ftrace-based tracing)
- Resolves: bz#946993
  (Q35 does not honor -drive if=ide,... and its sugared forms -cdrom, -hda, ...)

* Mon Oct 20 2014 Miroslav Rezanina <mrezanin@redhat.com> - rhev-2.1.2-4.el7
- kvm-seccomp-add-semctl-to-the-syscall-whitelist.patch [bz#1126704]
- kvm-dataplane-fix-virtio_blk_data_plane_create-op-blocke.patch [bz#1140001]
- kvm-block-fix-overlapping-multiwrite-requests.patch [bz#1123908]
- kvm-qemu-iotests-add-multiwrite-test-cases.patch [bz#1123908]
- Resolves: bz#1123908
  (block.c: multiwrite_merge() truncates overlapping requests)
- Resolves: bz#1126704
  (BUG: When use '-sandbox on'+'vnc'+'hda' and quit, qemu-kvm hang)
- Resolves: bz#1140001
  (data-plane hotplug should be refused to start if device is already in use (drive-mirror job))

* Fri Oct 10 2014 Miroslav Rezanina <mrezanin@redhat.com> - rhev-2.1.2-3.el7
- kvm-Disable-tests-for-removed-features.patch [bz#1108040]
- kvm-Disable-arm-board-types-using-lsi53c895a.patch [bz#1108040]
- kvm-libqtest-launch-QEMU-with-QEMU_AUDIO_DRV-none.patch [bz#1108040]
- kvm-Whitelist-blkdebug-driver.patch [bz#1108040]
- kvm-Turn-make-check-on.patch [bz#1108040]
- Resolves: bz#1108040
  (Enable make check for qemu-kvm-rhev 2.0 and newer)

* Fri Oct 10 2014 Miroslav Rezanina <mrezanin@redhat.com> - rhev-2.1.2-2.el7
- kvm-RPM-spec-Add-enable-numa-to-configure-command-line.patch [bz#1076990]
- kvm-block.curl-adding-timeout-option.patch [bz#1132569]
- kvm-curl-Allow-a-cookie-or-cookies-to-be-sent-with-http-.patch [bz#1132569]
- kvm-curl-Don-t-deref-NULL-pointer-in-call-to-aio_poll.patch [bz#1132569]
- kvm-curl-Add-timeout-and-cookie-options-and-misc.-fix-RH.patch [bz#1132569]
- kvm-Introduce-cpu_clean_all_dirty.patch [bz#1143054]
- kvm-kvmclock-Ensure-proper-env-tsc-value-for-kvmclock_cu.patch [bz#1143054]
- kvm-kvmclock-Ensure-time-in-migration-never-goes-backwar.patch [bz#1143054]
- kvm-IDE-Fill-the-IDENTIFY-request-consistently.patch [bz#852348]
- kvm-ide-Add-resize-callback-to-ide-core.patch [bz#852348]
- kvm-virtio-balloon-fix-integer-overflow-in-memory-stats-.patch [bz#1140997]
- kvm-block-extend-BLOCK_IO_ERROR-event-with-nospace-indic.patch [bz#1117445]
- kvm-block-extend-BLOCK_IO_ERROR-with-reason-string.patch [bz#1117445]
- Resolves: bz#1076990
  (Enable complex memory requirements for virtual machines)
- Resolves: bz#1117445
  (QMP: extend block events with error information)
- Resolves: bz#1132569
  (RFE: Enable curl driver in qemu-kvm-rhev: https only)
- Resolves: bz#1140997
  (guest is stuck when setting balloon memory with large guest-stats-polling-interval)
- Resolves: bz#1143054
  (kvmclock: Ensure time in migration never goes backward (backport))
- Resolves: bz#852348
  (fail to block_resize local data disk with IDE/AHCI disk_interface)

* Fri Sep 26 2014 Miroslav Rezanina <mrezanin@redhat.com> - rhev-2.1.2-1.el7
- Rebase to qemu 2.1.2 [bz#1121609]
- Resolves: bz#1121609
  Rebase qemu-kvm-rhev to qemu 2.1.2

* Wed Sep 24 2014 Miroslav Rezanina <mrezanin@redhat.com> - rhev-2.1.0-5.el7
- kvm-target-i386-Reject-invalid-CPU-feature-names-on-the-.patch [bz#1055532]
- kvm-target-ppc-virtex-ml507-machine-type-should-depend-o.patch [bz#1113998]
- kvm-RHEL-only-Disable-tests-that-don-t-work-with-RHEL-bu.patch [bz#1113998]
- kvm-RHEL-onlyy-Disable-unused-ppc-machine-types.patch [bz#1113998]
- kvm-RHEL-only-Remove-unneeded-devices-from-ppc64-qemu-kv.patch []
- kvm-RHEL-only-Replace-upstream-pseries-machine-types-wit.patch []
- kvm-scsi-bus-prepare-scsi_req_new-for-introduction-of-pa.patch [bz#1123349]
- kvm-scsi-bus-introduce-parse_cdb-in-SCSIDeviceClass-and-.patch [bz#1123349]
- kvm-scsi-block-extract-scsi_block_is_passthrough.patch [bz#1123349]
- kvm-scsi-block-scsi-generic-implement-parse_cdb.patch [bz#1123349]
- kvm-virtio-scsi-implement-parse_cdb.patch [bz#1123349]
- kvm-exec-file_ram_alloc-print-error-when-prealloc-fails.patch [bz#1135893]
- kvm-pc-increase-maximal-VCPU-count-to-240.patch [bz#1144089]
- kvm-ssh-Enable-ssh-driver-in-qemu-kvm-rhev-RHBZ-1138359.patch [bz#1138359]
- Resolves: bz#1055532
  (QEMU should abort when invalid CPU flag name is used)
- Resolves: bz#1113998
  (RHEL Power/KVM (qemu-kvm-rhev))
- Resolves: bz#1123349
  ([FJ7.0 Bug] SCSI command issued from KVM guest doesn't reach target device)
- Resolves: bz#1135893
  (qemu-kvm should report an error message when host's freehugepage memory < domain's memory)
- Resolves: bz#1138359
  (RFE: Enable ssh driver in qemu-kvm-rhev)
- Resolves: bz#1144089
  ([HP 7.1 FEAT] Increase qemu-kvm-rhev's VCPU limit to 240)

* Wed Sep 17 2014 Miroslav Rezanina <mrezanin@redhat.com> - rhev-2.1.0-4.el7
- kvm-virtio-rng-add-some-trace-events.patch [bz#1129259]
- kvm-block-vhdx-add-error-check.patch [bz#1126976]
- kvm-block-VHDX-endian-fixes.patch [bz#1126976]
- kvm-qdev-monitor-include-QOM-properties-in-device-FOO-he.patch [bz#1133736]
- kvm-block-acquire-AioContext-in-qmp_block_resize.patch [bz#1136752]
- kvm-virtio-blk-allow-block_resize-with-dataplane.patch [bz#1136752]
- kvm-block-acquire-AioContext-in-do_drive_del.patch [bz#1136752]
- kvm-virtio-blk-allow-drive_del-with-dataplane.patch [bz#1136752]
- kvm-rhel-Add-rhel7.1.0-machine-types.patch [bz#1093023]
- kvm-vmstate_xhci_event-bug-compat-for-rhel7.0.0-machine-.patch [bz#1136512]
- kvm-pflash_cfi01-fixup-stale-DPRINTF-calls.patch [bz#1139706]
- kvm-pflash_cfi01-write-flash-contents-to-bdrv-on-incomin.patch [bz#1139706]
- kvm-ide-Fix-segfault-when-flushing-a-device-that-doesn-t.patch [bz#1140145]
- kvm-xhci-PCIe-endpoint-migration-compatibility-fix.patch [bz#1138579]
- kvm-rh-machine-types-xhci-PCIe-endpoint-migration-compat.patch [bz#1138579]
- Resolves: bz#1093023
  (provide RHEL-specific machine types in QEMU)
- Resolves: bz#1126976
  (VHDX image format does not work on PPC64 (Endian issues))
- Resolves: bz#1129259
  (Add traces to virtio-rng device)
- Resolves: bz#1133736
  (qemu should provide iothread and x-data-plane properties for /usr/libexec/qemu-kvm -device virtio-blk-pci,?)
- Resolves: bz#1136512
  (rhel7.0.0 machtype compat after CVE-2014-5263 vmstate_xhci_event: fix unterminated field list)
- Resolves: bz#1136752
  (virtio-blk dataplane support for block_resize and hot unplug)
- Resolves: bz#1138579
  (Migration failed with nec-usb-xhci from RHEL7. 0 to RHEL7.1)
- Resolves: bz#1139706
  (pflash (UEFI varstore) migration shortcut for libvirt [RHEV])
- Resolves: bz#1140145
  (qemu-kvm crashed when doing iofuzz testing)

* Thu Aug 28 2014 Miroslav Rezanina <mrezanin@redhat.com> - rhev-2.1.0-3.el7
- kvm-Fix-pkgversion-value.patch [bz#1064742]
- kvm-virtio-serial-create-a-linked-list-of-all-active-dev.patch [bz#1003432]
- kvm-virtio-serial-search-for-duplicate-port-names-before.patch [bz#1003432]
- kvm-pc-RHEL-6-CPUID-compat-code-for-Broadwell-CPU-model.patch [bz#1111351]
- kvm-rpm-spec-build-qemu-kvm-with-lzo-and-snappy-enabled.patch [bz#1126933]
- Resolves: bz#1003432
  (qemu-kvm should not allow different virtio serial port use the same name)
- Resolves: bz#1064742
  (QMP: "query-version" doesn't include the -rhev prefix from the qemu-kvm-rhev package)
- Resolves: bz#1111351
  (RHEL-6.6 migration compatibility: CPU models)
- Resolves: bz#1126933
  ([FEAT RHEV7.1]: qemu: Support compression for dump-guest-memory command)

* Mon Aug 18 2014 Miroslav Rezanina <> - rhev-2.1.0-2.el7
- kvm-exit-when-no-kvm-and-vcpu-count-160.patch [bz#1076326 bz#1118665]
- kvm-Revert-Use-legacy-SMBIOS-for-rhel-machine-types.patch [bz#1118665]
- kvm-rhel-Use-SMBIOS-legacy-mode-for-machine-types-7.0.patch [bz#1118665]
- kvm-rhel-Suppress-hotplug-memory-address-space-for-machi.patch [bz#1118665]
- kvm-rhel-Fix-ACPI-table-size-for-machine-types-7.0.patch [bz#1118665]
- kvm-rhel-Fix-missing-pc-q35-rhel7.0.0-compatibility-prop.patch [bz#1118665]
- kvm-rhel-virtio-scsi-pci.any_layout-off-for-machine-type.patch [bz#1118665]
- kvm-rhel-PIIX4_PM.memory-hotplug-support-off-for-machine.patch [bz#1118665]
- kvm-rhel-apic.version-0x11-for-machine-types-7.0.patch [bz#1118665]
- kvm-rhel-nec-usb-xhci.superspeed-ports-first-off-for-mac.patch [bz#1118665]
- kvm-rhel-pci-serial.prog_if-0-for-machine-types-7.0.patch [bz#1118665]
- kvm-rhel-virtio-net-pci.guest_announce-off-for-machine-t.patch [bz#1118665]
- kvm-rhel-ICH9-LPC.memory-hotplug-support-off-for-machine.patch [bz#1118665]
- kvm-rhel-.power_controller_present-off-for-machine-types.patch [bz#1118665]
- kvm-rhel-virtio-net-pci.ctrl_guest_offloads-off-for-mach.patch [bz#1118665]
- kvm-pc-q35-rhel7.0.0-Disable-x2apic-default.patch [bz#1118665]
- Resolves: bz#1076326
  (qemu-kvm does not quit when booting guest w/ 161 vcpus and "-no-kvm")
- Resolves: bz#1118665
  (Migration: rhel7.0->rhev7.1)

* Sat Aug 02 2014 Miroslav Rezanina <mrezanin@redhat.com> - rhev-2.1.0-1.el7
- Rebase to 2.1.0 [bz#1121609]
- Resolves: bz#1121609
 (Rebase qemu-kvm-rhev to qemu 2.1)

* Wed Jul 09 2014 Miroslav Rezanina <mrezanin@redhat.com> - rhev-2.0.0-3.el7
- kvm-Remove-CONFIG_NE2000_ISA-from-all-config-files.patch []
- kvm-Fix-conditional-rpmbuild.patch []
- kvm-RHEL7-RHEV7.1-2.0-migration-compatibility.patch [bz#1085950]
- kvm-remove-superfluous-.hot_add_cpu-and-.max_cpus-initia.patch [bz#1085950]
- kvm-set-model-in-PC_RHEL6_5_COMPAT-for-qemu32-VCPU-RHEV-.patch [bz#1085950]
- kvm-Undo-Enable-x2apic-by-default-for-compatibility.patch [bz#1085950]
- kvm-qemu_loadvm_state-shadow-SeaBIOS-for-VM-incoming-fro.patch [bz#1103579]
- Resolves: bz#1085950
  (Migration/virtio-net: 7.0->vp-2.0-rc2: Mix of migration issues)
- Resolves: bz#1103579
  (fail to reboot guest after migration from RHEL6.5 host to RHEL7.0 host)

* Fri May 30 2014 Miroslav Rezanina <mrezanin@redhat.com> - rhev-2.0.0-2.el7
- kvm-pc-add-hot_add_cpu-callback-to-all-machine-types.patch [bz#1093411]
- Resolves: bz#1093411
  (Hot unplug CPU not working for RHEL7 host)

* Fri Apr 18 2014 Miroslav Rezanina <mrezanin@redhat.com> - 2.0.0-1.el7ev
- Rebase to qemu 2.0.0

* Wed Apr 02 2014 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-60.el7
- kvm-qcow2-fix-dangling-refcount-table-entry.patch [bz#1081793]
- kvm-qcow2-link-all-L2-meta-updates-in-preallocate.patch [bz#1081393]
- Resolves: bz#1081393
  (qemu-img will prompt that 'leaked clusters were found' while creating images with '-o preallocation=metadata,cluster_size<=1024')
- Resolves: bz#1081793
  (qemu-img core dumped when creating a qcow2 image base on block device(iscsi or libiscsi))

* Wed Mar 26 2014 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-59.el7
- kvm-qemu-iotests-add-.-check-cloop-support.patch [bz#1066691]
- kvm-qemu-iotests-add-cloop-input-validation-tests.patch [bz#1066691]
- kvm-block-cloop-validate-block_size-header-field-CVE-201.patch [bz#1079455]
- kvm-block-cloop-prevent-offsets_size-integer-overflow-CV.patch [bz#1079320]
- kvm-block-cloop-refuse-images-with-huge-offsets-arrays-C.patch [bz#1079455]
- kvm-block-cloop-refuse-images-with-bogus-offsets-CVE-201.patch [bz#1079455]
- kvm-size-off-by-one.patch [bz#1066691]
- kvm-qemu-iotests-Support-for-bochs-format.patch [bz#1066691]
- kvm-bochs-Unify-header-structs-and-make-them-QEMU_PACKED.patch [bz#1066691]
- kvm-bochs-Use-unsigned-variables-for-offsets-and-sizes-C.patch [bz#1079339]
- kvm-bochs-Check-catalog_size-header-field-CVE-2014-0143.patch [bz#1079320]
- kvm-bochs-Check-extent_size-header-field-CVE-2014-0142.patch [bz#1079315]
- kvm-bochs-Fix-bitmap-offset-calculation.patch [bz#1066691]
- kvm-vpc-vhd-add-bounds-check-for-max_table_entries-and-b.patch [bz#1079455]
- kvm-vpc-Validate-block-size-CVE-2014-0142.patch [bz#1079315]
- kvm-vdi-add-bounds-checks-for-blocks_in_image-and-disk_s.patch [bz#1079455]
- kvm-vhdx-Bounds-checking-for-block_size-and-logical_sect.patch [bz#1079346]
- kvm-curl-check-data-size-before-memcpy-to-local-buffer.-.patch [bz#1079455]
- kvm-qcow2-Check-header_length-CVE-2014-0144.patch [bz#1079455]
- kvm-qcow2-Check-backing_file_offset-CVE-2014-0144.patch [bz#1079455]
- kvm-qcow2-Check-refcount-table-size-CVE-2014-0144.patch [bz#1079455]
- kvm-qcow2-Validate-refcount-table-offset.patch [bz#1066691]
- kvm-qcow2-Validate-snapshot-table-offset-size-CVE-2014-0.patch [bz#1079455]
- kvm-qcow2-Validate-active-L1-table-offset-and-size-CVE-2.patch [bz#1079455]
- kvm-qcow2-Fix-backing-file-name-length-check.patch [bz#1066691]
- kvm-qcow2-Don-t-rely-on-free_cluster_index-in-alloc_refc.patch [bz#1079339]
- kvm-qcow2-Avoid-integer-overflow-in-get_refcount-CVE-201.patch [bz#1079320]
- kvm-qcow2-Check-new-refcount-table-size-on-growth.patch [bz#1066691]
- kvm-qcow2-Fix-types-in-qcow2_alloc_clusters-and-alloc_cl.patch [bz#1066691]
- kvm-qcow2-Protect-against-some-integer-overflows-in-bdrv.patch [bz#1066691]
- kvm-qcow2-Fix-new-L1-table-size-check-CVE-2014-0143.patch [bz#1079320]
- kvm-dmg-coding-style-and-indentation-cleanup.patch [bz#1066691]
- kvm-dmg-prevent-out-of-bounds-array-access-on-terminator.patch [bz#1066691]
- kvm-dmg-drop-broken-bdrv_pread-loop.patch [bz#1066691]
- kvm-dmg-use-appropriate-types-when-reading-chunks.patch [bz#1066691]
- kvm-dmg-sanitize-chunk-length-and-sectorcount-CVE-2014-0.patch [bz#1079325]
- kvm-dmg-use-uint64_t-consistently-for-sectors-and-length.patch [bz#1066691]
- kvm-dmg-prevent-chunk-buffer-overflow-CVE-2014-0145.patch [bz#1079325]
- kvm-block-vdi-bounds-check-qemu-io-tests.patch [bz#1066691]
- kvm-block-Limit-request-size-CVE-2014-0143.patch [bz#1079320]
- kvm-qcow2-Fix-copy_sectors-with-VM-state.patch [bz#1066691]
- kvm-qcow2-Fix-NULL-dereference-in-qcow2_open-error-path-.patch [bz#1079333]
- kvm-qcow2-Fix-L1-allocation-size-in-qcow2_snapshot_load_.patch [bz#1079325]
- kvm-qcow2-Check-maximum-L1-size-in-qcow2_snapshot_load_t.patch [bz#1079320]
- kvm-qcow2-Limit-snapshot-table-size.patch [bz#1066691]
- kvm-parallels-Fix-catalog-size-integer-overflow-CVE-2014.patch [bz#1079320]
- kvm-parallels-Sanity-check-for-s-tracks-CVE-2014-0142.patch [bz#1079315]
- kvm-fix-machine-check-propagation.patch [bz#740107]
- Resolves: bz#1066691
  (qemu-kvm: include leftover patches from block layer security audit)
- Resolves: bz#1079315
  (CVE-2014-0142 qemu-kvm: qemu: crash by possible division by zero [rhel-7.0])
- Resolves: bz#1079320
  (CVE-2014-0143 qemu-kvm: Qemu: block: multiple integer overflow flaws [rhel-7.0])
- Resolves: bz#1079325
  (CVE-2014-0145 qemu-kvm: Qemu: prevent possible buffer overflows [rhel-7.0])
- Resolves: bz#1079333
  (CVE-2014-0146 qemu-kvm: Qemu: qcow2: NULL dereference in qcow2_open() error path [rhel-7.0])
- Resolves: bz#1079339
  (CVE-2014-0147 qemu-kvm: Qemu: block: possible crash due signed types or logic error [rhel-7.0])
- Resolves: bz#1079346
  (CVE-2014-0148 qemu-kvm: Qemu: vhdx: bounds checking for block_size and logical_sector_size [rhel-7.0])
- Resolves: bz#1079455
  (CVE-2014-0144 qemu-kvm: Qemu: block: missing input validation [rhel-7.0])
- Resolves: bz#740107
  ([Hitachi 7.0 FEAT]  KVM: MCA Recovery for KVM guest OS memory)

* Wed Mar 26 2014 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-58.el7
- kvm-pc-Use-cpu64-rhel6-CPU-model-by-default-on-rhel6-mac.patch [bz#1080170]
- kvm-target-i386-Copy-cpu64-rhel6-definition-into-qemu64.patch [bz#1078607 bz#1080170]
- Resolves: bz#1080170
  (intel 82576 VF not work in windows 2008 x86 - Code 12 [TestOnly])
- Resolves: bz#1080170
  (Default CPU model for rhel6.* machine-types is different from RHEL-6)

* Fri Mar 21 2014 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-57.el7
- kvm-virtio-net-fix-guest-triggerable-buffer-overrun.patch [bz#1078308]
- Resolves: bz#1078308
  (EMBARGOED CVE-2014-0150 qemu: virtio-net: fix guest-triggerable buffer overrun [rhel-7.0])

* Fri Mar 21 2014 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-56.el7
- kvm-configure-Fix-bugs-preventing-Ceph-inclusion.patch [bz#1078809]
- Resolves: bz#1078809
  (can not boot qemu-kvm-rhev with rbd image)

* Wed Mar 19 2014 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-55.el7
- kvm-scsi-Change-scsi-sense-buf-size-to-252.patch [bz#1058173]
- kvm-scsi-Fix-migration-of-scsi-sense-data.patch [bz#1058173]
- Resolves: bz#1058173
  (qemu-kvm core dump booting guest with scsi-generic disk attached when using built-in iscsi driver)

* Wed Mar 19 2014 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-54.el7
- kvm-qdev-monitor-Set-properties-after-parent-is-assigned.patch [bz#1046248]
- kvm-block-Update-image-size-in-bdrv_invalidate_cache.patch [bz#1048575]
- kvm-qcow2-Keep-option-in-qcow2_invalidate_cache.patch [bz#1048575]
- kvm-qcow2-Check-bs-drv-in-copy_sectors.patch [bz#1048575]
- kvm-block-bs-drv-may-be-NULL-in-bdrv_debug_resume.patch [bz#1048575]
- kvm-iotests-Test-corruption-during-COW-request.patch [bz#1048575]
- Resolves: bz#1046248
  (qemu-kvm crash when send "info qtree" after hot plug a device with invalid addr)
- Resolves: bz#1048575
  (Segmentation fault occurs after migrate guest(use scsi disk and add stress) to des machine)

* Wed Mar 12 2014 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-53.el7
- kvm-dataplane-Fix-startup-race.patch [bz#1069541]
- kvm-QMP-Relax-__com.redhat_drive_add-parameter-checking.patch [bz#1057471]
- kvm-all-exit-in-case-max-vcpus-exceeded.patch [bz#993429]
- kvm-block-gluster-code-movements-state-storage-changes.patch [bz#1031526]
- kvm-block-gluster-add-reopen-support.patch [bz#1031526]
- kvm-virtio-net-add-feature-bit-for-any-header-s-g.patch [bz#990989]
- kvm-spec-Add-README.rhel6-gpxe-source.patch [bz#1073774]
- kvm-pc-Add-RHEL6-e1000-gPXE-image.patch [bz#1073774]
- kvm-loader-rename-in_ram-has_mr.patch [bz#1064018]
- kvm-pc-avoid-duplicate-names-for-ROM-MRs.patch [bz#1064018]
- kvm-qemu-img-convert-Fix-progress-output.patch [bz#1073728]
- kvm-qemu-iotests-Test-progress-output-for-conversion.patch [bz#1073728]
- kvm-iscsi-Use-bs-sg-for-everything-else-than-disks.patch [bz#1067784]
- kvm-block-Fix-bs-request_alignment-assertion-for-bs-sg-1.patch [bz#1067784]
- kvm-qemu_file-use-fwrite-correctly.patch [bz#1005103]
- kvm-qemu_file-Fix-mismerge-of-use-fwrite-correctly.patch [bz#1005103]
- Resolves: bz#1005103
  (Migration should fail when migrate guest offline to a file which is specified to a readonly directory.)
- Resolves: bz#1031526
  (Can not commit snapshot when disk is using glusterfs:native backend)
- Resolves: bz#1057471
  (fail to do hot-plug with "discard = on" with "Invalid parameter 'discard'" error)
- Resolves: bz#1064018
  (abort from conflicting genroms)
- Resolves: bz#1067784
  (qemu-kvm: block.c:850: bdrv_open_common: Assertion `bs->request_alignment != 0' failed. Aborted (core dumped))
- Resolves: bz#1069541
  (Segmentation fault when boot guest with dataplane=on)
- Resolves: bz#1073728
  (progress bar doesn't display when converting with -p)
- Resolves: bz#1073774
  (e1000 ROM cause migrate fail  from RHEL6.5 host to RHEL7.0 host)
- Resolves: bz#990989
  (backport inline header virtio-net optimization)
- Resolves: bz#993429
  (kvm: test maximum number of vcpus supported (rhel7))

* Wed Mar 05 2014 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-52.el7
- kvm-target-i386-Move-hyperv_-static-globals-to-X86CPU.patch [bz#1004773]
- kvm-Fix-uninitialized-cpuid_data.patch [bz#1057173]
- kvm-fix-coexistence-of-KVM-and-Hyper-V-leaves.patch [bz#1004773]
- kvm-make-availability-of-Hyper-V-enlightenments-depe.patch [bz#1004773]
- kvm-make-hyperv-hypercall-and-guest-os-id-MSRs-migra.patch [bz#1004773]
- kvm-make-hyperv-vapic-assist-page-migratable.patch [bz#1004773]
- kvm-target-i386-Convert-hv_relaxed-to-static-property.patch [bz#1057173]
- kvm-target-i386-Convert-hv_vapic-to-static-property.patch [bz#1057173]
- kvm-target-i386-Convert-hv_spinlocks-to-static-property.patch [bz#1057173]
- kvm-target-i386-Convert-check-and-enforce-to-static-prop.patch [bz#1004773]
- kvm-target-i386-Cleanup-foo-feature-handling.patch [bz#1057173]
- kvm-add-support-for-hyper-v-timers.patch [bz#1057173]
- Resolves: bz#1004773
  (Hyper-V guest OS id and hypercall MSRs not migrated)
- Resolves: bz#1057173
  (KVM Hyper-V Enlightenment - New feature - hv-time (QEMU))

* Wed Mar 05 2014 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-51.el7
- kvm-qmp-access-the-local-QemuOptsLists-for-drive-option.patch [bz#1026184]
- kvm-qxl-add-sanity-check.patch [bz#751937]
- kvm-Fix-two-XBZRLE-corruption-issues.patch [bz#1063417]
- kvm-qdev-monitor-set-DeviceState-opts-before-calling-rea.patch [bz#1037956]
- kvm-vfio-blacklist-loading-of-unstable-roms.patch [bz#1037956]
- kvm-block-Set-block-filename-sizes-to-PATH_MAX-instead-o.patch [bz#1072339]
- Resolves: bz#1026184
  (QMP: querying -drive option returns a NULL parameter list)
- Resolves: bz#1037956
  (bnx2x: boot one guest to do vfio-pci with all PFs assigned in same group meet QEMU segmentation fault (Broadcom BCM57810 card))
- Resolves: bz#1063417
  (google stressapptest vs Migration)
- Resolves: bz#1072339
  (RHEV: Cannot start VMs that have more than 23 snapshots.)
- Resolves: bz#751937
  (qxl triggers assert during iofuzz test)

* Wed Feb 26 2014 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-50.el7
- kvm-mempath-prefault-fix-off-by-one-error.patch [bz#1069039]
- kvm-qemu-option-has_help_option-and-is_valid_option_list.patch [bz#1065873]
- kvm-qemu-img-create-Support-multiple-o-options.patch [bz#1065873]
- kvm-qemu-img-convert-Support-multiple-o-options.patch [bz#1065873]
- kvm-qemu-img-amend-Support-multiple-o-options.patch [bz#1065873]
- kvm-qemu-img-Allow-o-help-with-incomplete-argument-list.patch [bz#1065873]
- kvm-qemu-iotests-Check-qemu-img-command-line-parsing.patch [bz#1065873]
- Resolves: bz#1065873
  (qemu-img silently ignores options with multiple -o parameters)
- Resolves: bz#1069039
  (-mem-prealloc option behaviour is opposite to expected)

* Wed Feb 19 2014 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-49.el7
- kvm-xhci-add-support-for-suspend-resume.patch [bz#1012365]
- kvm-qcow2-remove-n_start-and-n_end-of-qcow2_alloc_cluste.patch [bz#1049176]
- kvm-qcow2-fix-offset-overflow-in-qcow2_alloc_clusters_at.patch [bz#1049176]
- kvm-qcow2-check-for-NULL-l2meta.patch [bz#1055848]
- kvm-qemu-iotests-add-test-for-qcow2-preallocation-with-d.patch [bz#1055848]
- Resolves: bz#1012365
  (xhci usb storage lost in guest after wakeup from S3)
- Resolves: bz#1049176
  (qemu-img core dump when using "-o preallocation=metadata,cluster_size=2048k" to create image of libiscsi lun)
- Resolves: bz#1055848
  (qemu-img core dumped when cluster size is larger than the default value with opreallocation=metadata specified)

* Mon Feb 17 2014 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-48.el7
- kvm-spec-disable-qom-cast-debug.patch [bz#1063942]
- kvm-fix-guest-physical-bits-to-match-host-to-go-beyond-1.patch [bz#989677]
- kvm-monitor-Cleanup-mon-outbuf-on-write-error.patch [bz#1065225]
- Resolves: bz#1063942
  (configure qemu-kvm with --disable-qom-cast-debug)
- Resolves: bz#1065225
  (QMP socket breaks on unexpected close)
- Resolves: bz#989677
  ([HP 7.0 FEAT]: Increase KVM guest supported memory to 4TiB)

* Wed Feb 12 2014 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-47.el7
- kvm-seccomp-add-mkdir-and-fchmod-to-the-whitelist.patch [bz#1026314]
- kvm-seccomp-add-some-basic-shared-memory-syscalls-to-the.patch [bz#1026314]
- kvm-scsi-Support-TEST-UNIT-READY-in-the-dummy-LUN0.patch [bz#1004143]
- kvm-usb-add-vendor-request-defines.patch [bz#1039530]
- kvm-usb-move-usb_-hi-lo-helpers-to-header-file.patch [bz#1039530]
- kvm-usb-add-support-for-microsoft-os-descriptors.patch [bz#1039530]
- kvm-usb-add-microsoft-os-descriptors-compat-property.patch [bz#1039530]
- kvm-usb-hid-add-microsoft-os-descriptor-support.patch [bz#1039530]
- kvm-configure-add-option-to-disable-fstack-protect.patch [bz#1044182]
- kvm-exec-always-use-MADV_DONTFORK.patch [bz#1004197]
- kvm-pc-Save-size-of-RAM-below-4GB.patch [bz#1048080]
- kvm-acpi-Fix-PCI-hole-handling-on-build_srat.patch [bz#1048080]
- kvm-Add-check-for-cache-size-smaller-than-page-size.patch [bz#1017096]
- kvm-XBZRLE-cache-size-should-not-be-larger-than-guest-me.patch [bz#1047448]
- kvm-Don-t-abort-on-out-of-memory-when-creating-page-cach.patch [bz#1047448]
- kvm-Don-t-abort-on-memory-allocation-error.patch [bz#1047448]
- kvm-Set-xbzrle-buffers-to-NULL-after-freeing-them-to-avo.patch [bz#1038540]
- kvm-migration-fix-free-XBZRLE-decoded_buf-wrong.patch [bz#1038540]
- kvm-block-resize-backing-file-image-during-offline-commi.patch [bz#1047254]
- kvm-block-resize-backing-image-during-active-layer-commi.patch [bz#1047254]
- kvm-block-update-block-commit-documentation-regarding-im.patch [bz#1047254]
- kvm-block-Fix-bdrv_commit-return-value.patch [bz#1047254]
- kvm-block-remove-QED-.bdrv_make_empty-implementation.patch [bz#1047254]
- kvm-block-remove-qcow2-.bdrv_make_empty-implementation.patch [bz#1047254]
- kvm-qemu-progress-Drop-unused-include.patch [bz#997878]
- kvm-qemu-progress-Fix-progress-printing-on-SIGUSR1.patch [bz#997878]
- kvm-Documentation-qemu-img-Mention-SIGUSR1-progress-repo.patch [bz#997878]
- Resolves: bz#1004143
  ("test unit ready failed" on LUN 0 delays boot when a virtio-scsi target does not have any disk on LUN 0)
- Resolves: bz#1004197
  (Cannot hot-plug nic in windows VM when the vmem is larger)
- Resolves: bz#1017096
  (Fail to migrate while the size of migrate-compcache less then 4096)
- Resolves: bz#1026314
  (qemu-kvm hang when use '-sandbox on'+'vnc'+'hda')
- Resolves: bz#1038540
  (qemu-kvm aborted while cancel migration then restart it (with page delta compression))
- Resolves: bz#1039530
  (add support for microsoft os descriptors)
- Resolves: bz#1044182
  (Relax qemu-kvm stack protection to -fstack-protector-strong)
- Resolves: bz#1047254
  (qemu-img failed to commit image)
- Resolves: bz#1047448
  (qemu-kvm core  dump in src host when do migration with "migrate_set_capability xbzrle on and migrate_set_cache_size 10000G")
- Resolves: bz#1048080
  (Qemu-kvm NUMA emulation failed)
- Resolves: bz#997878
  (Kill -SIGUSR1 `pidof qemu-img convert` can not get progress of qemu-img)

* Wed Feb 12 2014 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-46.el7
- kvm-block-fix-backing-file-segfault.patch [bz#748906]
- kvm-block-Move-initialisation-of-BlockLimits-to-bdrv_ref.patch [bz#748906]
- kvm-raw-Fix-BlockLimits-passthrough.patch [bz#748906]
- kvm-block-Inherit-opt_transfer_length.patch [bz#748906]
- kvm-block-Update-BlockLimits-when-they-might-have-change.patch [bz#748906]
- kvm-qemu_memalign-Allow-small-alignments.patch [bz#748906]
- kvm-block-Detect-unaligned-length-in-bdrv_qiov_is_aligne.patch [bz#748906]
- kvm-block-Don-t-use-guest-sector-size-for-qemu_blockalig.patch [bz#748906]
- kvm-block-rename-buffer_alignment-to-guest_block_size.patch [bz#748906]
- kvm-raw-Probe-required-direct-I-O-alignment.patch [bz#748906]
- kvm-block-Introduce-bdrv_aligned_preadv.patch [bz#748906]
- kvm-block-Introduce-bdrv_co_do_preadv.patch [bz#748906]
- kvm-block-Introduce-bdrv_aligned_pwritev.patch [bz#748906]
- kvm-block-write-Handle-COR-dependency-after-I-O-throttli.patch [bz#748906]
- kvm-block-Introduce-bdrv_co_do_pwritev.patch [bz#748906]
- kvm-block-Switch-BdrvTrackedRequest-to-byte-granularity.patch [bz#748906]
- kvm-block-Allow-waiting-for-overlapping-requests-between.patch [bz#748906]
- kvm-block-use-DIV_ROUND_UP-in-bdrv_co_do_readv.patch [bz#748906]
- kvm-block-Make-zero-after-EOF-work-with-larger-alignment.patch [bz#748906]
- kvm-block-Generalise-and-optimise-COR-serialisation.patch [bz#748906]
- kvm-block-Make-overlap-range-for-serialisation-dynamic.patch [bz#748906]
- kvm-block-Fix-32-bit-truncation-in-mark_request_serialis.patch [bz#748906]
- kvm-block-Allow-wait_serialising_requests-at-any-point.patch [bz#748906]
- kvm-block-Align-requests-in-bdrv_co_do_pwritev.patch [bz#748906]
- kvm-lock-Fix-memory-leaks-in-bdrv_co_do_pwritev.patch [bz#748906]
- kvm-block-Assert-serialisation-assumptions-in-pwritev.patch [bz#748906]
- kvm-block-Change-coroutine-wrapper-to-byte-granularity.patch [bz#748906]
- kvm-block-Make-bdrv_pread-a-bdrv_prwv_co-wrapper.patch [bz#748906]
- kvm-block-Make-bdrv_pwrite-a-bdrv_prwv_co-wrapper.patch [bz#748906]
- kvm-iscsi-Set-bs-request_alignment.patch [bz#748906]
- kvm-blkdebug-Make-required-alignment-configurable.patch [bz#748906]
- kvm-blkdebug-Don-t-leak-bs-file-on-failure.patch [bz#748906]
- kvm-qemu-io-New-command-sleep.patch [bz#748906]
- kvm-qemu-iotests-Filter-out-qemu-io-prompt.patch [bz#748906]
- kvm-qemu-iotests-Test-pwritev-RMW-logic.patch [bz#748906]
- kvm-block-bdrv_aligned_pwritev-Assert-overlap-range.patch [bz#748906]
- kvm-block-Don-t-call-ROUND_UP-with-negative-values.patch [bz#748906]
- Resolves: bz#748906
  (qemu fails on disk with 4k sectors and cache=off)

* Wed Feb 05 2014 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-45.el7
- kvm-vfio-pci-Fail-initfn-on-DMA-mapping-errors.patch [bz#1044815]
- kvm-vfio-Destroy-memory-regions.patch [bz#1052030]
- kvm-docs-qcow2-compat-1.1-is-now-the-default.patch [bz#1048092]
- kvm-hda-codec-disable-streams-on-reset.patch [bz#947812]
- kvm-QEMUBH-make-AioContext-s-bh-re-entrant.patch [bz#1009297]
- kvm-qxl-replace-pipe-signaling-with-bottom-half.patch [bz#1009297]
- Resolves: bz#1009297
  (RHEL7.0 guest gui can not be used in dest host after migration)
- Resolves: bz#1044815
  (vfio initfn succeeds even if IOMMU mappings fail)
- Resolves: bz#1048092
  (manpage of qemu-img contains error statement about compat option)
- Resolves: bz#1052030
  (src qemu-kvm core dump after hotplug/unhotplug GPU device and do local migration)
- Resolves: bz#947812
  (There's a shot voice after  'system_reset'  during playing music inside rhel6 guest w/ intel-hda device)

* Wed Jan 29 2014 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-44.el7
- kvm-Partially-revert-rhel-Drop-cfi.pflash01-and-isa-ide-.patch [bz#1032346]
- kvm-Revert-pc-Disable-the-use-flash-device-for-BIOS-unle.patch [bz#1032346]
- kvm-memory-Replace-open-coded-memory_region_is_romd.patch [bz#1032346]
- kvm-memory-Rename-readable-flag-to-romd_mode.patch [bz#1032346]
- kvm-isapc-Fix-non-KVM-qemu-boot-read-write-memory-for-is.patch [bz#1032346]
- kvm-add-kvm_readonly_mem_enabled.patch [bz#1032346]
- kvm-support-using-KVM_MEM_READONLY-flag-for-regions.patch [bz#1032346]
- kvm-pc_sysfw-allow-flash-pflash-memory-to-be-used-with-K.patch [bz#1032346]
- kvm-fix-double-free-the-memslot-in-kvm_set_phys_mem.patch [bz#1032346]
- kvm-sysfw-remove-read-only-pc_sysfw_flash_vs_rom_bug_com.patch [bz#1032346]
- kvm-pc_sysfw-remove-the-rom_only-property.patch [bz#1032346]
- kvm-pc_sysfw-do-not-make-it-a-device-anymore.patch [bz#1032346]
- kvm-hw-i386-pc_sysfw-support-two-flash-drives.patch [bz#1032346]
- kvm-i440fx-test-qtest_start-should-be-paired-with-qtest_.patch [bz#1032346]
- kvm-i440fx-test-give-each-GTest-case-its-own-qtest.patch [bz#1032346]
- kvm-i440fx-test-generate-temporary-firmware-blob.patch [bz#1032346]
- kvm-i440fx-test-verify-firmware-under-4G-and-1M-both-bio.patch [bz#1032346]
- kvm-piix-fix-32bit-pci-hole.patch [bz#1032346]
- kvm-qapi-Add-backing-to-BlockStats.patch [bz#1041564]
- kvm-pc-Disable-RDTSCP-unconditionally-on-rhel6.-machine-.patch [bz#918907]
- kvm-pc-Disable-RDTSCP-on-AMD-CPU-models.patch [bz#1056428 bz#874400]
- kvm-block-add-.bdrv_reopen_prepare-stub-for-iscsi.patch [bz#1030301]
- Resolves: bz#1030301
  (qemu-img can not merge live snapshot to backing file(r/w backing file via libiscsi))
- Resolves: bz#1032346
  (basic OVMF support (non-volatile UEFI variables in flash, and fixup for ACPI tables))
- Resolves: bz#1041564
  ([NFR] qemu: Returning the watermark for all the images opened for writing)
- Resolves: bz#1056428
  ("rdtscp" flag defined on Opteron_G5 model and cann't be exposed to guest)
- Resolves: bz#874400
  ("rdtscp" flag defined on Opteron_G5 model and cann't be exposed to guest)
- Resolves: bz#918907
  (provide backwards-compatible RHEL specific machine types in QEMU - CPU features)

* Mon Jan 27 2014 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-43.el7
- kvm-piix-gigabyte-alignment-for-ram.patch [bz#1026548]
- kvm-pc_piix-document-gigabyte_align.patch [bz#1026548]
- kvm-q35-gigabyle-alignment-for-ram.patch [bz#1026548]
- kvm-virtio-bus-remove-vdev-field.patch [bz#983344]
- kvm-virtio-pci-remove-vdev-field.patch [bz#983344]
- kvm-virtio-bus-cleanup-plug-unplug-interface.patch [bz#983344]
- kvm-virtio-blk-switch-exit-callback-to-VirtioDeviceClass.patch [bz#983344]
- kvm-virtio-serial-switch-exit-callback-to-VirtioDeviceCl.patch [bz#983344]
- kvm-virtio-net-switch-exit-callback-to-VirtioDeviceClass.patch [bz#983344]
- kvm-virtio-scsi-switch-exit-callback-to-VirtioDeviceClas.patch [bz#983344]
- kvm-virtio-balloon-switch-exit-callback-to-VirtioDeviceC.patch [bz#983344]
- kvm-virtio-rng-switch-exit-callback-to-VirtioDeviceClass.patch [bz#983344]
- kvm-virtio-pci-add-device_unplugged-callback.patch [bz#983344]
- kvm-block-use-correct-filename-for-error-report.patch [bz#1051438]
- Resolves: bz#1026548
  (i386: pc: align gpa<->hpa on 1GB boundary)
- Resolves: bz#1051438
  (Error message contains garbled characters when unable to open image due to bad permissions (permission denied).)
- Resolves: bz#983344
  (QEMU core dump and host will reboot when do hot-unplug a virtio-blk disk which use  the switch behind switch)

* Fri Jan 24 2014 Daniel Mach <dmach@redhat.com> - 10:1.5.3-42
- Mass rebuild 2014-01-24

* Wed Jan 22 2014 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-41.el7
- kvm-help-add-id-suboption-to-iscsi.patch [bz#1019221]
- kvm-scsi-disk-add-UNMAP-limits-to-block-limits-VPD-page.patch [bz#1037503]
- kvm-qdev-Fix-32-bit-compilation-in-print_size.patch [bz#1034876]
- kvm-qdev-Use-clz-in-print_size.patch [bz#1034876]
- Resolves: bz#1019221
  (Iscsi miss id sub-option in help output)
- Resolves: bz#1034876
  (export acpi tables to guests)
- Resolves: bz#1037503
  (fix thin provisioning support for block device backends)

* Wed Jan 22 2014 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-40.el7
- kvm-avoid-a-bogus-COMPLETED-CANCELLED-transition.patch [bz#1053699]
- kvm-introduce-MIG_STATE_CANCELLING-state.patch [bz#1053699]
- kvm-vvfat-use-bdrv_new-to-allocate-BlockDriverState.patch [bz#1041301]
- kvm-block-implement-reference-count-for-BlockDriverState.patch [bz#1041301]
- kvm-block-make-bdrv_delete-static.patch [bz#1041301]
- kvm-migration-omit-drive-ref-as-we-have-bdrv_ref-now.patch [bz#1041301]
- kvm-xen_disk-simplify-blk_disconnect-with-refcnt.patch [bz#1041301]
- kvm-nbd-use-BlockDriverState-refcnt.patch [bz#1041301]
- kvm-block-use-BDS-ref-for-block-jobs.patch [bz#1041301]
- kvm-block-Make-BlockJobTypes-const.patch [bz#1041301]
- kvm-blockjob-rename-BlockJobType-to-BlockJobDriver.patch [bz#1041301]
- kvm-qapi-Introduce-enum-BlockJobType.patch [bz#1041301]
- kvm-qapi-make-use-of-new-BlockJobType.patch [bz#1041301]
- kvm-mirror-Don-t-close-target.patch [bz#1041301]
- kvm-mirror-Move-base-to-MirrorBlockJob.patch [bz#1041301]
- kvm-block-Add-commit_active_start.patch [bz#1041301]
- kvm-commit-Support-commit-active-layer.patch [bz#1041301]
- kvm-qemu-iotests-prefill-some-data-to-test-image.patch [bz#1041301]
- kvm-qemu-iotests-Update-test-cases-for-commit-active.patch [bz#1041301]
- kvm-commit-Remove-unused-check.patch [bz#1041301]
- kvm-blockdev-use-bdrv_getlength-in-qmp_drive_mirror.patch [bz#921890]
- kvm-qemu-iotests-make-assert_no_active_block_jobs-common.patch [bz#921890]
- kvm-block-drive-mirror-Check-for-NULL-backing_hd.patch [bz#921890]
- kvm-qemu-iotests-Extend-041-for-unbacked-mirroring.patch [bz#921890]
- kvm-qapi-schema-Update-description-for-NewImageMode.patch [bz#921890]
- kvm-block-drive-mirror-Reuse-backing-HD-for-sync-none.patch [bz#921890]
- kvm-qemu-iotests-Fix-test-041.patch [bz#921890]
- kvm-scsi-bus-fix-transfer-length-and-direction-for-VERIF.patch [bz#1035644]
- kvm-scsi-disk-fix-VERIFY-emulation.patch [bz#1035644]
- kvm-block-ensure-bdrv_drain_all-works-during-bdrv_delete.patch [bz#1041301]
- kvm-use-recommended-max-vcpu-count.patch [bz#998708]
- kvm-pc-Create-pc_compat_rhel-functions.patch [bz#1049706]
- kvm-pc-Enable-x2apic-by-default-on-more-recent-CPU-model.patch [bz#1049706]
- kvm-Build-all-subpackages-for-RHEV.patch [bz#1007204]
- Resolves: bz#1007204
  (qemu-img-rhev  qemu-kvm-rhev-tools are not built for qemu-kvm-1.5.3-3.el7)
- Resolves: bz#1035644
  (rhel7.0host + windows guest + virtio-win + 'chkdsk' in the guest gives qemu assertion in scsi_dma_complete)
- Resolves: bz#1041301
  (live snapshot merge (commit) of the active layer)
- Resolves: bz#1049706
  (MIss CPUID_EXT_X2APIC in Westmere cpu model)
- Resolves: bz#1053699
  (Backport Cancelled race condition fixes)
- Resolves: bz#921890
  (Core dump when block mirror with "sync" is "none" and mode is "absolute-paths")
- Resolves: bz#998708
  (qemu-kvm: maximum vcpu should be recommended maximum)

* Tue Jan 21 2014 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-39.el7
- kvm-Revert-qdev-monitor-Fix-crash-when-device_add-is-cal.patch [bz#669524]
- kvm-Revert-qdev-Do-not-let-the-user-try-to-device_add-wh.patch [bz#669524]
- kvm-qdev-monitor-Clean-up-qdev_device_add-variable-namin.patch [bz#669524]
- kvm-qdev-monitor-Fix-crash-when-device_add-is-called.2.patch.patch [bz#669524]
- kvm-qdev-monitor-Avoid-qdev-as-variable-name.patch [bz#669524]
- kvm-qdev-monitor-Inline-qdev_init-for-device_add.patch [bz#669524]
- kvm-qdev-Do-not-let-the-user-try-to-device_add-when-it.2.patch.patch [bz#669524]
- kvm-qdev-monitor-Avoid-device_add-crashing-on-non-device.patch [bz#669524]
- kvm-qdev-monitor-Improve-error-message-for-device-nonexi.patch [bz#669524]
- kvm-exec-change-well-known-physical-sections-to-macros.patch [bz#1003535]
- kvm-exec-separate-sections-and-nodes-per-address-space.patch [bz#1003535]
- Resolves: bz#1003535
  (qemu-kvm core dump when boot vm with more than 32 virtio disks/nics)
- Resolves: bz#669524
  (Confusing error message from -device <unknown dev>)

* Fri Jan 17 2014 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-38.el7
- kvm-intel-hda-fix-position-buffer.patch [bz#947785]
- kvm-The-calculation-of-bytes_xfer-in-qemu_put_buffer-is-.patch [bz#1003467]
- kvm-migration-Fix-rate-limit.patch [bz#1003467]
- kvm-audio-honor-QEMU_AUDIO_TIMER_PERIOD-instead-of-wakin.patch [bz#1017636]
- kvm-audio-Lower-default-wakeup-rate-to-100-times-second.patch [bz#1017636]
- kvm-audio-adjust-pulse-to-100Hz-wakeup-rate.patch [bz#1017636]
- kvm-pc-Fix-rhel6.-3dnow-3dnowext-compat-bits.patch [bz#918907]
- kvm-add-firmware-to-machine-options.patch [bz#1038603]
- kvm-switch-rhel7-machine-types-to-big-bios.patch [bz#1038603]
- kvm-add-bios-256k.bin-from-seabios-bin-1.7.2.2-10.el7.no.patch [bz#1038603]
- kvm-pci-fix-pci-bridge-fw-path.patch [bz#1034518]
- kvm-hw-cannot_instantiate_with_device_add_yet-due-to-poi.patch [bz#1031098]
- kvm-qdev-Document-that-pointer-properties-kill-device_ad.patch [bz#1031098]
- kvm-Add-back-no-hpet-but-ignore-it.patch [bz#1044742]
- Resolves: bz#1003467
  (Backport migration fixes from post qemu 1.6)
- Resolves: bz#1017636
  (PATCH: fix qemu using 50% host cpu when audio is playing)
- Resolves: bz#1031098
  (Disable device smbus-eeprom)
- Resolves: bz#1034518
  (boot order wrong with q35)
- Resolves: bz#1038603
  (make seabios 256k for rhel7 machine types)
- Resolves: bz#1044742
  (Cannot create guest on remote RHEL7 host using F20 virt-manager, libvirt's qemu -no-hpet detection is broken)
- Resolves: bz#918907
  (provide backwards-compatible RHEL specific machine types in QEMU - CPU features)
- Resolves: bz#947785
  (In rhel6.4 guest  sound recorder doesn't work when  playing audio)

* Wed Jan 15 2014 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-37.el7
- kvm-bitmap-use-long-as-index.patch [bz#997559]
- kvm-memory-cpu_physical_memory_set_dirty_flags-result-is.patch [bz#997559]
- kvm-memory-cpu_physical_memory_set_dirty_range-return-vo.patch [bz#997559]
- kvm-exec-use-accessor-function-to-know-if-memory-is-dirt.patch [bz#997559]
- kvm-memory-create-function-to-set-a-single-dirty-bit.patch [bz#997559]
- kvm-exec-drop-useless-if.patch [bz#997559]
- kvm-exec-create-function-to-get-a-single-dirty-bit.patch [bz#997559]
- kvm-memory-make-cpu_physical_memory_is_dirty-return-bool.patch [bz#997559]
- kvm-memory-all-users-of-cpu_physical_memory_get_dirty-us.patch [bz#997559]
- kvm-memory-set-single-dirty-flags-when-possible.patch [bz#997559]
- kvm-memory-cpu_physical_memory_set_dirty_range-always-di.patch [bz#997559]
- kvm-memory-cpu_physical_memory_mask_dirty_range-always-c.patch [bz#997559]
- kvm-memory-use-bit-2-for-migration.patch [bz#997559]
- kvm-memory-make-sure-that-client-is-always-inside-range.patch [bz#997559]
- kvm-memory-only-resize-dirty-bitmap-when-memory-size-inc.patch [bz#997559]
- kvm-memory-cpu_physical_memory_clear_dirty_flag-result-i.patch [bz#997559]
- kvm-bitmap-Add-bitmap_zero_extend-operation.patch [bz#997559]
- kvm-memory-split-dirty-bitmap-into-three.patch [bz#997559]
- kvm-memory-unfold-cpu_physical_memory_clear_dirty_flag-i.patch [bz#997559]
- kvm-memory-unfold-cpu_physical_memory_set_dirty-in-its-o.patch [bz#997559]
- kvm-memory-unfold-cpu_physical_memory_set_dirty_flag.patch [bz#997559]
- kvm-memory-make-cpu_physical_memory_get_dirty-the-main-f.patch [bz#997559]
- kvm-memory-cpu_physical_memory_get_dirty-is-used-as-retu.patch [bz#997559]
- kvm-memory-s-mask-clear-cpu_physical_memory_mask_dirty_r.patch [bz#997559]
- kvm-memory-use-find_next_bit-to-find-dirty-bits.patch [bz#997559]
- kvm-memory-cpu_physical_memory_set_dirty_range-now-uses-.patch [bz#997559]
- kvm-memory-cpu_physical_memory_clear_dirty_range-now-use.patch [bz#997559]
- kvm-memory-s-dirty-clean-in-cpu_physical_memory_is_dirty.patch [bz#997559]
- kvm-memory-make-cpu_physical_memory_reset_dirty-take-a-l.patch [bz#997559]
- kvm-exec-Remove-unused-global-variable-phys_ram_fd.patch [bz#997559]
- kvm-memory-cpu_physical_memory_set_dirty_tracking-should.patch [bz#997559]
- kvm-memory-move-private-types-to-exec.c.patch [bz#997559]
- kvm-memory-split-cpu_physical_memory_-functions-to-its-o.patch [bz#997559]
- kvm-memory-unfold-memory_region_test_and_clear.patch [bz#997559]
- kvm-use-directly-cpu_physical_memory_-api-for-tracki.patch [bz#997559]
- kvm-refactor-start-address-calculation.patch [bz#997559]
- kvm-memory-move-bitmap-synchronization-to-its-own-functi.patch [bz#997559]
- kvm-memory-syncronize-kvm-bitmap-using-bitmaps-operation.patch [bz#997559]
- kvm-ram-split-function-that-synchronizes-a-range.patch [bz#997559]
- kvm-migration-synchronize-memory-bitmap-64bits-at-a-time.patch [bz#997559]
- Resolves: bz#997559
  (Improve live migration bitmap handling)

* Tue Jan 14 2014 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-36.el7
- kvm-Add-support-statement-to-help-output.patch [bz#972773]
- kvm-__com.redhat_qxl_screendump-add-docs.patch [bz#903910]
- kvm-vl-Round-memory-sizes-below-2MiB-up-to-2MiB.patch [bz#999836]
- kvm-seccomp-exit-if-seccomp_init-fails.patch [bz#1044845]
- kvm-redhat-qemu-kvm.spec-require-python-for-build.patch [bz#1034876]
- kvm-redhat-qemu-kvm.spec-require-iasl.patch [bz#1034876]
- kvm-configure-make-iasl-option-actually-work.patch [bz#1034876]
- kvm-redhat-qemu-kvm.spec-add-cpp-as-build-dependency.patch [bz#1034876]
- kvm-acpi-build-disable-with-no-acpi.patch [bz#1045386]
- kvm-ehci-implement-port-wakeup.patch [bz#1039513]
- kvm-qdev-monitor-Fix-crash-when-device_add-is-called-wit.patch [bz#1026712 bz#1046007]
- kvm-block-vhdx-improve-error-message-and-.bdrv_check-imp.patch [bz#1035001]
- kvm-docs-updated-qemu-img-man-page-and-qemu-doc-to-refle.patch [bz#1017650]
- kvm-enable-pvticketlocks-by-default.patch [bz#1052340]
- kvm-fix-boot-strict-regressed-in-commit-6ef4716.patch [bz#997817]
- kvm-vl-make-boot_strict-variable-static-not-used-outside.patch [bz#997817]
- Resolves: bz#1017650
  (need to update qemu-img man pages on "VHDX" format)
- Resolves: bz#1026712
  (Qemu core dumpd when boot guest with driver name as "virtio-pci")
- Resolves: bz#1034876
  (export acpi tables to guests)
- Resolves: bz#1035001
  (VHDX: journal log should not be replayed by default, but rather via qemu-img check -r all)
- Resolves: bz#1039513
  (backport remote wakeup for ehci)
- Resolves: bz#1044845
  (QEMU seccomp sandbox - exit if seccomp_init() fails)
- Resolves: bz#1045386
  (qemu-kvm: hw/i386/acpi-build.c:135: acpi_get_pm_info: Assertion `obj' failed.)
- Resolves: bz#1046007
  (qemu-kvm aborted when hot plug PCI device to guest with romfile and rombar=0)
- Resolves: bz#1052340
  (pvticketlocks: default on)
- Resolves: bz#903910
  (RHEL7 does not have equivalent functionality for __com.redhat_qxl_screendump)
- Resolves: bz#972773
  (RHEL7: Clarify support statement in KVM help)
- Resolves: bz#997817
  (-boot order and -boot once regressed since RHEL-6)
- Resolves: bz#999836
  (-m 1 crashes)

* Thu Jan 09 2014 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-35.el7
- kvm-option-Add-assigned-flag-to-QEMUOptionParameter.patch [bz#1033490]
- kvm-qcow2-refcount-Snapshot-update-for-zero-clusters.patch [bz#1033490]
- kvm-qemu-iotests-Snapshotting-zero-clusters.patch [bz#1033490]
- kvm-block-Image-file-option-amendment.patch [bz#1033490]
- kvm-qcow2-cache-Empty-cache.patch [bz#1033490]
- kvm-qcow2-cluster-Expand-zero-clusters.patch [bz#1033490]
- kvm-qcow2-Save-refcount-order-in-BDRVQcowState.patch [bz#1033490]
- kvm-qcow2-Implement-bdrv_amend_options.patch [bz#1033490]
- kvm-qcow2-Correct-bitmap-size-in-zero-expansion.patch [bz#1033490]
- kvm-qcow2-Free-only-newly-allocated-clusters-on-error.patch [bz#1033490]
- kvm-qcow2-Add-missing-space-in-error-message.patch [bz#1033490]
- kvm-qemu-iotest-qcow2-image-option-amendment.patch [bz#1033490]
- kvm-qemu-iotests-New-test-case-in-061.patch [bz#1033490]
- kvm-qemu-iotests-Preallocated-zero-clusters-in-061.patch [bz#1033490]
- Resolves: bz#1033490
  (Cannot upgrade/downgrade qcow2 images)

* Wed Jan 08 2014 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-34.el7
- kvm-block-stream-Don-t-stream-unbacked-devices.patch [bz#965636]
- kvm-qemu-io-Let-open-pass-options-to-block-driver.patch [bz#1004347]
- kvm-qcow2.py-Subcommand-for-changing-header-fields.patch [bz#1004347]
- kvm-qemu-iotests-Remaining-error-propagation-adjustments.patch [bz#1004347]
- kvm-qemu-iotests-Add-test-for-inactive-L2-overlap.patch [bz#1004347]
- kvm-qemu-iotests-Adjust-test-result-039.patch [bz#1004347]
- kvm-virtio-net-don-t-update-mac_table-in-error-state.patch [bz#1048671]
- kvm-qcow2-Zero-initialise-first-cluster-for-new-images.patch [bz#1032904]
- Resolves: bz#1004347
  (Backport qcow2 corruption prevention patches)
- Resolves: bz#1032904
  (qemu-img can not create libiscsi qcow2_v3 image)
- Resolves: bz#1048671
  (virtio-net: mac_table change isn't recovered in error state)
- Resolves: bz#965636
  (streaming with no backing file should not do anything)

* Wed Jan 08 2014 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-33.el7
- kvm-block-qemu-iotests-for-vhdx-read-sample-dynamic-imag.patch [bz#879234]
- kvm-block-qemu-iotests-add-quotes-to-TEST_IMG-usage-io-p.patch [bz#879234]
- kvm-block-qemu-iotests-fix-_make_test_img-to-work-with-s.patch [bz#879234]
- kvm-block-qemu-iotests-add-quotes-to-TEST_IMG.base-usage.patch [bz#879234]
- kvm-block-qemu-iotests-add-quotes-to-TEST_IMG-usage-in-0.patch [bz#879234]
- kvm-block-qemu-iotests-removes-duplicate-double-quotes-i.patch [bz#879234]
- kvm-block-vhdx-minor-comments-and-typo-correction.patch [bz#879234]
- kvm-block-vhdx-add-header-update-capability.patch [bz#879234]
- kvm-block-vhdx-code-movement-VHDXMetadataEntries-and-BDR.patch [bz#879234]
- kvm-block-vhdx-log-support-struct-and-defines.patch [bz#879234]
- kvm-block-vhdx-break-endian-translation-functions-out.patch [bz#879234]
- kvm-block-vhdx-update-log-guid-in-header-and-first-write.patch [bz#879234]
- kvm-block-vhdx-code-movement-move-vhdx_close-above-vhdx_.patch [bz#879234]
- kvm-block-vhdx-log-parsing-replay-and-flush-support.patch [bz#879234]
- kvm-block-vhdx-add-region-overlap-detection-for-image-fi.patch [bz#879234]
- kvm-block-vhdx-add-log-write-support.patch [bz#879234]
- kvm-block-vhdx-write-support.patch [bz#879234]
- kvm-block-vhdx-remove-BAT-file-offset-bit-shifting.patch [bz#879234]
- kvm-block-vhdx-move-more-endian-translations-to-vhdx-end.patch [bz#879234]
- kvm-block-vhdx-break-out-code-operations-to-functions.patch [bz#879234]
- kvm-block-vhdx-fix-comment-typos-in-header-fix-incorrect.patch [bz#879234]
- kvm-block-vhdx-add-.bdrv_create-support.patch [bz#879234]
- kvm-block-vhdx-update-_make_test_img-to-filter-out-vhdx-.patch [bz#879234]
- kvm-block-qemu-iotests-for-vhdx-add-write-test-support.patch [bz#879234]
- kvm-block-vhdx-qemu-iotest-log-replay-of-data-sector.patch [bz#879234]
- Resolves: bz#879234
  ([RFE] qemu-img: Add/improve support for VHDX format)

* Mon Jan 06 2014 Michal Novotny <minovotn@redhat.com> - 1.5.3-32.el7
- kvm-block-change-default-of-.has_zero_init-to-0.patch.patch [bz#1007815]
- kvm-iscsi-factor-out-sector-conversions.patch.patch [bz#1007815]
- kvm-iscsi-add-logical-block-provisioning-information-to-.patch.patch [bz#1007815]
- kvm-iscsi-add-.bdrv_get_block_status.patch.patch.patch [bz#1007815]
- kvm-iscsi-split-discard-requests-in-multiple-parts.patch.patch.patch [bz#1007815]
- kvm-block-make-BdrvRequestFlags-public.patch.patch.patch [bz#1007815]
- kvm-block-add-flags-to-bdrv_-_write_zeroes.patch.patch.patch [bz#1007815]
- kvm-block-introduce-BDRV_REQ_MAY_UNMAP-request-flag.patch.patch.patch [bz#1007815]
- kvm-block-add-logical-block-provisioning-info-to-BlockDr.patch.patch.patch [bz#1007815]
- kvm-block-add-wrappers-for-logical-block-provisioning-in.patch.patch.patch [bz#1007815]
- kvm-block-iscsi-add-.bdrv_get_info.patch.patch [bz#1007815]
- kvm-block-add-BlockLimits-structure-to-BlockDriverState.patch.patch.patch [bz#1007815]
- kvm-block-raw-copy-BlockLimits-on-raw_open.patch.patch.patch [bz#1007815]
- kvm-block-honour-BlockLimits-in-bdrv_co_do_write_zeroes.patch.patch.patch [bz#1007815]
- kvm-block-honour-BlockLimits-in-bdrv_co_discard.patch.patch.patch [bz#1007815]
- kvm-iscsi-set-limits-in-BlockDriverState.patch.patch.patch [bz#1007815]
- kvm-iscsi-simplify-iscsi_co_discard.patch.patch.patch [bz#1007815]
- kvm-iscsi-add-bdrv_co_write_zeroes.patch.patch.patch [bz#1007815]
- kvm-block-introduce-bdrv_make_zero.patch.patch.patch [bz#1007815]
- kvm-block-get_block_status-fix-BDRV_BLOCK_ZERO-for-unall.patch.patch.patch [bz#1007815]
- kvm-qemu-img-add-support-for-fully-allocated-images.patch.patch.patch [bz#1007815]
- kvm-qemu-img-conditionally-zero-out-target-on-convert.patch.patch.patch [bz#1007815]
- kvm-block-generalize-BlockLimits-handling-to-cover-bdrv_.patch.patch.patch [bz#1007815]
- kvm-block-add-flags-to-BlockRequest.patch.patch.patch [bz#1007815]
- kvm-block-add-flags-argument-to-bdrv_co_write_zeroes-tra.patch.patch.patch [bz#1007815]
- kvm-block-add-bdrv_aio_write_zeroes.patch.patch.patch [bz#1007815]
- kvm-block-handle-ENOTSUP-from-discard-in-generic-code.patch.patch.patch [bz#1007815]
- kvm-block-make-bdrv_co_do_write_zeroes-stricter-in-produ.patch.patch.patch [bz#1007815]
- kvm-vpc-vhdx-add-get_info.patch.patch.patch [bz#1007815]
- kvm-block-drivers-add-discard-write_zeroes-properties-to.patch.patch.patch [bz#1007815]
- kvm-block-drivers-expose-requirement-for-write-same-alig.patch.patch.patch [bz#1007815]
- kvm-block-iscsi-remove-.bdrv_has_zero_init.patch.patch.patch [bz#1007815]
- kvm-block-iscsi-updated-copyright.patch.patch.patch [bz#1007815]
- kvm-block-iscsi-check-WRITE-SAME-support-differently-dep.patch.patch.patch [bz#1007815]
- kvm-scsi-disk-catch-write-protection-errors-in-UNMAP.patch.patch.patch [bz#1007815]
- kvm-scsi-disk-reject-ANCHOR-1-for-UNMAP-and-WRITE-SAME-c.patch.patch.patch [bz#1007815]
- kvm-scsi-disk-correctly-implement-WRITE-SAME.patch.patch.patch [bz#1007815]
- kvm-scsi-disk-fix-WRITE-SAME-with-large-non-zero-payload.patch.patch.patch [bz#1007815]
- kvm-raw-posix-implement-write_zeroes-with-MAY_UNMAP-for-.patch.patch.patch.patch [bz#1007815]
- kvm-raw-posix-implement-write_zeroes-with-MAY_UNMAP-for-.patch.patch.patch.patch.patch [bz#1007815]
- kvm-raw-posix-add-support-for-write_zeroes-on-XFS-and-bl.patch.patch [bz#1007815]
- kvm-qemu-iotests-033-is-fast.patch.patch [bz#1007815]
- kvm-qemu-img-add-support-for-skipping-zeroes-in-input-du.patch.patch [bz#1007815]
- kvm-qemu-img-fix-usage-instruction-for-qemu-img-convert.patch.patch [bz#1007815]
- kvm-block-iscsi-set-bdi-cluster_size.patch.patch [bz#1007815]
- kvm-block-add-opt_transfer_length-to-BlockLimits.patch.patch [bz#1039557]
- kvm-block-iscsi-set-bs-bl.opt_transfer_length.patch.patch [bz#1039557]
- kvm-qemu-img-dynamically-adjust-iobuffer-size-during-con.patch.patch [bz#1039557]
- kvm-qemu-img-round-down-request-length-to-an-aligned-sec.patch.patch [bz#1039557]
- kvm-qemu-img-decrease-progress-update-interval-on-conver.patch.patch [bz#1039557]
- Resolves: bz#1007815
  (fix WRITE SAME support)
- Resolves: bz#1039557
  (optimize qemu-img for thin provisioned images)

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 10:1.5.3-31
- Mass rebuild 2013-12-27

* Wed Dec 18 2013 Michal Novotny <minovotn@redhat.com> - 1.5.3-30.el7
- kvm-Revert-HMP-Disable-drive_add-for-Red-Hat-Enterprise-2.patch.patch [bz#889051]
- Resolves: bz#889051
  (Commands "__com.redhat_drive_add/del" don' t exist in RHEL7.0)

* Wed Dec 18 2013 Michal Novotny <minovotn@redhat.com> - 1.5.3-29.el7
- kvm-QMP-Forward-port-__com.redhat_drive_del-from-RHEL-6.patch [bz#889051]
- kvm-QMP-Forward-port-__com.redhat_drive_add-from-RHEL-6.patch [bz#889051]
- kvm-HMP-Forward-port-__com.redhat_drive_add-from-RHEL-6.patch [bz#889051]
- kvm-QMP-Document-throttling-parameters-of-__com.redhat_d.patch [bz#889051]
- kvm-HMP-Disable-drive_add-for-Red-Hat-Enterprise-Linux.patch [bz#889051]
- Resolves: bz#889051
  (Commands "__com.redhat_drive_add/del" don' t exist in RHEL7.0)

* Wed Dec 18 2013 Michal Novotny <minovotn@redhat.com> - 1.5.3-28.el7
- kvm-virtio_pci-fix-level-interrupts-with-irqfd.patch [bz#1035132]
- Resolves: bz#1035132
  (fail to boot and call trace with x-data-plane=on specified for rhel6.5 guest)

* Wed Dec 18 2013 Michal Novotny <minovotn@redhat.com> - 1.5.3-27.el7
- Change systemd service location [bz#1025217]
- kvm-vmdk-Allow-read-only-open-of-VMDK-version-3.patch [bz#1007710 bz#1029852]
- Resolves: bz#1007710
  ([RFE] Enable qemu-img to support VMDK version 3)
- Resolves: bz#1025217
  (systemd can't control ksm.service and ksmtuned.service)
- Resolves: bz#1029852
  (qemu-img fails to convert vmdk image with "qemu-img: Could not open 'image.vmdk'")

* Wed Dec 18 2013 Michal Novotny <minovotn@redhat.com> - 1.5.3-26.el7
- Add BuildRequires to libRDMAcm-devel for RDMA support [bz#1011720]
- kvm-add-a-header-file-for-atomic-operations.patch [bz#1011720]
- kvm-savevm-Fix-potential-memory-leak.patch [bz#1011720]
- kvm-migration-Fail-migration-on-bdrv_flush_all-error.patch [bz#1011720]
- kvm-rdma-add-documentation.patch [bz#1011720]
- kvm-rdma-introduce-qemu_update_position.patch [bz#1011720]
- kvm-rdma-export-yield_until_fd_readable.patch [bz#1011720]
- kvm-rdma-export-throughput-w-MigrationStats-QMP.patch [bz#1011720]
- kvm-rdma-introduce-qemu_file_mode_is_not_valid.patch [bz#1011720]
- kvm-rdma-introduce-qemu_ram_foreach_block.patch [bz#1011720]
- kvm-rdma-new-QEMUFileOps-hooks.patch [bz#1011720]
- kvm-rdma-introduce-capability-x-rdma-pin-all.patch [bz#1011720]
- kvm-rdma-update-documentation-to-reflect-new-unpin-suppo.patch [bz#1011720]- kvm-rdma-bugfix-ram_control_save_page.patch [bz#1011720]
- kvm-rdma-introduce-ram_handle_compressed.patch [bz#1011720]
- kvm-rdma-core-logic.patch [bz#1011720]
- kvm-rdma-send-pc.ram.patch [bz#1011720]
- kvm-rdma-allow-state-transitions-between-other-states-be.patch [bz#1011720]
- kvm-rdma-introduce-MIG_STATE_NONE-and-change-MIG_STATE_S.patch [bz#1011720]
- kvm-rdma-account-for-the-time-spent-in-MIG_STATE_SETUP-t.patch [bz#1011720]
- kvm-rdma-bugfix-make-IPv6-support-work.patch [bz#1011720]
- kvm-rdma-forgot-to-turn-off-the-debugging-flag.patch [bz#1011720]
- kvm-rdma-correct-newlines-in-error-statements.patch [bz#1011720]
- kvm-rdma-don-t-use-negative-index-to-array.patch [bz#1011720]
- kvm-rdma-qemu_rdma_post_send_control-uses-wrongly-RDMA_W.patch [bz#1011720]
- kvm-rdma-use-DRMA_WRID_READY.patch [bz#1011720]
- kvm-rdma-memory-leak-RDMAContext-host.patch [bz#1011720]
- kvm-rdma-use-resp.len-after-validation-in-qemu_rdma_regi.patch [bz#1011720]
- kvm-rdma-validate-RDMAControlHeader-len.patch [bz#1011720]
- kvm-rdma-check-if-RDMAControlHeader-len-match-transferre.patch [bz#1011720]
- kvm-rdma-proper-getaddrinfo-handling.patch [bz#1011720]
- kvm-rdma-IPv6-over-Ethernet-RoCE-is-broken-in-linux-work.patch [bz#1011720]
- kvm-rdma-remaining-documentation-fixes.patch [bz#1011720]
- kvm-rdma-silly-ipv6-bugfix.patch [bz#1011720]
- kvm-savevm-fix-wrong-initialization-by-ram_control_load_.patch [bz#1011720]
- kvm-arch_init-right-return-for-ram_save_iterate.patch [bz#1011720]
- kvm-rdma-clean-up-of-qemu_rdma_cleanup.patch [bz#1011720]
- kvm-rdma-constify-ram_chunk_-index-start-end.patch [bz#1011720]
- kvm-migration-Fix-debug-print-type.patch [bz#1011720]
- kvm-arch_init-make-is_zero_page-accept-size.patch [bz#1011720]
- kvm-migration-ram_handle_compressed.patch [bz#1011720]
- kvm-migration-fix-spice-migration.patch [bz#1011720]
- kvm-pci-assign-cap-number-of-devices-that-can-be-assigne.patch [bz#678368]
- kvm-vfio-cap-number-of-devices-that-can-be-assigned.patch [bz#678368]
- kvm-Revert-usb-tablet-Don-t-claim-wakeup-capability-for-.patch [bz#1039513]
- kvm-mempath-prefault-pages-manually-v4.patch [bz#1026554]
- Resolves: bz#1011720
  ([HP 7.0 Feat]: Backport RDMA based live guest migration changes from upstream to RHEL7.0 KVM)
- Resolves: bz#1026554
  (qemu: mempath: prefault pages manually)
- Resolves: bz#1039513
  (backport remote wakeup for ehci)
- Resolves: bz#678368
  (RFE: Support more than 8 assigned devices)

* Wed Dec 18 2013 Michal Novotny <minovotn@redhat.com> - 1.5.3-25.el7
- kvm-Change-package-description.patch [bz#1017696]
- kvm-seccomp-add-kill-to-the-syscall-whitelist.patch [bz#1026314]
- kvm-json-parser-fix-handling-of-large-whole-number-value.patch [bz#997915]
- kvm-qapi-add-QMP-input-test-for-large-integers.patch [bz#997915]
- kvm-qapi-fix-visitor-serialization-tests-for-numbers-dou.patch [bz#997915]
- kvm-qapi-add-native-list-coverage-for-visitor-serializat.patch [bz#997915]
- kvm-qapi-add-native-list-coverage-for-QMP-output-visitor.patch [bz#997915]
- kvm-qapi-add-native-list-coverage-for-QMP-input-visitor-.patch [bz#997915]
- kvm-qapi-lack-of-two-commas-in-dict.patch [bz#997915]
- kvm-tests-QAPI-schema-parser-tests.patch [bz#997915]
- kvm-tests-Use-qapi-schema-test.json-as-schema-parser-tes.patch [bz#997915]
- kvm-qapi.py-Restructure-lexer-and-parser.patch [bz#997915]
- kvm-qapi.py-Decent-syntax-error-reporting.patch [bz#997915]
- kvm-qapi.py-Reject-invalid-characters-in-schema-file.patch [bz#997915]
- kvm-qapi.py-Fix-schema-parser-to-check-syntax-systematic.patch [bz#997915]
- kvm-qapi.py-Fix-diagnosing-non-objects-at-a-schema-s-top.patch [bz#997915]
- kvm-qapi.py-Rename-expr_eval-to-expr-in-parse_schema.patch [bz#997915]
- kvm-qapi.py-Permit-comments-starting-anywhere-on-the-lin.patch [bz#997915]
- kvm-scripts-qapi.py-Avoid-syntax-not-supported-by-Python.patch [bz#997915]
- kvm-tests-Fix-schema-parser-test-for-in-tree-build.patch [bz#997915]
- Resolves: bz#1017696
  ([branding] remove references to dynamic translation and user-mode emulation)
- Resolves: bz#1026314
  (qemu-kvm hang when use '-sandbox on'+'vnc'+'hda')
- Resolves: bz#997915
  (Backport new QAPI parser proactively to help developers and avoid silly conflicts)
    
* Tue Dec 17 2013 Michal Novotny <minovotn@redhat.com> - 1.5.3-24.el7
- kvm-range-add-Range-structure.patch [bz#1034876]
- kvm-range-add-Range-to-typedefs.patch [bz#1034876]
- kvm-range-add-min-max-operations-on-ranges.patch [bz#1034876]
- kvm-qdev-Add-SIZE-type-to-qdev-properties.patch [bz#1034876]
- kvm-qapi-make-visit_type_size-fallback-to-type_int.patch [bz#1034876]
- kvm-pc-move-IO_APIC_DEFAULT_ADDRESS-to-include-hw-i386-i.patch [bz#1034876]
- kvm-pci-add-helper-to-retrieve-the-64-bit-range.patch [bz#1034876]
- kvm-pci-fix-up-w64-size-calculation-helper.patch [bz#1034876]
- kvm-refer-to-FWCfgState-explicitly.patch [bz#1034876]
- kvm-fw_cfg-move-typedef-to-qemu-typedefs.h.patch [bz#1034876]
- kvm-arch_init-align-MR-size-to-target-page-size.patch [bz#1034876]
- kvm-loader-store-FW-CFG-ROM-files-in-RAM.patch [bz#1034876]
- kvm-pci-store-PCI-hole-ranges-in-guestinfo-structure.patch [bz#1034876]
- kvm-pc-pass-PCI-hole-ranges-to-Guests.patch [bz#1034876]
- kvm-pc-replace-i440fx_common_init-with-i440fx_init.patch [bz#1034876]
- kvm-pc-don-t-access-fw-cfg-if-NULL.patch [bz#1034876]
- kvm-pc-add-I440FX-QOM-cast-macro.patch [bz#1034876]
- kvm-pc-limit-64-bit-hole-to-2G-by-default.patch [bz#1034876]
- kvm-q35-make-pci-window-address-size-match-guest-cfg.patch [bz#1034876]
- kvm-q35-use-64-bit-window-programmed-by-guest.patch [bz#1034876]
- kvm-piix-use-64-bit-window-programmed-by-guest.patch [bz#1034876]
- kvm-pc-fix-regression-for-64-bit-PCI-memory.patch [bz#1034876]
- kvm-cleanup-object.h-include-error.h-directly.patch [bz#1034876]
- kvm-qom-cleanup-struct-Error-references.patch [bz#1034876]
- kvm-qom-add-pointer-to-int-property-helpers.patch [bz#1034876]
- kvm-fw_cfg-interface-to-trigger-callback-on-read.patch [bz#1034876]
- kvm-loader-support-for-unmapped-ROM-blobs.patch [bz#1034876]
- kvm-pcie_host-expose-UNMAPPED-macro.patch [bz#1034876]
- kvm-pcie_host-expose-address-format.patch [bz#1034876]
- kvm-q35-use-macro-for-MCFG-property-name.patch [bz#1034876]
- kvm-q35-expose-mmcfg-size-as-a-property.patch [bz#1034876]
- kvm-i386-add-ACPI-table-files-from-seabios.patch [bz#1034876]
- kvm-acpi-add-rules-to-compile-ASL-source.patch [bz#1034876]
- kvm-acpi-pre-compiled-ASL-files.patch [bz#1034876]
- kvm-acpi-ssdt-pcihp-updat-generated-file.patch [bz#1034876]
- kvm-loader-use-file-path-size-from-fw_cfg.h.patch [bz#1034876]
- kvm-i386-add-bios-linker-loader.patch [bz#1034876]
- kvm-loader-allow-adding-ROMs-in-done-callbacks.patch [bz#1034876]
- kvm-i386-define-pc-guest-info.patch [bz#1034876]
- kvm-acpi-piix-add-macros-for-acpi-property-names.patch [bz#1034876]
- kvm-piix-APIs-for-pc-guest-info.patch [bz#1034876]
- kvm-ich9-APIs-for-pc-guest-info.patch [bz#1034876]
- kvm-pvpanic-add-API-to-access-io-port.patch [bz#1034876]
- kvm-hpet-add-API-to-find-it.patch [bz#1034876]
- kvm-hpet-fix-build-with-CONFIG_HPET-off.patch [bz#1034876]
- kvm-acpi-add-interface-to-access-user-installed-tables.patch [bz#1034876]
- kvm-pc-use-new-api-to-add-builtin-tables.patch [bz#1034876]
- kvm-i386-ACPI-table-generation-code-from-seabios.patch [bz#1034876]
- kvm-ssdt-fix-PBLK-length.patch [bz#1034876]
- kvm-ssdt-proc-update-generated-file.patch [bz#1034876]
- kvm-pc-disable-pci-info.patch [bz#1034876]
- kvm-acpi-build-fix-build-on-glib-2.22.patch [bz#1034876]
- kvm-acpi-build-fix-build-on-glib-2.14.patch [bz#1034876]
- kvm-acpi-build-fix-support-for-glib-2.22.patch [bz#1034876]
- kvm-acpi-build-Fix-compiler-warning-missing-gnu_printf-f.patch [bz#1034876]
- kvm-exec-Fix-prototype-of-phys_mem_set_alloc-and-related.patch [bz#1034876]
- Resolves: bz#1034876
  (export acpi tables to guests)

* Tue Dec 17 2013 Michal Novotny <minovotn@redhat.com> - 1.5.3-23.el7
- kvm-qdev-monitor-Unref-device-when-device_add-fails.patch [bz#1003773]
- kvm-qdev-Drop-misleading-qdev_free-function.patch [bz#1003773]
- kvm-blockdev-fix-drive_init-opts-and-bs_opts-leaks.patch [bz#1003773]
- kvm-libqtest-rename-qmp-to-qmp_discard_response.patch [bz#1003773]
- kvm-libqtest-add-qmp-fmt-.-QDict-function.patch [bz#1003773]
- kvm-blockdev-test-add-test-case-for-drive_add-duplicate-.patch [bz#1003773]
- kvm-qdev-monitor-test-add-device_add-leak-test-cases.patch [bz#1003773]
- kvm-qtest-Use-display-none-by-default.patch [bz#1003773]
- Resolves: bz#1003773
  (When virtio-blk-pci device with dataplane is failed to be added, the drive cannot be released.)

* Tue Dec 17 2013 Michal Novotny <minovotn@redhat.com> - 1.5.3-22.el7
- Fix ksmtuned with set_process_name=1 [bz#1027420]
- Fix committed memory when no qemu-kvm running [bz#1027418]
- kvm-virtio-net-fix-the-memory-leak-in-rxfilter_notify.patch [bz#1033810]
- kvm-qom-Fix-memory-leak-in-object_property_set_link.patch [bz#1033810]
- kvm-fix-intel-hda-live-migration.patch [bz#1036537]
- kvm-vfio-pci-Release-all-MSI-X-vectors-when-disabled.patch [bz#1029743]
- kvm-Query-KVM-for-available-memory-slots.patch [bz#921490]
- kvm-block-Dont-ignore-previously-set-bdrv_flags.patch [bz#1039501]
- kvm-cleanup-trace-events.pl-New.patch [bz#997832]
- kvm-slavio_misc-Fix-slavio_led_mem_readw-_writew-tracepo.patch [bz#997832]
- kvm-milkymist-minimac2-Fix-minimac2_read-_write-tracepoi.patch [bz#997832]
- kvm-trace-events-Drop-unused-events.patch [bz#997832]
- kvm-trace-events-Fix-up-source-file-comments.patch [bz#997832]
- kvm-trace-events-Clean-up-with-scripts-cleanup-trace-eve.patch [bz#997832]
- kvm-trace-events-Clean-up-after-removal-of-old-usb-host-.patch [bz#997832]
- kvm-net-Update-netdev-peer-on-link-change.patch [bz#1027571]
- Resolves: bz#1027418
  (ksmtuned committed_memory() still returns "", not 0, when no qemu running)
- Resolves: bz#1027420
  (ksmtuned can’t handle libvirt WITH set_process_name=1)
- Resolves: bz#1027571
  ([virtio-win]win8.1 guest network can not resume automatically after do "set_link tap1 on")
- Resolves: bz#1029743
  (qemu-kvm core dump after hot plug/unplug 82576 PF about 100 times)
- Resolves: bz#1033810
  (memory leak in using object_get_canonical_path())
- Resolves: bz#1036537
  (Cross version migration from RHEL6.5 host to RHEL7.0 host with sound device failed.)
- Resolves: bz#1039501
  ([provisioning] discard=on broken)
- Resolves: bz#921490
  (qemu-kvm core dumped after hot plugging more than 11 VF through vfio-pci)
- Resolves: bz#997832
  (Backport trace fixes proactively to avoid confusion and silly conflicts)

* Tue Dec 03 2013 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-21.el7
- kvm-scsi-Allocate-SCSITargetReq-r-buf-dynamically-CVE-20.patch [bz#1007334]
- Resolves: bz#1007334
  (CVE-2013-4344 qemu-kvm: qemu: buffer overflow in scsi_target_emulate_report_luns [rhel-7.0])

* Thu Nov 28 2013 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-20.el7
- kvm-pc-drop-virtio-balloon-pci-event_idx-compat-property.patch [bz#1029539]
- kvm-virtio-net-only-delete-bh-that-existed.patch [bz#922463]
- kvm-virtio-net-broken-RX-filtering-logic-fixed.patch [bz#1029370]
- kvm-block-Avoid-unecessary-drv-bdrv_getlength-calls.patch [bz#1025138]
- kvm-block-Round-up-total_sectors.patch [bz#1025138]
- kvm-doc-fix-hardcoded-helper-path.patch [bz#1016952]
- kvm-introduce-RFQDN_REDHAT-RHEL-6-7-fwd.patch [bz#971933]
- kvm-error-reason-in-BLOCK_IO_ERROR-BLOCK_JOB_ERROR-event.patch [bz#971938]
- kvm-improve-debuggability-of-BLOCK_IO_ERROR-BLOCK_JOB_ER.patch [bz#895041]
- kvm-vfio-pci-Fix-multifunction-on.patch [bz#1029275]
- kvm-qcow2-Change-default-for-new-images-to-compat-1.1.patch [bz#1026739]
- kvm-qcow2-change-default-for-new-images-to-compat-1.1-pa.patch [bz#1026739]
- kvm-rng-egd-offset-the-point-when-repeatedly-read-from-t.patch [bz#1032862]
- kvm-Fix-rhel-rhev-conflict-for-qemu-kvm-common.patch [bz#1033463]
- Resolves: bz#1016952
  (qemu-kvm man page guide wrong path for qemu-bridge-helper)
- Resolves: bz#1025138
  (Read/Randread/Randrw performance regression)
- Resolves: bz#1026739
  (qcow2: Switch to compat=1.1 default for new images)
- Resolves: bz#1029275
  (Guest only find one 82576 VF(function 0) while use multifunction)
- Resolves: bz#1029370
  ([whql][netkvm][wlk] Virtio-net device handles RX multicast filtering improperly)
- Resolves: bz#1029539
  (Machine type rhel6.1.0 and  balloon device cause migration fail from RHEL6.5 host to RHEL7.0 host)
- Resolves: bz#1032862
  (virtio-rng-egd: repeatedly read same random data-block w/o considering the buffer offset)
- Resolves: bz#1033463
  (can not upgrade qemu-kvm-common to qemu-kvm-common-rhev due to conflicts)
- Resolves: bz#895041
  (QMP: forward port I/O error debug messages)
- Resolves: bz#922463
  (qemu-kvm core dump when virtio-net multi queue guest hot-unpluging vNIC)
- Resolves: bz#971933
  (QMP: add RHEL's vendor extension prefix)
- Resolves: bz#971938
  (QMP: Add error reason to BLOCK_IO_ERROR event)

* Mon Nov 11 2013 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-19.el7
- kvm-qapi-qapi-visit.py-fix-list-handling-for-union-types.patch [bz#848203]
- kvm-qapi-qapi-visit.py-native-list-support.patch [bz#848203]
- kvm-qapi-enable-generation-of-native-list-code.patch [bz#848203]
- kvm-net-add-support-of-mac-programming-over-macvtap-in-Q.patch [bz#848203]
- Resolves: bz#848203
  (MAC Programming for virtio over macvtap - qemu-kvm support)

* Fri Nov 08 2013 Michal Novotny <minovotn@redhat.com> - 1.5.3-18.el7
- Removing leaked patch kvm-e1000-rtl8139-update-HMP-NIC-when-every-bit-is-writt.patch

* Thu Nov 07 2013 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-17.el7
- kvm-pci-assign-Add-MSI-affinity-support.patch [bz#1025877]
- kvm-Fix-potential-resource-leak-missing-fclose.patch [bz#1025877]
- kvm-pci-assign-remove-the-duplicate-function-name-in-deb.patch [bz#1025877]
- kvm-Remove-s390-ccw-img-loader.patch [bz#1017682]
- kvm-Fix-vscclient-installation.patch [bz#1017681]
- kvm-Change-qemu-bridge-helper-permissions-to-4755.patch [bz#1017689]
- kvm-net-update-nic-info-during-device-reset.patch [bz#922589]
- kvm-net-e1000-update-network-information-when-macaddr-is.patch [bz#922589]
- kvm-net-rtl8139-update-network-information-when-macaddr-.patch [bz#922589]
- kvm-virtio-net-fix-up-HMP-NIC-info-string-on-reset.patch [bz#1026689]
- kvm-vfio-pci-VGA-quirk-update.patch [bz#1025477]
- kvm-vfio-pci-Add-support-for-MSI-affinity.patch [bz#1025477]
- kvm-vfio-pci-Test-device-reset-capabilities.patch [bz#1026550]
- kvm-vfio-pci-Lazy-PCI-option-ROM-loading.patch [bz#1026550]
- kvm-vfio-pci-Cleanup-error_reports.patch [bz#1026550]
- kvm-vfio-pci-Add-dummy-PCI-ROM-write-accessor.patch [bz#1026550]
- kvm-vfio-pci-Fix-endian-issues-in-vfio_pci_size_rom.patch [bz#1026550]
- kvm-linux-headers-Update-to-include-vfio-pci-hot-reset-s.patch [bz#1025472]
- kvm-vfio-pci-Implement-PCI-hot-reset.patch [bz#1025472]
- kvm-linux-headers-Update-for-KVM-VFIO-device.patch [bz#1025474]
- kvm-vfio-pci-Make-use-of-new-KVM-VFIO-device.patch [bz#1025474]
- kvm-vmdk-Fix-vmdk_parse_extents.patch [bz#995866]
- kvm-vmdk-fix-VMFS-extent-parsing.patch [bz#995866]
- kvm-e1000-rtl8139-update-HMP-NIC-when-every-bit-is-writt.patch [bz#922589]
- kvm-don-t-disable-ctrl_mac_addr-feature-for-6.5-machine-.patch [bz#1005039]
- Resolves: bz#1005039
  (add compat property to disable ctrl_mac_addr feature)
- Resolves: bz#1017681
  (rpmdiff test "Multilib regressions": vscclient is a libtool script on s390/s390x/ppc/ppc64)
- Resolves: bz#1017682
  (/usr/share/qemu-kvm/s390-ccw.img need not be distributed)
- Resolves: bz#1017689
  (/usr/libexec/qemu-bridge-helper permissions should be 4755)
- Resolves: bz#1025472
  (Nvidia GPU device assignment - qemu-kvm - bus reset support)
- Resolves: bz#1025474
  (Nvidia GPU device assignment - qemu-kvm - NoSnoop support)
- Resolves: bz#1025477
  (VFIO MSI affinity)
- Resolves: bz#1025877
  (pci-assign lacks MSI affinity support)
- Resolves: bz#1026550
  (QEMU VFIO update ROM loading code)
- Resolves: bz#1026689
  (virtio-net: macaddr is reset but network info of monitor isn't updated)
- Resolves: bz#922589
  (e1000/rtl8139: qemu mac address can not be changed via set the hardware address in guest)
- Resolves: bz#995866
  (fix vmdk support to ESX images)

* Thu Nov 07 2013 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-16.el7
- kvm-block-drop-bs_snapshots-global-variable.patch [bz#1026524]
- kvm-block-move-snapshot-code-in-block.c-to-block-snapsho.patch [bz#1026524]
- kvm-block-fix-vvfat-error-path-for-enable_write_target.patch [bz#1026524]
- kvm-block-Bugfix-format-and-snapshot-used-in-drive-optio.patch [bz#1026524]
- kvm-iscsi-use-bdrv_new-instead-of-stack-structure.patch [bz#1026524]
- kvm-qcow2-Add-corrupt-bit.patch [bz#1004347]
- kvm-qcow2-Metadata-overlap-checks.patch [bz#1004347]
- kvm-qcow2-Employ-metadata-overlap-checks.patch [bz#1004347]
- kvm-qcow2-refcount-Move-OFLAG_COPIED-checks.patch [bz#1004347]
- kvm-qcow2-refcount-Repair-OFLAG_COPIED-errors.patch [bz#1004347]
- kvm-qcow2-refcount-Repair-shared-refcount-blocks.patch [bz#1004347]
- kvm-qcow2_check-Mark-image-consistent.patch [bz#1004347]
- kvm-qemu-iotests-Overlapping-cluster-allocations.patch [bz#1004347]
- kvm-w32-Fix-access-to-host-devices-regression.patch [bz#1026524]
- kvm-add-qemu-img-convert-n-option-skip-target-volume-cre.patch [bz#1026524]
- kvm-bdrv-Use-Error-for-opening-images.patch [bz#1026524]
- kvm-bdrv-Use-Error-for-creating-images.patch [bz#1026524]
- kvm-block-Error-parameter-for-open-functions.patch [bz#1026524]
- kvm-block-Error-parameter-for-create-functions.patch [bz#1026524]
- kvm-qemu-img-create-Emit-filename-on-error.patch [bz#1026524]
- kvm-qcow2-Use-Error-parameter.patch [bz#1026524]
- kvm-qemu-iotests-Adjustments-due-to-error-propagation.patch [bz#1026524]
- kvm-block-raw-Employ-error-parameter.patch [bz#1026524]
- kvm-block-raw-win32-Employ-error-parameter.patch [bz#1026524]
- kvm-blkdebug-Employ-error-parameter.patch [bz#1026524]
- kvm-blkverify-Employ-error-parameter.patch [bz#1026524]
- kvm-block-raw-posix-Employ-error-parameter.patch [bz#1026524]
- kvm-block-raw-win32-Always-use-errno-in-hdev_open.patch [bz#1026524]
- kvm-qmp-Documentation-for-BLOCK_IMAGE_CORRUPTED.patch [bz#1004347]
- kvm-qcow2-Correct-snapshots-size-for-overlap-check.patch [bz#1004347]
- kvm-qcow2-CHECK_OFLAG_COPIED-is-obsolete.patch [bz#1004347]
- kvm-qcow2-Correct-endianness-in-overlap-check.patch [bz#1004347]
- kvm-qcow2-Switch-L1-table-in-a-single-sequence.patch [bz#1004347]
- kvm-qcow2-Use-pread-for-inactive-L1-in-overlap-check.patch [bz#1004347]
- kvm-qcow2-Remove-wrong-metadata-overlap-check.patch [bz#1004347]
- kvm-qcow2-Use-negated-overflow-check-mask.patch [bz#1004347]
- kvm-qcow2-Make-overlap-check-mask-variable.patch [bz#1004347]
- kvm-qcow2-Add-overlap-check-options.patch [bz#1004347]
- kvm-qcow2-Array-assigning-options-to-OL-check-bits.patch [bz#1004347]
- kvm-qcow2-Add-more-overlap-check-bitmask-macros.patch [bz#1004347]
- kvm-qcow2-Evaluate-overlap-check-options.patch [bz#1004347]
- kvm-qapi-types.py-Split-off-generate_struct_fields.patch [bz#978402]
- kvm-qapi-types.py-Fix-enum-struct-sizes-on-i686.patch [bz#978402]
- kvm-qapi-types-visit.py-Pass-whole-expr-dict-for-structs.patch [bz#978402]
- kvm-qapi-types-visit.py-Inheritance-for-structs.patch [bz#978402]
- kvm-blockdev-Introduce-DriveInfo.enable_auto_del.patch [bz#978402]
- kvm-Implement-qdict_flatten.patch [bz#978402]
- kvm-blockdev-blockdev-add-QMP-command.patch [bz#978402]
- kvm-blockdev-Separate-ID-generation-from-DriveInfo-creat.patch [bz#978402]
- kvm-blockdev-Pass-QDict-to-blockdev_init.patch [bz#978402]
- kvm-blockdev-Move-parsing-of-media-option-to-drive_init.patch [bz#978402]
- kvm-blockdev-Move-parsing-of-if-option-to-drive_init.patch [bz#978402]
- kvm-blockdev-Moving-parsing-of-geometry-options-to-drive.patch [bz#978402]
- kvm-blockdev-Move-parsing-of-boot-option-to-drive_init.patch [bz#978402]
- kvm-blockdev-Move-bus-unit-index-processing-to-drive_ini.patch [bz#978402]
- kvm-blockdev-Move-virtio-blk-device-creation-to-drive_in.patch [bz#978402]
- kvm-blockdev-Remove-IF_-check-for-read-only-blockdev_ini.patch [bz#978402]
- kvm-qemu-iotests-Check-autodel-behaviour-for-device_del.patch [bz#978402]
- kvm-blockdev-Remove-media-parameter-from-blockdev_init.patch [bz#978402]
- kvm-blockdev-Don-t-disable-COR-automatically-with-blockd.patch [bz#978402]
- kvm-blockdev-blockdev_init-error-conversion.patch [bz#978402]
- kvm-sd-Avoid-access-to-NULL-BlockDriverState.patch [bz#978402]
- kvm-blockdev-fix-cdrom-read_only-flag.patch [bz#978402]
- kvm-block-fix-backing-file-overriding.patch [bz#978402]
- kvm-block-Disable-BDRV_O_COPY_ON_READ-for-the-backing-fi.patch [bz#978402]
- kvm-block-Don-t-copy-backing-file-name-on-error.patch [bz#978402]
- kvm-qemu-iotests-Try-creating-huge-qcow2-image.patch [bz#980771]
- kvm-block-move-qmp-and-info-dump-related-code-to-block-q.patch [bz#980771]
- kvm-block-dump-snapshot-and-image-info-to-specified-outp.patch [bz#980771]
- kvm-block-add-snapshot-info-query-function-bdrv_query_sn.patch [bz#980771]
- kvm-block-add-image-info-query-function-bdrv_query_image.patch [bz#980771]
- kvm-qmp-add-ImageInfo-in-BlockDeviceInfo-used-by-query-b.patch [bz#980771]
- kvm-vmdk-Implement-.bdrv_has_zero_init.patch [bz#980771]
- kvm-qemu-iotests-Add-basic-ability-to-use-binary-sample-.patch [bz#980771]
- kvm-qemu-iotests-Quote-TEST_IMG-and-TEST_DIR-usage.patch [bz#980771]
- kvm-qemu-iotests-fix-test-case-059.patch [bz#980771]
- kvm-qapi-Add-ImageInfoSpecific-type.patch [bz#980771]
- kvm-block-Add-bdrv_get_specific_info.patch [bz#980771]
- kvm-block-qapi-Human-readable-ImageInfoSpecific-dump.patch [bz#980771]
- kvm-qcow2-Add-support-for-ImageInfoSpecific.patch [bz#980771]
- kvm-qemu-iotests-Discard-specific-info-in-_img_info.patch [bz#980771]
- kvm-qemu-iotests-Additional-info-from-qemu-img-info.patch [bz#980771]
- kvm-vmdk-convert-error-code-to-use-errp.patch [bz#980771]
- kvm-vmdk-refuse-enabling-zeroed-grain-with-flat-images.patch [bz#980771]
- kvm-qapi-Add-optional-field-compressed-to-ImageInfo.patch [bz#980771]
- kvm-vmdk-Only-read-cid-from-image-file-when-opening.patch [bz#980771]
- kvm-vmdk-Implment-bdrv_get_specific_info.patch [bz#980771]
- Resolves: bz#1004347
  (Backport qcow2 corruption prevention patches)
- Resolves: bz#1026524
  (Backport block layer error parameter patches)
- Resolves: bz#978402
  ([RFE] Add discard support to qemu-kvm layer)
- Resolves: bz#980771
  ([RFE]  qemu-img should be able to tell the compat version of a qcow2 image)

* Thu Nov 07 2013 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-15.el7
- kvm-cow-make-reads-go-at-a-decent-speed.patch [bz#989646]
- kvm-cow-make-writes-go-at-a-less-indecent-speed.patch [bz#989646]
- kvm-cow-do-not-call-bdrv_co_is_allocated.patch [bz#989646]
- kvm-block-keep-bs-total_sectors-up-to-date-even-for-grow.patch [bz#989646]
- kvm-block-make-bdrv_co_is_allocated-static.patch [bz#989646]
- kvm-block-do-not-use-total_sectors-in-bdrv_co_is_allocat.patch [bz#989646]
- kvm-block-remove-bdrv_is_allocated_above-bdrv_co_is_allo.patch [bz#989646]
- kvm-block-expect-errors-from-bdrv_co_is_allocated.patch [bz#989646]
- kvm-block-Fix-compiler-warning-Werror-uninitialized.patch [bz#989646]
- kvm-qemu-img-always-probe-the-input-image-for-allocated-.patch [bz#989646]
- kvm-block-make-bdrv_has_zero_init-return-false-for-copy-.patch [bz#989646]
- kvm-block-introduce-bdrv_get_block_status-API.patch [bz#989646]
- kvm-block-define-get_block_status-return-value.patch [bz#989646]
- kvm-block-return-get_block_status-data-and-flags-for-for.patch [bz#989646]
- kvm-block-use-bdrv_has_zero_init-to-return-BDRV_BLOCK_ZE.patch [bz#989646]
- kvm-block-return-BDRV_BLOCK_ZERO-past-end-of-backing-fil.patch [bz#989646]
- kvm-qemu-img-add-a-map-subcommand.patch [bz#989646]
- kvm-docs-qapi-document-qemu-img-map.patch [bz#989646]
- kvm-raw-posix-return-get_block_status-data-and-flags.patch [bz#989646]
- kvm-raw-posix-report-unwritten-extents-as-zero.patch [bz#989646]
- kvm-block-add-default-get_block_status-implementation-fo.patch [bz#989646]
- kvm-block-look-for-zero-blocks-in-bs-file.patch [bz#989646]
- kvm-qemu-img-fix-invalid-JSON.patch [bz#989646]
- kvm-block-get_block_status-set-pnum-0-on-error.patch [bz#989646]
- kvm-block-get_block_status-avoid-segfault-if-there-is-no.patch [bz#989646]
- kvm-block-get_block_status-avoid-redundant-callouts-on-r.patch [bz#989646]
- kvm-qcow2-Restore-total_sectors-value-in-save_vmstate.patch [bz#1025740]
- kvm-qcow2-Unset-zero_beyond_eof-in-save_vmstate.patch [bz#1025740]
- kvm-qemu-iotests-Test-for-loading-VM-state-from-qcow2.patch [bz#1025740]
- kvm-apic-rename-apic-specific-bitopts.patch [bz#1001216]
- kvm-hw-import-bitmap-operations-in-qdev-core-header.patch [bz#1001216]
- kvm-qemu-help-Sort-devices-by-logical-functionality.patch [bz#1001216]
- kvm-devices-Associate-devices-to-their-logical-category.patch [bz#1001216]
- kvm-Mostly-revert-qemu-help-Sort-devices-by-logical-func.patch [bz#1001216]
- kvm-qdev-monitor-Group-device_add-help-and-info-qdm-by-c.patch [bz#1001216]
- kvm-qdev-Replace-no_user-by-cannot_instantiate_with_devi.patch [bz#1001216]
- kvm-sysbus-Set-cannot_instantiate_with_device_add_yet.patch [bz#1001216]
- kvm-cpu-Document-why-cannot_instantiate_with_device_add_.patch [bz#1001216]
- kvm-apic-Document-why-cannot_instantiate_with_device_add.patch [bz#1001216]
- kvm-pci-host-Consistently-set-cannot_instantiate_with_de.patch [bz#1001216]
- kvm-ich9-Document-why-cannot_instantiate_with_device_add.patch [bz#1001216]
- kvm-piix3-piix4-Clean-up-use-of-cannot_instantiate_with_.patch [bz#1001216]
- kvm-vt82c686-Clean-up-use-of-cannot_instantiate_with_dev.patch [bz#1001216]
- kvm-isa-Clean-up-use-of-cannot_instantiate_with_device_a.patch [bz#1001216]
- kvm-qdev-Do-not-let-the-user-try-to-device_add-when-it-c.patch [bz#1001216]
- kvm-rhel-Revert-unwanted-cannot_instantiate_with_device_.patch [bz#1001216]
- kvm-rhel-Revert-downstream-changes-to-unused-default-con.patch [bz#1001076]
- kvm-rhel-Drop-cfi.pflash01-and-isa-ide-device.patch [bz#1001076]
- kvm-rhel-Drop-isa-vga-device.patch [bz#1001088]
- kvm-rhel-Make-isa-cirrus-vga-device-unavailable.patch [bz#1001088]
- kvm-rhel-Make-ccid-card-emulated-device-unavailable.patch [bz#1001123]
- kvm-x86-fix-migration-from-pre-version-12.patch [bz#1005695]
- kvm-x86-cpuid-reconstruct-leaf-0Dh-data.patch [bz#1005695]
- kvm-kvmvapic-Catch-invalid-ROM-size.patch [bz#920021]
- kvm-kvmvapic-Enter-inactive-state-on-hardware-reset.patch [bz#920021]
- kvm-kvmvapic-Clear-also-physical-ROM-address-when-enteri.patch [bz#920021]
- kvm-block-optionally-disable-live-block-jobs.patch [bz#987582]
- kvm-rpm-spec-template-disable-live-block-ops-for-rhel-en.patch [bz#987582]
- kvm-migration-disable-live-block-migration-b-i-for-rhel-.patch [bz#1022392]
- kvm-Build-ceph-rbd-only-for-rhev.patch [bz#987583]
- kvm-spec-Disable-host-cdrom-RHEL-only.patch [bz#760885]
- kvm-rhel-Make-pci-serial-2x-and-pci-serial-4x-device-una.patch [bz#1001180]
- kvm-usb-host-libusb-Fix-reset-handling.patch [bz#980415]
- kvm-usb-host-libusb-Configuration-0-may-be-a-valid-confi.patch [bz#980383]
- kvm-usb-host-libusb-Detach-kernel-drivers-earlier.patch [bz#980383]
- kvm-monitor-Remove-pci_add-command-for-Red-Hat-Enterpris.patch [bz#1010858]
- kvm-monitor-Remove-pci_del-command-for-Red-Hat-Enterpris.patch [bz#1010858]
- kvm-monitor-Remove-usb_add-del-commands-for-Red-Hat-Ente.patch [bz#1010858]
- kvm-monitor-Remove-host_net_add-remove-for-Red-Hat-Enter.patch [bz#1010858]
- kvm-fw_cfg-add-API-to-find-FW-cfg-object.patch [bz#990601]
- kvm-pvpanic-use-FWCfgState-explicitly.patch [bz#990601]
- kvm-pvpanic-initialization-cleanup.patch [bz#990601]
- kvm-pvpanic-fix-fwcfg-for-big-endian-hosts.patch [bz#990601]
- kvm-hw-misc-make-pvpanic-known-to-user.patch [bz#990601]
- kvm-gdbstub-do-not-restart-crashed-guest.patch [bz#990601]
- kvm-gdbstub-fix-for-commit-87f25c12bfeaaa0c41fb857713bbc.patch [bz#990601]
- kvm-vl-allow-cont-from-panicked-state.patch [bz#990601]
- kvm-hw-misc-don-t-create-pvpanic-device-by-default.patch [bz#990601]
- kvm-block-vhdx-add-migration-blocker.patch [bz#1007176]
- kvm-qemu-kvm.spec-add-vhdx-to-the-read-only-block-driver.patch [bz#1007176]
- kvm-qemu-kvm.spec-Add-VPC-VHD-driver-to-the-block-read-o.patch [bz#1007176]
- Resolves: bz#1001076
  (Disable or remove other block devices we won't support)
- Resolves: bz#1001088
  (Disable or remove display devices we won't support)
- Resolves: bz#1001123
  (Disable or remove device ccid-card-emulated)
- Resolves: bz#1001180
  (Disable or remove devices pci-serial-2x, pci-serial-4x)
- Resolves: bz#1001216
  (Fix no_user or provide another way make devices unavailable with -device / device_add)
- Resolves: bz#1005695
  (QEMU should hide CPUID.0Dh values that it does not support)
- Resolves: bz#1007176
  (Add VPC and VHDX file formats as supported in qemu-kvm (read-only))
- Resolves: bz#1010858
  (Disable unused human monitor commands)
- Resolves: bz#1022392
  (Disable live-storage-migration in qemu-kvm (migrate -b/-i))
- Resolves: bz#1025740
  (Saving VM state on qcow2 images results in VM state corruption)
- Resolves: bz#760885
  (Disable host cdrom passthrough)
- Resolves: bz#920021
  (qemu-kvm segment fault when reboot guest after hot unplug device with option ROM)
- Resolves: bz#980383
  (The usb3.0 stick can't be returned back to host after shutdown guest with usb3.0 pass-through)
- Resolves: bz#980415
  (libusbx: error [_open_sysfs_attr] open /sys/bus/usb/devices/4-1/bConfigurationValue failed ret=-1 errno=2)
- Resolves: bz#987582
  (Initial Virtualization Differentiation for RHEL7 (Live snapshots))
- Resolves: bz#987583
  (Initial Virtualization Differentiation for RHEL7 (Ceph enablement))
- Resolves: bz#989646
  (Support backup vendors in qemu to access qcow disk readonly)
- Resolves: bz#990601
  (pvpanic device triggers guest bugs when present by default)

* Wed Nov 06 2013 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-14.el7
- kvm-target-i386-remove-tabs-from-target-i386-cpu.h.patch [bz#928867]
- kvm-migrate-vPMU-state.patch [bz#928867]
- kvm-blockdev-do-not-default-cache.no-flush-to-true.patch [bz#1009993]
- kvm-virtio-blk-do-not-relay-a-previous-driver-s-WCE-conf.patch [bz#1009993]
- kvm-rng-random-use-error_setg_file_open.patch [bz#907743]
- kvm-block-mirror_complete-use-error_setg_file_open.patch [bz#907743]
- kvm-blockdev-use-error_setg_file_open.patch [bz#907743]
- kvm-cpus-use-error_setg_file_open.patch [bz#907743]
- kvm-dump-qmp_dump_guest_memory-use-error_setg_file_open.patch [bz#907743]
- kvm-savevm-qmp_xen_save_devices_state-use-error_setg_fil.patch [bz#907743]
- kvm-block-bdrv_reopen_prepare-don-t-use-QERR_OPEN_FILE_F.patch [bz#907743]
- kvm-qerror-drop-QERR_OPEN_FILE_FAILED-macro.patch [bz#907743]
- kvm-rhel-Drop-ivshmem-device.patch [bz#787463]
- kvm-usb-remove-old-usb-host-code.patch [bz#1001144]
- kvm-Add-rhel6-pxe-roms-files.patch [bz#997702]
- kvm-Add-rhel6-pxe-rom-to-redhat-rpm.patch [bz#997702]
- kvm-Fix-migration-from-rhel6.5-to-rhel7-with-ipxe.patch [bz#997702]
- kvm-pc-Don-t-prematurely-explode-QEMUMachineInitArgs.patch [bz#994490]
- kvm-pc-Don-t-explode-QEMUMachineInitArgs-into-local-vari.patch [bz#994490]
- kvm-smbios-Normalize-smbios_entry_add-s-error-handling-t.patch [bz#994490]
- kvm-smbios-Convert-to-QemuOpts.patch [bz#994490]
- kvm-smbios-Improve-diagnostics-for-conflicting-entries.patch [bz#994490]
- kvm-smbios-Make-multiple-smbios-type-accumulate-sanely.patch [bz#994490]
- kvm-smbios-Factor-out-smbios_maybe_add_str.patch [bz#994490]
- kvm-hw-Pass-QEMUMachine-to-its-init-method.patch [bz#994490]
- kvm-smbios-Set-system-manufacturer-product-version-by-de.patch [bz#994490]
- kvm-smbios-Decouple-system-product-from-QEMUMachine.patch [bz#994490]
- kvm-rhel-SMBIOS-type-1-branding.patch [bz#994490]
- kvm-Add-disable-rhev-features-option-to-configure.patch []
- Resolves: bz#1001144
  (Disable or remove device usb-host-linux)
- Resolves: bz#1009993
  (RHEL7 guests do not issue fdatasyncs on virtio-blk)
- Resolves: bz#787463
  (disable ivshmem (was: [Hitachi 7.0 FEAT] Support ivshmem (Inter-VM Shared Memory)))
- Resolves: bz#907743
  (qemu-ga: empty reason string for OpenFileFailed error)
- Resolves: bz#928867
  (Virtual PMU support during live migration - qemu-kvm)
- Resolves: bz#994490
  (Set per-machine-type SMBIOS strings)
- Resolves: bz#997702
  (Migration from RHEL6.5 host to RHEL7.0 host is failed with virtio-net device)

* Tue Nov 05 2013 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-13.el7
- kvm-seabios-paravirt-allow-more-than-1TB-in-x86-guest.patch [bz#989677]
- kvm-scsi-prefer-UUID-to-VM-name-for-the-initiator-name.patch [bz#1006468]
- kvm-Fix-incorrect-rhel_rhev_conflicts-macro-usage.patch [bz#1017693]
- Resolves: bz#1006468
  (libiscsi initiator name should use vm UUID)
- Resolves: bz#1017693
  (incorrect use of rhel_rhev_conflicts)
- Resolves: bz#989677
  ([HP 7.0 FEAT]: Increase KVM guest supported memory to 4TiB)

* Mon Nov 04 2013 Michal Novotny <minovotn@redhat.com> - 1.5.3-12.el7
- kvm-vl-Clean-up-parsing-of-boot-option-argument.patch [bz#997817]
- kvm-qemu-option-check_params-is-now-unused-drop-it.patch [bz#997817]
- kvm-vl-Fix-boot-order-and-once-regressions-and-related-b.patch [bz#997817]
- kvm-vl-Rename-boot_devices-to-boot_order-for-consistency.patch [bz#997817]
- kvm-pc-Make-no-fd-bootchk-stick-across-boot-order-change.patch [bz#997817]
- kvm-doc-Drop-ref-to-Bochs-from-no-fd-bootchk-documentati.patch [bz#997817]
- kvm-libqtest-Plug-fd-and-memory-leaks-in-qtest_quit.patch [bz#997817]
- kvm-libqtest-New-qtest_end-to-go-with-qtest_start.patch [bz#997817]
- kvm-qtest-Don-t-reset-on-qtest-chardev-connect.patch [bz#997817]
- kvm-boot-order-test-New-covering-just-PC-for-now.patch [bz#997817]
- kvm-qemu-ga-execute-fsfreeze-freeze-in-reverse-order-of-.patch [bz#1019352]
- kvm-rbd-link-and-load-librbd-dynamically.patch [bz#989608]
- kvm-rbd-Only-look-for-qemu-specific-copy-of-librbd.so.1.patch [bz#989608]
- kvm-spec-Whitelist-rbd-block-driver.patch [bz#989608]
- Resolves: bz#1019352
  (qemu-guest-agent: "guest-fsfreeze-freeze" deadlocks if the guest have mounted disk images)
- Resolves: bz#989608
  ([7.0 FEAT] qemu runtime support for librbd backend (ceph))
- Resolves: bz#997817
  (-boot order and -boot once regressed since RHEL-6)

* Thu Oct 31 2013 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-11.el7
- kvm-chardev-fix-pty_chr_timer.patch [bz#994414]
- kvm-qemu-socket-zero-initialize-SocketAddress.patch [bz#922010]
- kvm-qemu-socket-drop-pointless-allocation.patch [bz#922010]
- kvm-qemu-socket-catch-monitor_get_fd-failures.patch [bz#922010]
- kvm-qemu-char-check-optional-fields-using-has_.patch [bz#922010]
- kvm-error-add-error_setg_file_open-helper.patch [bz#922010]
- kvm-qemu-char-use-more-specific-error_setg_-variants.patch [bz#922010]
- kvm-qemu-char-print-notification-to-stderr.patch [bz#922010]
- kvm-qemu-char-fix-documentation-for-telnet-wait-socket-f.patch [bz#922010]
- kvm-qemu-char-don-t-leak-opts-on-error.patch [bz#922010]
- kvm-qemu-char-use-ChardevBackendKind-in-CharDriver.patch [bz#922010]
- kvm-qemu-char-minor-mux-chardev-fixes.patch [bz#922010]
- kvm-qemu-char-add-chardev-mux-support.patch [bz#922010]
- kvm-qemu-char-report-udp-backend-errors.patch [bz#922010]
- kvm-qemu-socket-don-t-leak-opts-on-error.patch [bz#922010]
- kvm-chardev-handle-qmp_chardev_add-KIND_MUX-failure.patch [bz#922010]
- kvm-acpi-piix4-Enable-qemu-kvm-compatibility-mode.patch [bz#1019474]
- kvm-target-i386-support-loading-of-cpu-xsave-subsection.patch [bz#1004743]
- Resolves: bz#1004743
  (XSAVE migration format not compatible between RHEL6 and RHEL7)
- Resolves: bz#1019474
  (RHEL-7 can't load piix4_pm migration section from RHEL-6.5)
- Resolves: bz#922010
  (RFE: support hotplugging chardev & serial ports)
- Resolves: bz#994414
  (hot-unplug chardev with pty backend caused qemu Segmentation fault)

* Thu Oct 17 2013 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-10.el7
- kvm-xhci-fix-endpoint-interval-calculation.patch [bz#1001604]
- kvm-xhci-emulate-intr-endpoint-intervals-correctly.patch [bz#1001604]
- kvm-xhci-reset-port-when-disabling-slot.patch [bz#1001604]
- kvm-Revert-usb-hub-report-status-changes-only-once.patch [bz#1001604]
- kvm-target-i386-Set-model-6-on-qemu64-qemu32-CPU-models.patch [bz#1004290]
- kvm-pc-rhel6-doesn-t-have-APIC-on-pentium-CPU-models.patch [bz#918907]
- kvm-pc-RHEL-6-had-x2apic-set-on-Opteron_G-123.patch [bz#918907]
- kvm-pc-RHEL-6-don-t-have-RDTSCP.patch [bz#918907]
- kvm-scsi-Fix-scsi_bus_legacy_add_drive-scsi-generic-with.patch [bz#1009285]
- kvm-seccomp-fine-tuning-whitelist-by-adding-times.patch [bz#1004175]
- kvm-block-add-bdrv_write_zeroes.patch [bz#921465]
- kvm-block-raw-add-bdrv_co_write_zeroes.patch [bz#921465]
- kvm-rdma-export-qemu_fflush.patch [bz#921465]
- kvm-block-migration-efficiently-encode-zero-blocks.patch [bz#921465]
- kvm-Fix-real-mode-guest-migration.patch [bz#921465]
- kvm-Fix-real-mode-guest-segments-dpl-value-in-savevm.patch [bz#921465]
- kvm-migration-add-autoconvergence-documentation.patch [bz#921465]
- kvm-migration-send-total-time-in-QMP-at-completed-stage.patch [bz#921465]
- kvm-migration-don-t-use-uninitialized-variables.patch [bz#921465]
- kvm-pc-drop-external-DSDT-loading.patch [bz#921465]
- kvm-hda-codec-refactor-common-definitions-into-a-header-.patch [bz#954195]
- kvm-hda-codec-make-mixemu-selectable-at-runtime.patch [bz#954195]
- kvm-audio-remove-CONFIG_MIXEMU-configure-option.patch [bz#954195]
- kvm-pc_piix-disable-mixer-for-6.4.0-machine-types-and-be.patch [bz#954195]
- kvm-spec-mixemu-config-option-is-no-longer-supported-and.patch [bz#954195]
- Resolves: bz#1001604
  (usb hub doesn't work properly (win7 sees downstream port #1 only).)
- Resolves: bz#1004175
  ('-sandbox on'  option  cause  qemu-kvm process hang)
- Resolves: bz#1004290
  (Use model 6 for qemu64 and intel cpus)
- Resolves: bz#1009285
  (-device usb-storage,serial=... crashes with SCSI generic drive)
- Resolves: bz#918907
  (provide backwards-compatible RHEL specific machine types in QEMU - CPU features)
- Resolves: bz#921465
  (Migration can not finished even the "remaining ram" is already 0 kb)
- Resolves: bz#954195
  (RHEL machines <=6.4 should not use mixemu)

* Thu Oct 10 2013 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-9.el7
- kvm-qxl-fix-local-renderer.patch [bz#1005036]
- kvm-spec-include-userspace-iSCSI-initiator-in-block-driv.patch [bz#923843]
- kvm-linux-headers-update-to-kernel-3.10.0-26.el7.patch [bz#1008987]
- kvm-target-i386-add-feature-kvm_pv_unhalt.patch [bz#1008987]
- kvm-warn-if-num-cpus-is-greater-than-num-recommended.patch [bz#1010881]
- kvm-char-move-backends-io-watch-tag-to-CharDriverState.patch [bz#1007222]
- kvm-char-use-common-function-to-disable-callbacks-on-cha.patch [bz#1007222]
- kvm-char-remove-watch-callback-on-chardev-detach-from-fr.patch [bz#1007222]
- kvm-block-don-t-lose-data-from-last-incomplete-sector.patch [bz#1017049]
- kvm-vmdk-fix-cluster-size-check-for-flat-extents.patch [bz#1017049]
- kvm-qemu-iotests-add-monolithicFlat-creation-test-to-059.patch [bz#1017049]
- Resolves: bz#1005036
  (When using “-vga qxl” together with “-display vnc=:5” or “-display  sdl” qemu displays  pixel garbage)
- Resolves: bz#1007222
  (QEMU core dumped when do hot-unplug virtio serial port during transfer file between host to guest with virtio serial through TCP socket)
- Resolves: bz#1008987
  (pvticketlocks: add kvm feature kvm_pv_unhalt)
- Resolves: bz#1010881
  (backport vcpu soft limit warning)
- Resolves: bz#1017049
  (qemu-img refuses to open the vmdk format image its created)
- Resolves: bz#923843
  (include userspace iSCSI initiator in block driver whitelist)

* Wed Oct 09 2013 Miroslav Rezanina <mrezanin@redhat.com> - qemu-kvm-1.5.3-8.el7
- kvm-vmdk-Make-VMDK3Header-and-VmdkGrainMarker-QEMU_PACKE.patch [bz#995866]
- kvm-vmdk-use-unsigned-values-for-on-disk-header-fields.patch [bz#995866]
- kvm-qemu-iotests-add-poke_file-utility-function.patch [bz#995866]
- kvm-qemu-iotests-add-empty-test-case-for-vmdk.patch [bz#995866]
- kvm-vmdk-check-granularity-field-in-opening.patch [bz#995866]
- kvm-vmdk-check-l2-table-size-when-opening.patch [bz#995866]
- kvm-vmdk-check-l1-size-before-opening-image.patch [bz#995866]
- kvm-vmdk-use-heap-allocation-for-whole_grain.patch [bz#995866]
- kvm-vmdk-rename-num_gtes_per_gte-to-num_gtes_per_gt.patch [bz#995866]
- kvm-vmdk-Move-l1_size-check-into-vmdk_add_extent.patch [bz#995866]
- kvm-vmdk-fix-L1-and-L2-table-size-in-vmdk3-open.patch [bz#995866]
- kvm-vmdk-support-vmfsSparse-files.patch [bz#995866]
- kvm-vmdk-support-vmfs-files.patch [bz#995866]
- Resolves: bz#995866
  (fix vmdk support to ESX images)

* Thu Sep 26 2013 Miroslav Rezanina <mrezanin@redhat.com> - qemu-kvm-1.5.3-7.el7
- kvm-spice-fix-display-initialization.patch [bz#974887]
- kvm-Remove-i82550-network-card-emulation.patch [bz#921983]
- kvm-Remove-usb-wacom-tablet.patch [bz#903914]
- kvm-Disable-usb-uas.patch [bz#903914]
- kvm-Disable-vhost-scsi.patch [bz#994642]
- kvm-Remove-no-hpet-option.patch [bz#947441]
- kvm-Disable-isa-parallel.patch [bz#1002286]
- kvm-xhci-implement-warm-port-reset.patch [bz#949514]
- kvm-usb-add-serial-bus-property.patch [bz#953304]
- kvm-rhel6-compat-usb-serial-numbers.patch [bz#953304]
- kvm-vmdk-fix-comment-for-vmdk_co_write_zeroes.patch [bz#995866]
- kvm-gluster-Add-image-resize-support.patch [bz#1007226]
- kvm-block-Introduce-bs-zero_beyond_eof.patch [bz#1007226]
- kvm-block-Produce-zeros-when-protocols-reading-beyond-en.patch [bz#1007226]
- kvm-gluster-Abort-on-AIO-completion-failure.patch [bz#1007226]
- kvm-Preparation-for-usb-bt-dongle-conditional-build.patch [bz#1001131]
- kvm-Remove-dev-bluetooth.c-dependency-from-vl.c.patch [bz#1001131]
- kvm-exec-Fix-Xen-RAM-allocation-with-unusual-options.patch [bz#1009328]
- kvm-exec-Clean-up-fall-back-when-mem-path-allocation-fai.patch [bz#1009328]
- kvm-exec-Reduce-ifdeffery-around-mem-path.patch [bz#1009328]
- kvm-exec-Simplify-the-guest-physical-memory-allocation-h.patch [bz#1009328]
- kvm-exec-Drop-incorrect-dead-S390-code-in-qemu_ram_remap.patch [bz#1009328]
- kvm-exec-Clean-up-unnecessary-S390-ifdeffery.patch [bz#1009328]
- kvm-exec-Don-t-abort-when-we-can-t-allocate-guest-memory.patch [bz#1009328]
- kvm-pc_sysfw-Fix-ISA-BIOS-init-for-ridiculously-big-flas.patch [bz#1009328]
- kvm-virtio-scsi-Make-type-virtio-scsi-common-abstract.patch [bz#903918]
- kvm-qga-move-logfiles-to-new-directory-for-easier-SELinu.patch [bz#1009491]
- kvm-target-i386-add-cpu64-rhel6-CPU-model.patch [bz#918907]
- kvm-fix-steal-time-MSR-vmsd-callback-to-proper-opaque-ty.patch [bz#903889]
- Resolves: bz#1001131
  (Disable or remove device usb-bt-dongle)
- Resolves: bz#1002286
  (Disable or remove device isa-parallel)
- Resolves: bz#1007226
  (Introduce bs->zero_beyond_eof)
- Resolves: bz#1009328
  ([RFE] Nicer error report when qemu-kvm can't allocate guest RAM)
- Resolves: bz#1009491
  (move qga logfiles to new /var/log/qemu-ga/ directory [RHEL-7])
- Resolves: bz#903889
  (The value of steal time in "top" command always is "0.0% st" after guest migration)
- Resolves: bz#903914
  (Disable or remove usb related devices that we will not support)
- Resolves: bz#903918
  (Disable or remove emulated SCSI devices we will not support)
- Resolves: bz#918907
  (provide backwards-compatible RHEL specific machine types in QEMU - CPU features)
- Resolves: bz#921983
  (Disable or remove emulated network devices that we will not support)
- Resolves: bz#947441
  (HPET device must be disabled)
- Resolves: bz#949514
  (fail to passthrough the USB3.0 stick to windows guest with xHCI controller under pc-i440fx-1.4)
- Resolves: bz#953304
  (Serial number of some USB devices must be fixed for older RHEL machine types)
- Resolves: bz#974887
  (the screen of guest fail to display correctly when use spice + qxl driver)
- Resolves: bz#994642
  (should disable vhost-scsi)
- Resolves: bz#995866
  (fix vmdk support to ESX images)

* Mon Sep 23 2013 Paolo Bonzini <pbonzini@redhat.com> - qemu-kvm-1.5.3-6.el7
- re-enable spice
- Related: #979953

* Mon Sep 23 2013 Paolo Bonzini <pbonzini@redhat.com> - qemu-kvm-1.5.3-5.el7
- temporarily disable spice until libiscsi rebase is complete
- Related: #979953

* Thu Sep 19 2013 Michal Novotny <minovotn@redhat.com> - qemu-kvm-1.5.3-4.el7
- kvm-block-package-preparation-code-in-qmp_transaction.patch [bz#1005818]
- kvm-block-move-input-parsing-code-in-qmp_transaction.patch [bz#1005818]
- kvm-block-package-committing-code-in-qmp_transaction.patch [bz#1005818]
- kvm-block-package-rollback-code-in-qmp_transaction.patch [bz#1005818]
- kvm-block-make-all-steps-in-qmp_transaction-as-callback.patch [bz#1005818]
- kvm-blockdev-drop-redundant-proto_drv-check.patch [bz#1005818]
- kvm-block-Don-t-parse-protocol-from-file.filename.patch [bz#1005818]
- kvm-Revert-block-Disable-driver-specific-options-for-1.5.patch [bz#1005818]
- kvm-qcow2-Add-refcount-update-reason-to-all-callers.patch [bz#1005818]
- kvm-qcow2-Options-to-enable-discard-for-freed-clusters.patch [bz#1005818]
- kvm-qcow2-Batch-discards.patch [bz#1005818]
- kvm-block-Always-enable-discard-on-the-protocol-level.patch [bz#1005818]
- kvm-qapi.py-Avoid-code-duplication.patch [bz#1005818]
- kvm-qapi.py-Allow-top-level-type-reference-for-command-d.patch [bz#1005818]
- kvm-qapi-schema-Use-BlockdevSnapshot-type-for-blockdev-s.patch [bz#1005818]
- kvm-qapi-types.py-Implement-base-for-unions.patch [bz#1005818]
- kvm-qapi-visit.py-Split-off-generate_visit_struct_fields.patch [bz#1005818]
- kvm-qapi-visit.py-Implement-base-for-unions.patch [bz#1005818]
- kvm-docs-Document-QAPI-union-types.patch [bz#1005818]
- kvm-qapi-Add-visitor-for-implicit-structs.patch [bz#1005818]
- kvm-qapi-Flat-unions-with-arbitrary-discriminator.patch [bz#1005818]
- kvm-qapi-Add-consume-argument-to-qmp_input_get_object.patch [bz#1005818]
- kvm-qapi.py-Maintain-a-list-of-union-types.patch [bz#1005818]
- kvm-qapi-qapi-types.py-native-list-support.patch [bz#1005818]
- kvm-qapi-Anonymous-unions.patch [bz#1005818]
- kvm-block-Allow-driver-option-on-the-top-level.patch [bz#1005818]
- kvm-QemuOpts-Add-qemu_opt_unset.patch [bz#1005818]
- kvm-blockdev-Rename-I-O-throttling-options-for-QMP.patch [bz#1005818]
- kvm-qemu-iotests-Update-051-reference-output.patch [bz#1005818]
- kvm-blockdev-Rename-readonly-option-to-read-only.patch [bz#1005818]
- kvm-blockdev-Split-up-cache-option.patch [bz#1005818]
- kvm-qcow2-Use-dashes-instead-of-underscores-in-options.patch [bz#1005818]
- kvm-qemu-iotests-filter-QEMU-version-in-monitor-banner.patch [bz#1006959]
- kvm-tests-set-MALLOC_PERTURB_-to-expose-memory-bugs.patch [bz#1006959]
- kvm-qemu-iotests-Whitespace-cleanup.patch [bz#1006959]
- kvm-qemu-iotests-Fixed-test-case-026.patch [bz#1006959]
- kvm-qemu-iotests-Fix-test-038.patch [bz#1006959]
- kvm-qemu-iotests-Remove-lsi53c895a-tests-from-051.patch [bz#1006959]
- Resolves: bz#1005818
  (qcow2: Backport discard command line options)
- Resolves: bz#1006959
  (qemu-iotests false positives)

* Thu Aug 29 2013 Miroslav Rezanina <mrezanin@redhat.com> - qemu-kvm-1.5.3-3.el7
- Fix rhel/rhev split

* Thu Aug 29 2013 Miroslav Rezanina <mrezanin@redhat.com> - qemu-kvm-1.5.3-2.el7
- kvm-osdep-add-qemu_get_local_state_pathname.patch [bz#964304]
- kvm-qga-determine-default-state-dir-and-pidfile-dynamica.patch [bz#964304]
- kvm-configure-don-t-save-any-fixed-local_statedir-for-wi.patch [bz#964304]
- kvm-qga-create-state-directory-on-win32.patch [bz#964304]
- kvm-qga-save-state-directory-in-ga_install_service-RHEL-.patch [bz#964304]
- kvm-Makefile-create-.-var-run-when-installing-the-POSIX-.patch [bz#964304]
- kvm-qemu-option-Fix-qemu_opts_find-for-null-id-arguments.patch [bz#980782]
- kvm-qemu-option-Fix-qemu_opts_set_defaults-for-corner-ca.patch [bz#980782]
- kvm-vl-New-qemu_get_machine_opts.patch [bz#980782]
- kvm-Fix-machine-options-accel-kernel_irqchip-kvm_shadow_.patch [bz#980782]
- kvm-microblaze-Fix-latent-bug-with-default-DTB-lookup.patch [bz#980782]
- kvm-Simplify-machine-option-queries-with-qemu_get_machin.patch [bz#980782]
- kvm-pci-add-VMSTATE_MSIX.patch [bz#838170]
- kvm-xhci-add-XHCISlot-addressed.patch [bz#838170]
- kvm-xhci-add-xhci_alloc_epctx.patch [bz#838170]
- kvm-xhci-add-xhci_init_epctx.patch [bz#838170]
- kvm-xhci-add-live-migration-support.patch [bz#838170]
- kvm-pc-set-level-xlevel-correctly-on-486-qemu32-CPU-mode.patch [bz#918907]
- kvm-pc-Remove-incorrect-rhel6.x-compat-model-value-for-C.patch [bz#918907]
- kvm-pc-rhel6.x-has-x2apic-present-on-Conroe-Penryn-Nehal.patch [bz#918907]
- kvm-pc-set-compat-CPUID-0x80000001-.EDX-bits-on-Westmere.patch [bz#918907]
- kvm-pc-Remove-PCLMULQDQ-from-Westmere-on-rhel6.x-machine.patch [bz#918907]
- kvm-pc-SandyBridge-rhel6.x-compat-fixes.patch [bz#918907]
- kvm-pc-Haswell-doesn-t-have-rdtscp-on-rhel6.x.patch [bz#918907]
- kvm-i386-fix-LAPIC-TSC-deadline-timer-save-restore.patch [bz#972433]
- kvm-all.c-max_cpus-should-not-exceed-KVM-vcpu-limit.patch [bz#996258]
- kvm-add-timestamp-to-error_report.patch [bz#906937]
- kvm-Convert-stderr-message-calling-error_get_pretty-to-e.patch [bz#906937]
- Resolves: bz#838170
  (Add live migration support for USB [xhci, usb-uas])
- Resolves: bz#906937
  ([Hitachi 7.0 FEAT][QEMU]Add a time stamp to error message (*))
- Resolves: bz#918907
  (provide backwards-compatible RHEL specific machine types in QEMU - CPU features)
- Resolves: bz#964304
  (Windows guest agent service failed to be started)
- Resolves: bz#972433
  ("INFO: rcu_sched detected stalls" after RHEL7 kvm vm migrated)
- Resolves: bz#980782
  (kernel_irqchip defaults to off instead of on without -machine)
- Resolves: bz#996258
  (boot guest with maxcpu=255 successfully but actually max number of vcpu is 160)

* Wed Aug 28 2013 Miroslav Rezanina <mrezanin@redhat.com> - 10:1.5.3-1
- Rebase to qemu 1.5.3

* Tue Aug 20 2013 Miroslav Rezanina <mrezanin@redhat.com> - 10:1.5.2-4
- qemu: guest agent creates files with insecure permissions in deamon mode [rhel-7.0] (rhbz 974444)
- update qemu-ga config & init script in RHEL7 wrt. fsfreeze hook (rhbz 969942)
- RHEL7 does not have equivalent functionality for __com.redhat_qxl_screendump (rhbz 903910)
- SEP flag behavior for CPU models of RHEL6 machine types should be compatible (rhbz 960216)
- crash command can not read the dump-guest-memory file when paging=false [RHEL-7] (rhbz 981582)
- RHEL 7 qemu-kvm fails to build on F19 host due to libusb deprecated API (rhbz 996469)
- Live migration support in virtio-blk-data-plane (rhbz 995030)
- qemu-img resize can execute successfully even input invalid syntax (rhbz 992935)

* Fri Aug 09 2013 Miroslav Rezanina <mrezanin@redhat.com> - 10:1.5.2-3
- query mem info from monitor would cause qemu-kvm hang [RHEL-7] (rhbz #970047)
- Throttle-down guest to help with live migration convergence (backport to RHEL7.0) (rhbz #985958)
- disable (for now) EFI-enabled roms (rhbz #962563)
- qemu-kvm "vPMU passthrough" mode breaks migration, shouldn't be enabled by default (rhbz #853101)
- Remove pending watches after virtserialport unplug (rhbz #992900)
- Containment of error when an SR-IOV device encounters an error... (rhbz #984604)

* Wed Jul 31 2013 Miroslav Rezanina <mrezanin@redhat.com> - 10:1.5.2-2
- SPEC file prepared for RHEL/RHEV split (rhbz #987165)
- RHEL guest( sata disk ) can not boot up (rhbz #981723)
- Kill the "use flash device for BIOS unless KVM" misfeature (rhbz #963280)
- Provide RHEL-6 machine types (rhbz #983991)
- Change s3/s4 default to "disable". (rhbz #980840)  
- Support Virtual Memory Disk Format in qemu (rhbz #836675)
- Glusterfs backend for QEMU (rhbz #805139)

* Tue Jul 02 2013 Miroslav Rezanina <mrezanin@redhat.com> - 10:1.5.2-1
- Rebase to 1.5.2

* Tue Jul 02 2013 Miroslav Rezanina <mrezanin@redhat.com> - 10:1.5.1-2
- Fix package package version info (bz #952996)
- pc: Replace upstream machine types by RHEL-7 types (bz #977864)
- target-i386: Update model values on Conroe/Penryn/Nehalem CPU model (bz #861210)
- target-i386: Set level=4 on Conroe/Penryn/Nehalem (bz #861210)

* Fri Jun 28 2013 Miroslav Rezanina <mrezanin@redhat.com> - 10:1.5.1-1
- Rebase to 1.5.1
- Change epoch to 10 to obsolete RHEL-6 qemu-kvm-rhev package (bz #818626)

* Fri May 24 2013 Miroslav Rezanina <mrezanin@redhat.com> - 3:1.5.0-2
- Enable werror (bz #948290)
- Enable nbd driver (bz #875871)
- Fix udev rules file location (bz #958860)
- Remove +x bit from systemd unit files (bz #965000)
- Drop unneeded kvm.modules on x86 (bz #963642)
- Fix build flags
- Enable libusb

* Thu May 23 2013 Miroslav Rezanina <mrezanin@redhat.com> - 3:1.5.0-1
- Rebase to 1.5.0

* Tue Apr 23 2013 Miroslav Rezanina <mrezanin@redhat.com> - 3:1.4.0-4
- Enable build of libcacard subpackage for non-x86_64 archs (bz #873174)
- Enable build of qemu-img subpackage for non-x86_64 archs (bz #873174)
- Enable build of qemu-guest-agent subpackage for non-x86_64 archs (bz #873174)

* Tue Apr 23 2013 Miroslav Rezanina <mrezanin@redhat.com> - 3:1.4.0-3
- Enable/disable features supported by rhel7
- Use qemu-kvm instead of qemu in filenames and pathes

* Fri Apr 19 2013 Daniel Mach <dmach@redhat.com> - 3:1.4.0-2.1
- Rebuild for cyrus-sasl

* Fri Apr 05 2013 Miroslav Rezanina <mrezanin@redhat.com> - 3:1.4.0-2
- Synchronization with Fedora 19 package version 2:1.4.0-8

* Wed Apr 03 2013 Daniel Mach <dmach@redhat.com> - 3:1.4.0-1.1
- Rebuild for libseccomp

* Thu Mar 07 2013 Miroslav Rezanina <mrezanin@redhat.com> - 3:1.4.0-1
- Rebase to 1.4.0

* Mon Feb 25 2013 Michal Novotny <minovotn@redhat.com> - 3:1.3.0-8
- Missing package qemu-system-x86 in hardware certification kvm testing (bz#912433)
- Resolves: bz#912433
  (Missing package qemu-system-x86 in hardware certification kvm testing)

* Fri Feb 22 2013 Alon Levy <alevy@redhat.com> - 3:1.3.0-6
- Bump epoch back to 3 since there has already been a 3 package release:
  3:1.2.0-20.el7 https://brewweb.devel.redhat.com/buildinfo?buildID=244866
- Mark explicit libcacard dependency on new enough qemu-img to avoid conflict
  since /usr/bin/vscclient was moved from qemu-img to libcacard subpackage.

* Wed Feb 13 2013 Michal Novotny <minovotn@redhat.com> - 2:1.3.0-5
- Fix patch contents for usb-redir (bz#895491)
- Resolves: bz#895491
  (PATCH: 0110-usb-redir-Add-flow-control-support.patch has been mangled on rebase !!)

* Wed Feb 06 2013 Alon Levy <alevy@redhat.com> - 2:1.3.0-4
- Add patch from f19 package for libcacard missing error_set symbol.
- Resolves: bz#891552

* Mon Jan 07 2013 Michal Novotny <minovotn@redhat.com> - 2:1.3.0-3
- Remove dependency on bogus qemu-kvm-kvm package [bz#870343]
- Resolves: bz#870343
  (qemu-kvm-1.2.0-16.el7 cant be installed)

* Tue Dec 18 2012 Michal Novotny <minovotn@redhat.com> - 2:1.3.0-2
- Rename qemu to qemu-kvm
- Move qemu-kvm to libexecdir

* Fri Dec 07 2012 Cole Robinson <crobinso@redhat.com> - 2:1.3.0-1
- Switch base tarball from qemu-kvm to qemu
- qemu 1.3 release
- Option to use linux VFIO driver to assign PCI devices
- Many USB3 improvements
- New paravirtualized hardware random number generator device.
- Support for Glusterfs volumes with "gluster://" -drive URI
- Block job commands for live block commit and storage migration

* Wed Nov 28 2012 Alon Levy <alevy@redhat.com> - 2:1.2.0-25
* Merge libcacard into qemu, since they both use the same sources now.

* Thu Nov 22 2012 Paolo Bonzini <pbonzini@redhat.com> - 2:1.2.0-24
- Move vscclient to qemu-common, qemu-nbd to qemu-img

* Tue Nov 20 2012 Alon Levy <alevy@redhat.com> - 2:1.2.0-23
- Rewrite fix for bz #725965 based on fix for bz #867366
- Resolve bz #867366

* Fri Nov 16 2012 Paolo Bonzini <pbonzini@redhat.com> - 2:1.2.0-23
- Backport --with separate_kvm support from EPEL branch

* Fri Nov 16 2012 Paolo Bonzini <pbonzini@redhat.com> - 2:1.2.0-22
- Fix previous commit

* Fri Nov 16 2012 Paolo Bonzini <pbonzini@redhat.com> - 2:1.2.0-21
- Backport commit 38f419f (configure: Fix CONFIG_QEMU_HELPERDIR generation,
  2012-10-17)

* Thu Nov 15 2012 Paolo Bonzini <pbonzini@redhat.com> - 2:1.2.0-20
- Install qemu-bridge-helper as suid root
- Distribute a sample /etc/qemu/bridge.conf file

* Thu Nov  1 2012 Hans de Goede <hdegoede@redhat.com> - 2:1.2.0-19
- Sync spice patches with upstream, minor bugfixes and set the qxl pci
  device revision to 4 by default, so that guests know they can use
  the new features

* Tue Oct 30 2012 Cole Robinson <crobinso@redhat.com> - 2:1.2.0-18
- Fix loading arm initrd if kernel is very large (bz #862766)
- Don't use reserved word 'function' in systemtap files (bz #870972)
- Drop assertion that was triggering when pausing guests w/ qxl (bz
  #870972)

* Sun Oct 28 2012 Cole Robinson <crobinso@redhat.com> - 2:1.2.0-17
- Pull patches queued for qemu 1.2.1

* Fri Oct 19 2012 Paolo Bonzini <pbonzini@redhat.com> - 2:1.2.0-16
- add s390x KVM support
- distribute pre-built firmware or device trees for Alpha, Microblaze, S390
- add missing system targets
- add missing linux-user targets
- fix previous commit

* Thu Oct 18 2012 Dan Horák <dan[at]danny.cz> - 2:1.2.0-15
- fix build on non-kvm arches like s390(x)

* Wed Oct 17 2012 Paolo Bonzini <pbonzini@redhat.com> - 2:1.2.0-14
- Change SLOF Requires for the new version number

* Thu Oct 11 2012 Paolo Bonzini <pbonzini@redhat.com> - 2:1.2.0-13
- Add ppc support to kvm.modules (original patch by David Gibson)
- Replace x86only build with kvmonly build: add separate defines and
  conditionals for all packages, so that they can be chosen and
  renamed in kvmonly builds and so that qemu has the appropriate requires
- Automatically pick libfdt dependancy
- Add knob to disable spice+seccomp

* Fri Sep 28 2012 Paolo Bonzini <pbonzini@redhat.com> - 2:1.2.0-12
- Call udevadm on post, fixing bug 860658

* Fri Sep 28 2012 Hans de Goede <hdegoede@redhat.com> - 2:1.2.0-11
- Rebuild against latest spice-server and spice-protocol
- Fix non-seamless migration failing with vms with usb-redir devices,
  to allow boxes to load such vms from disk

* Tue Sep 25 2012 Hans de Goede <hdegoede@redhat.com> - 2:1.2.0-10
- Sync Spice patchsets with upstream (rhbz#860238)
- Fix building with usbredir >= 0.5.2

* Thu Sep 20 2012 Hans de Goede <hdegoede@redhat.com> - 2:1.2.0-9
- Sync USB and Spice patchsets with upstream

* Sun Sep 16 2012 Richard W.M. Jones <rjones@redhat.com> - 2:1.2.0-8
- Use 'global' instead of 'define', and underscore in definition name,
  n-v-r, and 'dist' tag of SLOF, all to fix RHBZ#855252.

* Fri Sep 14 2012 Paolo Bonzini <pbonzini@redhat.com> - 2:1.2.0-4
- add versioned dependency from qemu-system-ppc to SLOF (BZ#855252)

* Wed Sep 12 2012 Richard W.M. Jones <rjones@redhat.com> - 2:1.2.0-3
- Fix RHBZ#853408 which causes libguestfs failure.

* Sat Sep  8 2012 Hans de Goede <hdegoede@redhat.com> - 2:1.2.0-2
- Fix crash on (seamless) migration
- Sync usbredir live migration patches with upstream

* Fri Sep  7 2012 Hans de Goede <hdegoede@redhat.com> - 2:1.2.0-1
- New upstream release 1.2.0 final
- Add support for Spice seamless migration
- Add support for Spice dynamic monitors
- Add support for usb-redir live migration

* Tue Sep 04 2012 Adam Jackson <ajax@redhat.com> 1.2.0-0.5.rc1
- Flip Requires: ceph >= foo to Conflicts: ceph < foo, so we pull in only the
  libraries which we need and not the rest of ceph which we don't.

* Tue Aug 28 2012 Cole Robinson <crobinso@redhat.com> 1.2.0-0.4.rc1
- Update to 1.2.0-rc1

* Mon Aug 20 2012 Richard W.M. Jones <rjones@redhat.com> - 1.2-0.3.20120806git3e430569
- Backport Bonzini's vhost-net fix (RHBZ#848400).

* Tue Aug 14 2012 Cole Robinson <crobinso@redhat.com> - 1.2-0.2.20120806git3e430569
- Bump release number, previous build forgot but the dist bump helped us out

* Tue Aug 14 2012 Cole Robinson <crobinso@redhat.com> - 1.2-0.1.20120806git3e430569
- Revive qemu-system-{ppc*, sparc*} (bz 844502)
- Enable KVM support for all targets (bz 844503)

* Mon Aug 06 2012 Cole Robinson <crobinso@redhat.com> - 1.2-0.1.20120806git3e430569.fc18
- Update to git snapshot

* Sun Jul 29 2012 Cole Robinson <crobinso@redhat.com> - 1.1.1-1
- Upstream stable release 1.1.1
- Fix systemtap tapsets (bz 831763)
- Fix VNC audio tunnelling (bz 840653)
- Don't renable ksm on update (bz 815156)
- Bump usbredir dep (bz 812097)
- Fix RPM install error on non-virt machines (bz 660629)
- Obsolete openbios to fix upgrade dependency issues (bz 694802)

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2:1.1.0-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Tue Jul 10 2012 Richard W.M. Jones <rjones@redhat.com> - 2:1.1.0-8
- Re-diff previous patch so that it applies and actually apply it

* Tue Jul 10 2012 Richard W.M. Jones <rjones@redhat.com> - 2:1.1.0-7
- Add patch to fix default machine options.  This fixes libvirt
  detection of qemu.
- Back out patch 1 which conflicts.

* Fri Jul  6 2012 Hans de Goede <hdegoede@redhat.com> - 2:1.1.0-5
- Fix qemu crashing (on an assert) whenever USB-2.0 isoc transfers are used

* Thu Jul  5 2012 Richard W.M. Jones <rjones@redhat.com> - 2:1.1.0-4
- Disable tests since they hang intermittently.
- Add kvmvapic.bin (replaces vapic.bin).
- Add cpus-x86_64.conf.  qemu now creates /etc/qemu/target-x86_64.conf
  as an empty file.
- Add qemu-icon.bmp.
- Add qemu-bridge-helper.
- Build and include virtfs-proxy-helper + man page (thanks Hans de Goede).

* Wed Jul  4 2012 Hans de Goede <hdegoede@redhat.com> - 2:1.1.0-1
- New upstream release 1.1.0
- Drop about a 100 spice + USB patches, which are all upstream

* Mon Apr 23 2012 Paolo Bonzini <pbonzini@redhat.com> - 2:1.0-17
- Fix install failure due to set -e (rhbz #815272)

* Mon Apr 23 2012 Paolo Bonzini <pbonzini@redhat.com> - 2:1.0-16
- Fix kvm.modules to exit successfully on non-KVM capable systems (rhbz #814932)

* Thu Apr 19 2012 Hans de Goede <hdegoede@redhat.com> - 2:1.0-15
- Add a couple of backported QXL/Spice bugfixes
- Add spice volume control patches

* Fri Apr 6 2012 Paolo Bonzini <pbonzini@redhat.com> - 2:1.0-12
- Add back PPC and SPARC user emulators
- Update binfmt rules from upstream

* Mon Apr  2 2012 Hans de Goede <hdegoede@redhat.com> - 2:1.0-11
- Some more USB bugfixes from upstream

* Thu Mar 29 2012 Eduardo Habkost <ehabkost@redhat.com> - 2:1.0-12
- Fix ExclusiveArch mistake that disabled all non-x86_64 builds on Fedora

* Wed Mar 28 2012 Eduardo Habkost <ehabkost@redhat.com> - 2:1.0-11
- Use --with variables for build-time settings

* Wed Mar 28 2012 Daniel P. Berrange <berrange@redhat.com> - 2:1.0-10
- Switch to use iPXE for netboot ROMs

* Thu Mar 22 2012 Daniel P. Berrange <berrange@redhat.com> - 2:1.0-9
- Remove O_NOATIME for 9p filesystems

* Mon Mar 19 2012 Daniel P. Berrange <berrange@redhat.com> - 2:1.0-8
- Move udev rules to /lib/udev/rules.d (rhbz #748207)

* Fri Mar  9 2012 Hans de Goede <hdegoede@redhat.com> - 2:1.0-7
- Add a whole bunch of USB bugfixes from upstream

* Mon Feb 13 2012 Daniel P. Berrange <berrange@redhat.com> - 2:1.0-6
- Add many more missing BRs for misc QEMU features
- Enable running of test suite during build

* Tue Feb 07 2012 Justin M. Forbes <jforbes@redhat.com> - 2:1.0-5
- Add support for virtio-scsi

* Sun Feb  5 2012 Richard W.M. Jones <rjones@redhat.com> - 2:1.0-4
- Require updated ceph for latest librbd with rbd_flush symbol.

* Tue Jan 24 2012 Justin M. Forbes <jforbes@redhat.com> - 2:1.0-3
- Add support for vPMU
- e1000: bounds packet size against buffer size CVE-2012-0029

* Fri Jan 13 2012 Justin M. Forbes <jforbes@redhat.com> - 2:1.0-2
- Add patches for USB redirect bits
- Remove palcode-clipper, we don't build it

* Wed Jan 11 2012 Justin M. Forbes <jforbes@redhat.com> - 2:1.0-1
- Add patches from 1.0.1 queue

* Fri Dec 16 2011 Justin M. Forbes <jforbes@redhat.com> - 2:1.0-1
- Update to qemu 1.0

* Tue Nov 15 2011 Justin M. Forbes <jforbes@redhat.com> - 2:0.15.1-3
- Enable spice for i686 users as well

* Thu Nov 03 2011 Justin M. Forbes <jforbes@redhat.com> - 2:0.15.1-2
- Fix POSTIN scriplet failure (#748281)

* Fri Oct 21 2011 Justin M. Forbes <jforbes@redhat.com> - 2:0.15.1-1
- Require seabios-bin >= 0.6.0-2 (#741992)
- Replace init scripts with systemd units (#741920)
- Update to 0.15.1 stable upstream
  
* Fri Oct 21 2011 Paul Moore <pmoore@redhat.com>
- Enable full relro and PIE (rhbz #738812)

* Wed Oct 12 2011 Daniel P. Berrange <berrange@redhat.com> - 2:0.15.0-6
- Add BR on ceph-devel to enable RBD block device

* Wed Oct  5 2011 Daniel P. Berrange <berrange@redhat.com> - 2:0.15.0-5
- Create a qemu-guest-agent sub-RPM for guest installation

* Tue Sep 13 2011 Daniel P. Berrange <berrange@redhat.com> - 2:0.15.0-4
- Enable DTrace tracing backend for SystemTAP (rhbz #737763)
- Enable build with curl (rhbz #737006)

* Thu Aug 18 2011 Hans de Goede <hdegoede@redhat.com> - 2:0.15.0-3
- Add missing BuildRequires: usbredir-devel, so that the usbredir code
  actually gets build

* Thu Aug 18 2011 Richard W.M. Jones <rjones@redhat.com> - 2:0.15.0-2
- Add upstream qemu patch 'Allow to leave type on default in -machine'
  (2645c6dcaf6ea2a51a3b6dfa407dd203004e4d11).

* Sun Aug 14 2011 Justin M. Forbes <jforbes@redhat.com> - 2:0.15.0-1
- Update to 0.15.0 stable release.

* Thu Aug 04 2011 Justin M. Forbes <jforbes@redhat.com> - 2:0.15.0-0.3.201108040af4922
- Update to 0.15.0-rc1 as we prepare for 0.15.0 release

* Thu Aug  4 2011 Daniel P. Berrange <berrange@redhat.com> - 2:0.15.0-0.3.2011072859fadcc
- Fix default accelerator for non-KVM builds (rhbz #724814)

* Thu Jul 28 2011 Justin M. Forbes <jforbes@redhat.com> - 2:0.15.0-0.1.2011072859fadcc
- Update to 0.15.0-rc0 as we prepare for 0.15.0 release

* Tue Jul 19 2011 Hans de Goede <hdegoede@redhat.com> - 2:0.15.0-0.2.20110718525e3df
- Add support usb redirection over the network, see:
  http://fedoraproject.org/wiki/Features/UsbNetworkRedirection
- Restore chardev flow control patches

* Mon Jul 18 2011 Justin M. Forbes <jforbes@redhat.com> - 2:0.15.0-0.1.20110718525e3df
- Update to git snapshot as we prepare for 0.15.0 release

* Wed Jun 22 2011 Richard W.M. Jones <rjones@redhat.com> - 2:0.14.0-9
- Add BR libattr-devel.  This caused the -fstype option to be disabled.
  https://www.redhat.com/archives/libvir-list/2011-June/thread.html#01017

* Mon May  2 2011 Hans de Goede <hdegoede@redhat.com> - 2:0.14.0-8
- Fix a bug in the spice flow control patches which breaks the tcp chardev

* Tue Mar 29 2011 Justin M. Forbes <jforbes@redhat.com> - 2:0.14.0-7
- Disable qemu-ppc and qemu-sparc packages (#679179)

* Mon Mar 28 2011 Justin M. Forbes <jforbes@redhat.com> - 2:0.14.0-6
- Spice fixes for flow control.

* Tue Mar 22 2011 Dan Horák <dan[at]danny.cz> - 2:0.14.0-5
- be more careful when removing the -g flag on s390

* Fri Mar 18 2011 Justin M. Forbes <jforbes@redhat.com> - 2:0.14.0-4
- Fix thinko on adding the most recent patches.

* Wed Mar 16 2011 Justin M. Forbes <jforbes@redhat.com> - 2:0.14.0-3
- Fix migration issue with vhost
- Fix qxl locking issues for spice

* Wed Mar 02 2011 Justin M. Forbes <jforbes@redhat.com> - 2:0.14.0-2
- Re-enable sparc and cris builds

* Thu Feb 24 2011 Justin M. Forbes <jforbes@redhat.com> - 2:0.14.0-1
- Update to 0.14.0 release

* Fri Feb 11 2011 Justin M. Forbes <jforbes@redhat.com> - 2:0.14.0-0.1.20110210git7aa8c46
- Update git snapshot
- Temporarily disable qemu-cris and qemu-sparc due to build errors (to be resolved shorly)

* Tue Feb 08 2011 Justin M. Forbes <jforbes@redhat.com> - 2:0.14.0-0.1.20110208git3593e6b
- Update to 0.14.0 rc git snapshot
- Add virtio-net to modules

* Wed Nov  3 2010 Daniel P. Berrange <berrange@redhat.com> - 2:0.13.0-2
- Revert previous change
- Make qemu-common own the /etc/qemu directory
- Add /etc/qemu/target-x86_64.conf to qemu-system-x86 regardless
  of host architecture.

* Wed Nov 03 2010 Dan Horák <dan[at]danny.cz> - 2:0.13.0-2
- Remove kvm config file on non-x86 arches (part of #639471)
- Own the /etc/qemu directory

* Mon Oct 18 2010 Justin M. Forbes <jforbes@redhat.com> - 2:0.13.0-1
- Update to 0.13.0 upstream release
- Fixes for vhost
- Fix mouse in certain guests (#636887)
- Fix issues with WinXP guest install (#579348)
- Resolve build issues with S390 (#639471)
- Fix Windows XP on Raw Devices (#631591)

* Tue Oct 05 2010 jkeating - 2:0.13.0-0.7.rc1.1
- Rebuilt for gcc bug 634757

* Tue Sep 21 2010 Justin M. Forbes <jforbes@redhat.com> - 2:0.13.0-0.7.rc1
- Flip qxl pci id from unstable to stable (#634535)
- KSM Fixes from upstream (#558281)

* Tue Sep 14 2010 Justin M. Forbes <jforbes@redhat.com> - 2:0.13.0-0.6.rc1
- Move away from git snapshots as 0.13 is close to release
- Updates for spice 0.6

* Tue Aug 10 2010 Justin M. Forbes <jforbes@redhat.com> - 2:0.13.0-0.5.20100809git25fdf4a
- Fix typo in e1000 gpxe rom requires.
- Add links to newer vgabios

* Tue Aug 10 2010 Justin M. Forbes <jforbes@redhat.com> - 2:0.13.0-0.4.20100809git25fdf4a
- Disable spice on 32bit, it is not supported and buildreqs don't exist.

* Mon Aug 9 2010 Justin M. Forbes <jforbes@redhat.com> - 2:0.13.0-0.3.20100809git25fdf4a
- Updates from upstream towards 0.13 stable
- Fix requires on gpxe
- enable spice now that buildreqs are in the repository.
- ksmtrace has moved to a separate upstream package

* Tue Jul 27 2010 Justin M. Forbes <jforbes@redhat.com> - 2:0.13.0-0.2.20100727gitb81fe95
- add texinfo buildreq for manpages.

* Tue Jul 27 2010 Justin M. Forbes <jforbes@redhat.com> - 2:0.13.0-0.1.20100727gitb81fe95
- Update to 0.13.0 upstream snapshot
- ksm init fixes from upstream

* Tue Jul 20 2010 Dan Horák <dan[at]danny.cz> - 2:0.12.3-8
- Add avoid-llseek patch from upstream needed for building on s390(x)
- Don't use parallel make on s390(x)

* Tue Jun 22 2010 Amit Shah <amit.shah@redhat.com> - 2:0.12.3-7
- Add vvfat hardening patch from upstream (#605202)

* Fri Apr 23 2010 Justin M. Forbes <jforbes@redhat.com> - 2:0.12.3-6
- Change requires to the noarch seabios-bin
- Add ownership of docdir to qemu-common (#572110)
- Fix "Cannot boot from non-existent NIC" error when using virt-install (#577851)

* Thu Apr 15 2010 Justin M. Forbes <jforbes@redhat.com> - 2:0.12.3-5
- Update virtio console patches from upstream

* Thu Mar 11 2010 Justin M. Forbes <jforbes@redhat.com> - 2:0.12.3-4
- Detect cdrom via ioctl (#473154)
- re add increased buffer for USB control requests (#546483)

* Wed Mar 10 2010 Justin M. Forbes <jforbes@redhat.com> - 2:0.12.3-3
- Migration clear the fd in error cases (#518032)

* Tue Mar 09 2010 Justin M. Forbes <jforbes@redhat.com> - 2:0.12.3-2
- Allow builds --with x86only
- Add libaio-devel buildreq for aio support

* Fri Feb 26 2010 Justin M. Forbes <jforbes@redhat.com> - 2:0.12.3-1
- Update to 0.12.3 upstream
- vhost-net migration/restart fixes
- Add F-13 machine type
- virtio-serial fixes

* Tue Feb 09 2010 Justin M. Forbes <jforbes@redhat.com> - 2:0.12.2-6
- Add vhost net support.

* Thu Feb 04 2010 Justin M. Forbes <jforbes@redhat.com> - 2:0.12.2-5
- Avoid creating too large iovecs in multiwrite merge (#559717)
- Don't try to set max_kernel_pages during ksm init on newer kernels (#558281)
- Add logfile options for ksmtuned debug.

* Wed Jan 27 2010 Amit Shah <amit.shah@redhat.com> - 2:0.12.2-4
- Remove build dependency on iasl now that we have seabios

* Wed Jan 27 2010 Amit Shah <amit.shah@redhat.com> - 2:0.12.2-3
- Remove source target for 0.12.1.2

* Wed Jan 27 2010 Amit Shah <amit.shah@redhat.com> - 2:0.12.2-2
- Add virtio-console patches from upstream for the F13 VirtioSerial feature

* Mon Jan 25 2010 Justin M. Forbes <jforbes@redhat.com> - 2:0.12.2-1
- Update to 0.12.2 upstream

* Sun Jan 10 2010 Justin M. Forbes <jforbes@redhat.com> - 2:0.12.1.2-3
- Point to seabios instead of bochs, and add a requires for seabios

* Mon Jan  4 2010 Justin M. Forbes <jforbes@redhat.com> - 2:0.12.1.2-2
- Remove qcow2 virtio backing file patch

* Mon Jan  4 2010 Justin M. Forbes <jforbes@redhat.com> - 2:0.12.1.2-1
- Update to 0.12.1.2 upstream
- Remove patches included in upstream

* Fri Nov 20 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.11.0-12
- Fix a use-after-free crasher in the slirp code (#539583)
- Fix overflow in the parallels image format support (#533573)

* Wed Nov  4 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.11.0-11
- Temporarily disable preadv/pwritev support to fix data corruption (#526549)

* Tue Nov  3 2009 Justin M. Forbes <jforbes@redhat.com> - 2:0.11.0-10
- Default ksm and ksmtuned services on.

* Thu Oct 29 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.11.0-9
- Fix dropped packets with non-virtio NICs (#531419)

* Wed Oct 21 2009 Glauber Costa <gcosta@redhat.com> - 2:0.11.0-8
- Properly save kvm time registers (#524229)

* Mon Oct 19 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.11.0-7
- Fix potential segfault from too small MSR_COUNT (#528901)

* Fri Oct  9 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.11.0-6
- Fix fs errors with virtio and qcow2 backing file (#524734)
- Fix ksm initscript errors on kernel missing ksm (#527653)
- Add missing Requires(post): getent, useradd, groupadd (#527087)

* Tue Oct  6 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.11.0-5
- Add 'retune' verb to ksmtuned init script

* Mon Oct  5 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.11.0-4
- Use rtl8029 PXE rom for ne2k_pci, not ne (#526777)
- Also, replace the gpxe-roms-qemu pkg requires with file-based requires

* Thu Oct  1 2009 Justin M. Forbes <jmforbes@redhat.com> - 2:0.11.0-3
- Improve error reporting on file access (#524695)

* Mon Sep 28 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.11.0-2
- Fix pci hotplug to not exit if supplied an invalid NIC model (#524022)

* Mon Sep 28 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.11.0-1
- Update to 0.11.0 release
- Drop a couple of upstreamed patches

* Wed Sep 23 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.92-5
- Fix issue causing NIC hotplug confusion when no model is specified (#524022)

* Wed Sep 16 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.92-4
- Fix for KSM patch from Justin Forbes

* Wed Sep 16 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.92-3
- Add ksmtuned, also from Dan Kenigsberg
- Use %%_initddir macro

* Wed Sep 16 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.92-2
- Add ksm control script from Dan Kenigsberg

* Mon Sep  7 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.92-1
- Update to qemu-kvm-0.11.0-rc2
- Drop upstreamed patches
- extboot install now fixed upstream
- Re-place TCG init fix (#516543) with the one gone upstream

* Mon Sep  7 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.91-0.10.rc1
- Fix MSI-X error handling on older kernels (#519787)

* Fri Sep  4 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.91-0.9.rc1
- Make pulseaudio the default audio backend (#519540, #495964, #496627)

* Thu Aug 20 2009 Richard W.M. Jones <rjones@redhat.com> - 2:0.10.91-0.8.rc1
- Fix segfault when qemu-kvm is invoked inside a VM (#516543)

* Tue Aug 18 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.91-0.7.rc1
- Fix permissions on udev rules (#517571)

* Mon Aug 17 2009 Lubomir Rintel <lkundrak@v3.sk> - 2:0.10.91-0.6.rc1
- Allow blacklisting of kvm modules (#517866)

* Fri Aug  7 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.91-0.5.rc1
- Fix virtio_net with -net user (#516022)

* Tue Aug  4 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.91-0.4.rc1
- Update to qemu-kvm-0.11-rc1; no changes from rc1-rc0

* Tue Aug  4 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.91-0.3.rc1.rc0
- Fix extboot checksum (bug #514899)

* Fri Jul 31 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.91-0.2.rc1.rc0
- Add KSM support
- Require bochs-bios >= 2.3.8-0.8 for latest kvm bios updates

* Thu Jul 30 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.91-0.1.rc1.rc0
- Update to qemu-kvm-0.11.0-rc1-rc0
- This is a pre-release of the official -rc1
- A vista installer regression is blocking the official -rc1 release
- Drop qemu-prefer-sysfs-for-usb-host-devices.patch
- Drop qemu-fix-build-for-esd-audio.patch
- Drop qemu-slirp-Fix-guestfwd-for-incoming-data.patch
- Add patch to ensure extboot.bin is installed

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2:0.10.50-14.kvm88
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Thu Jul 23 2009 Glauber Costa <glommer@redhat.com> - 2:0.10.50-13.kvm88
- Fix bug 513249, -net channel option is broken

* Thu Jul 16 2009 Daniel P. Berrange <berrange@redhat.com> - 2:0.10.50-12.kvm88
- Add 'qemu' user and group accounts
- Force disable xen until it can be made to build

* Thu Jul 16 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.50-11.kvm88
- Update to kvm-88, see http://www.linux-kvm.org/page/ChangeLog
- Package mutiboot.bin
- Update for how extboot is built
- Fix sf.net source URL
- Drop qemu-fix-ppc-softmmu-kvm-disabled-build.patch
- Drop qemu-fix-pcspk-build-with-kvm-disabled.patch
- Cherry-pick fix for esound support build failure

* Wed Jul 15 2009 Daniel Berrange <berrange@lettuce.camlab.fab.redhat.com> - 2:0.10.50-10.kvm87
- Add udev rules to make /dev/kvm world accessible & group=kvm (rhbz #497341)
- Create a kvm group if it doesn't exist (rhbz #346151)

* Tue Jul 07 2009 Glauber Costa <glommer@redhat.com> - 2:0.10.50-9.kvm87
- use pxe roms from gpxe, instead of etherboot package.

* Fri Jul  3 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.50-8.kvm87
- Prefer sysfs over usbfs for usb passthrough (#508326)

* Sat Jun 27 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.50-7.kvm87
- Update to kvm-87
- Drop upstreamed patches
- Cherry-pick new ppc build fix from upstream
- Work around broken linux-user build on ppc
- Fix hw/pcspk.c build with --disable-kvm
- Re-enable preadv()/pwritev() since #497429 is long since fixed
- Kill petalogix-s3adsp1800.dtb, since we don't ship the microblaze target

* Fri Jun  5 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.50-6.kvm86
- Fix 'kernel requires an x86-64 CPU' error
- BuildRequires ncurses-devel to enable '-curses' option (#504226)

* Wed Jun  3 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.50-5.kvm86
- Prevent locked cdrom eject - fixes hang at end of anaconda installs (#501412)
- Avoid harmless 'unhandled wrmsr' warnings (#499712)

* Thu May 21 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.50-4.kvm86
- Update to kvm-86 release
- ChangeLog here: http://marc.info/?l=kvm&m=124282885729710

* Fri May  1 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.50-3.kvm85
- Really provide qemu-kvm as a metapackage for comps

* Tue Apr 28 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.50-2.kvm85
- Provide qemu-kvm as a metapackage for comps

* Mon Apr 27 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.50-1.kvm85
- Update to qemu-kvm-devel-85
- kvm-85 is based on qemu development branch, currently version 0.10.50
- Include new qemu-io utility in qemu-img package
- Re-instate -help string for boot=on to fix virtio booting with libvirt
- Drop upstreamed patches
- Fix missing kernel/include/asm symlink in upstream tarball
- Fix target-arm build
- Fix build on ppc
- Disable preadv()/pwritev() until bug #497429 is fixed
- Kill more .kernelrelease uselessness
- Make non-kvm qemu build verbose

* Fri Apr 24 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10-15
- Fix source numbering typos caused by make-release addition

* Thu Apr 23 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10-14
- Improve instructions for generating the tarball

* Tue Apr 21 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10-13
- Enable pulseaudio driver to fix qemu lockup at shutdown (#495964)

* Tue Apr 21 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10-12
- Another qcow2 image corruption fix (#496642)

* Mon Apr 20 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10-11
- Fix qcow2 image corruption (#496642)

* Sun Apr 19 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10-10
- Run sysconfig.modules from %%post on x86_64 too (#494739)

* Sun Apr 19 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10-9
- Align VGA ROM to 4k boundary - fixes 'qemu-kvm -std vga' (#494376)

* Tue Apr  14 2009 Glauber Costa <glommer@redhat.com> - 2:0.10-8
- Provide qemu-kvm conditional on the architecture.

* Thu Apr  9 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10-7
- Add a much cleaner fix for vga segfault (#494002)

* Sun Apr  5 2009 Glauber Costa <glommer@redhat.com> - 2:0.10-6
- Fixed qcow2 segfault creating disks over 2TB. #491943

* Fri Apr  3 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10-5
- Fix vga segfault under kvm-autotest (#494002)
- Kill kernelrelease hack; it's not needed
- Build with "make V=1" for more verbose logs

* Thu Apr 02 2009 Glauber Costa <glommer@redhat.com> - 2:0.10-4
- Support botting gpxe roms.

* Wed Apr 01 2009 Glauber Costa <glommer@redhat.com> - 2:0.10-2
- added missing patch. love for CVS.

* Wed Apr 01 2009 Glauber Costa <glommer@redhat.com> - 2:0.10-1
- Include debuginfo for qemu-img
- Do not require qemu-common for qemu-img
- Explicitly own each of the firmware files
- remove firmwares for ppc and sparc. They should be provided by an external package.
  Not that the packages exists for sparc in the secondary arch repo as noarch, but they
  don't automatically get into main repos. Unfortunately it's the best we can do right
  now.
- rollback a bit in time. Snapshot from avi's maint/2.6.30
  - this requires the sasl patches to come back.
  - with-patched-kernel comes back.

* Wed Mar 25 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10-0.12.kvm20090323git
- BuildRequires pciutils-devel for device assignment (#492076)

* Mon Mar 23 2009 Glauber Costa <glommer@redhat.com> - 2:0.10-0.11.kvm20090323git
- Update to snapshot kvm20090323.
- Removed patch2 (upstream).
- use upstream's new split package.
- --with-patched-kernel flag not needed anymore
- Tell how to get the sources.

* Wed Mar 18 2009 Glauber Costa <glommer@redhat.com> - 2:0.10-0.10.kvm20090310git
- Added extboot to files list.

* Wed Mar 11 2009 Glauber Costa <glommer@redhat.com> - 2:0.10-0.9.kvm20090310git
- Fix wrong reference to bochs bios.

* Wed Mar 11 2009 Glauber Costa <glommer@redhat.com> - 2:0.10-0.8.kvm20090310git
- fix Obsolete/Provides pair
- Use kvm bios from bochs-bios package.
- Using RPM_OPT_FLAGS in configure
- Picked back audio-drv-list from kvm package

* Tue Mar 10 2009 Glauber Costa <glommer@redhat.com> - 2:0.10-0.7.kvm20090310git
- modify ppc patch

* Tue Mar 10 2009 Glauber Costa <glommer@redhat.com> - 2:0.10-0.6.kvm20090310git
- updated to kvm20090310git
- removed sasl patches (already in this release)

* Tue Mar 10 2009 Glauber Costa <glommer@redhat.com> - 2:0.10-0.5.kvm20090303git
- kvm.modules were being wrongly mentioned at %%install.
- update description for the x86 system package to include kvm support
- build kvm's own bios. It is still necessary while kvm uses a slightly different
  irq routing mechanism

* Thu Mar 05 2009 Glauber Costa <glommer@redhat.com> - 2:0.10-0.4.kvm20090303git
- seems Epoch does not go into the tags. So start back here.

* Thu Mar 05 2009 Glauber Costa <glommer@redhat.com> - 2:0.10-0.1.kvm20090303git
- Use bochs-bios instead of bochs-bios-data
- It's official: upstream set on 0.10

* Thu Mar  5 2009 Daniel P. Berrange <berrange@redhat.com> - 2:0.9.2-0.2.kvm20090303git
- Added BSD to license list, since many files are covered by BSD

* Wed Mar 04 2009 Glauber Costa <glommer@redhat.com> - 0.9.2-0.1.kvm20090303git
- missing a dot. shame on me

* Wed Mar 04 2009 Glauber Costa <glommer@redhat.com> - 0.92-0.1.kvm20090303git
- Set Epoch to 2
- Set version to 0.92. It seems upstream keep changing minds here, so pick the lowest
- Provides KVM, Obsoletes KVM
- Only install qemu-kvm in ix86 and x86_64
- Remove pkgdesc macros, as they were generating bogus output for rpm -qi.
- fix ppc and ppc64 builds

* Tue Mar 03 2009 Glauber Costa <glommer@redhat.com> - 0.10-0.3.kvm20090303git
- only execute post scripts for user package.
- added kvm tools.

* Tue Mar 03 2009 Glauber Costa <glommer@redhat.com> - 0.10-0.2.kvm20090303git
- put kvm.modules into cvs

* Tue Mar 03 2009 Glauber Costa <glommer@redhat.com> - 0.10-0.1.kvm20090303git
- Set Epoch to 1
- Build KVM (basic build, no tools yet)
- Set ppc in ExcludeArch. This is temporary, just to fix one issue at a time.
  ppc users (IBM ? ;-)) please wait a little bit.

* Tue Mar  3 2009 Daniel P. Berrange <berrange@redhat.com> - 1.0-0.5.svn6666
- Support VNC SASL authentication protocol
- Fix dep on bochs-bios-data

* Tue Mar 03 2009 Glauber Costa <glommer@redhat.com> - 1.0-0.4.svn6666
- use bios from bochs-bios package.

* Tue Mar 03 2009 Glauber Costa <glommer@redhat.com> - 1.0-0.3.svn6666
- use vgabios from vgabios package.

* Mon Mar 02 2009 Glauber Costa <glommer@redhat.com> - 1.0-0.2.svn6666
- use pxe roms from etherboot package.

* Mon Mar 02 2009 Glauber Costa <glommer@redhat.com> - 1.0-0.1.svn6666
- Updated to tip svn (release 6666). Featuring split packages for qemu.
  Unfortunately, still using binary blobs for the bioses.

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9.1-13
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sun Jan 11 2009 Debarshi Ray <rishi@fedoraproject.org> - 0.9.1-12
- Updated build patch. Closes Red Hat Bugzilla bug #465041.

* Wed Dec 31 2008 Dennis Gilmore <dennis@ausil.us> - 0.9.1-11
- add sparcv9 and sparc64 support

* Fri Jul 25 2008 Bill Nottingham <notting@redhat.com>
- Fix qemu-img summary (#456344)

* Wed Jun 25 2008 Daniel P. Berrange <berrange@redhat.com> - 0.9.1-10.fc10
- Rebuild for GNU TLS ABI change

* Wed Jun 11 2008 Daniel P. Berrange <berrange@redhat.com> - 0.9.1-9.fc10
- Remove bogus wildcard from files list (rhbz #450701)

* Sat May 17 2008 Lubomir Rintel <lkundrak@v3.sk> - 0.9.1-8
- Register binary handlers also for shared libraries

* Mon May  5 2008 Daniel P. Berrange <berrange@redhat.com> - 0.9.1-7.fc10
- Fix text console PTYs to be in rawmode

* Sun Apr 27 2008 Lubomir Kundrak <lkundrak@redhat.com> - 0.9.1-6
- Register binary handler for SuperH-4 CPU

* Wed Mar 19 2008 Daniel P. Berrange <berrange@redhat.com> - 0.9.1-5.fc9
- Split qemu-img tool into sub-package for smaller footprint installs

* Wed Feb 27 2008 Daniel P. Berrange <berrange@redhat.com> - 0.9.1-4.fc9
- Fix block device checks for extendable disk formats (rhbz #435139)

* Sat Feb 23 2008 Daniel P. Berrange <berrange@redhat.com> - 0.9.1-3.fc9
- Fix block device extents check (rhbz #433560)

* Mon Feb 18 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 0.9.1-2
- Autorebuild for GCC 4.3

* Tue Jan  8 2008 Daniel P. Berrange <berrange@redhat.com> - 0.9.1-1.fc9
- Updated to 0.9.1 release
- Fix license tag syntax
- Don't mark init script as a config file

* Wed Sep 26 2007 Daniel P. Berrange <berrange@redhat.com> - 0.9.0-5.fc8
- Fix rtl8139 checksum calculation for Vista (rhbz #308201)

* Tue Aug 28 2007 Daniel P. Berrange <berrange@redhat.com> - 0.9.0-4.fc8
- Fix debuginfo by passing -Wl,--build-id to linker

* Tue Aug 28 2007 David Woodhouse <dwmw2@infradead.org> 0.9.0-4
- Update licence
- Fix CDROM emulation (#253542)

* Tue Aug 28 2007 Daniel P. Berrange <berrange@redhat.com> - 0.9.0-3.fc8
- Added backport of VNC password auth, and TLS+x509 cert auth
- Switch to rtl8139 NIC by default for linkstate reporting
- Fix rtl8139 mmio region mappings with multiple NICs

* Sun Apr  1 2007 Hans de Goede <j.w.r.degoede@hhs.nl> 0.9.0-2
- Fix direct loading of a linux kernel with -kernel & -initrd (bz 234681)
- Remove spurious execute bits from manpages (bz 222573)

* Tue Feb  6 2007 David Woodhouse <dwmw2@infradead.org> 0.9.0-1
- Update to 0.9.0

* Wed Jan 31 2007 David Woodhouse <dwmw2@infradead.org> 0.8.2-5
- Include licences

* Mon Nov 13 2006 Hans de Goede <j.w.r.degoede@hhs.nl> 0.8.2-4
- Backport patch to make FC6 guests work by Kevin Kofler
  <Kevin@tigcc.ticalc.org> (bz 207843).

* Mon Sep 11 2006 David Woodhouse <dwmw2@infradead.org> 0.8.2-3
- Rebuild

* Thu Aug 24 2006 Matthias Saou <http://freshrpms.net/> 0.8.2-2
- Remove the target-list iteration for x86_64 since they all build again.
- Make gcc32 vs. gcc34 conditional on %%{fedora} to share the same spec for
  FC5 and FC6.

* Wed Aug 23 2006 Matthias Saou <http://freshrpms.net/> 0.8.2-1
- Update to 0.8.2 (#200065).
- Drop upstreamed syscall-macros patch2.
- Put correct scriplet dependencies.
- Force install mode for the init script to avoid umask problems.
- Add %%postun condrestart for changes to the init script to be applied if any.
- Update description with the latest "about" from the web page (more current).
- Update URL to qemu.org one like the Source.
- Add which build requirement.
- Don't include texi files in %%doc since we ship them in html.
- Switch to using gcc34 on devel, FC5 still has gcc32.
- Add kernheaders patch to fix linux/compiler.h inclusion.
- Add target-sparc patch to fix compiling on ppc (some int32 to float).

* Thu Jun  8 2006 David Woodhouse <dwmw2@infradead.org> 0.8.1-3
- More header abuse in modify_ldt(), change BuildRoot:

* Wed Jun  7 2006 David Woodhouse <dwmw2@infradead.org> 0.8.1-2
- Fix up kernel header abuse

* Tue May 30 2006 David Woodhouse <dwmw2@infradead.org> 0.8.1-1
- Update to 0.8.1

* Sat Mar 18 2006 David Woodhouse <dwmw2@infradead.org> 0.8.0-6
- Update linker script for PPC

* Sat Mar 18 2006 David Woodhouse <dwmw2@infradead.org> 0.8.0-5
- Just drop $RPM_OPT_FLAGS. They're too much of a PITA

* Sat Mar 18 2006 David Woodhouse <dwmw2@infradead.org> 0.8.0-4
- Disable stack-protector options which gcc 3.2 doesn't like

* Fri Mar 17 2006 David Woodhouse <dwmw2@infradead.org> 0.8.0-3
- Use -mcpu= instead of -mtune= on x86_64 too
- Disable SPARC targets on x86_64, because dyngen doesn't like fnegs

* Fri Mar 17 2006 David Woodhouse <dwmw2@infradead.org> 0.8.0-2
- Don't use -mtune=pentium4 on i386. GCC 3.2 doesn't like it

* Fri Mar 17 2006 David Woodhouse <dwmw2@infradead.org> 0.8.0-1
- Update to 0.8.0
- Resort to using compat-gcc-32
- Enable ALSA

* Mon May 16 2005 David Woodhouse <dwmw2@infradead.org> 0.7.0-2
- Proper fix for GCC 4 putting 'blr' or 'ret' in the middle of the function,
  for i386, x86_64 and PPC.

* Sat Apr 30 2005 David Woodhouse <dwmw2@infradead.org> 0.7.0-1
- Update to 0.7.0
- Fix dyngen for PPC functions which end in unconditional branch

* Thu Apr  7 2005 Michael Schwendt <mschwendt[AT]users.sf.net>
- rebuilt

* Sun Feb 13 2005 David Woodhouse <dwmw2@infradead.org> 0.6.1-2
- Package cleanup

* Sun Nov 21 2004 David Woodhouse <dwmw2@redhat.com> 0.6.1-1
- Update to 0.6.1

* Tue Jul 20 2004 David Woodhouse <dwmw2@redhat.com> 0.6.0-2
- Compile fix from qemu CVS, add x86_64 host support

* Wed May 12 2004 David Woodhouse <dwmw2@redhat.com> 0.6.0-1
- Update to 0.6.0.

* Sat May 8 2004 David Woodhouse <dwmw2@redhat.com> 0.5.5-1
- Update to 0.5.5.

* Sun May 2 2004 David Woodhouse <dwmw2@redhat.com> 0.5.4-1
- Update to 0.5.4.

* Thu Apr 22 2004 David Woodhouse <dwmw2@redhat.com> 0.5.3-1
- Update to 0.5.3. Add init script.

* Thu Jul 17 2003 Jeff Johnson <jbj@redhat.com> 0.4.3-1
- Create.
