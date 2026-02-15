# -*- rpm-spec -*-

# This spec file assumes you are building on a Fedora or RHEL version
# that's still supported by the vendor. It may work on other distros
# or versions, but no effort will be made to ensure that going forward.
%define min_rhel 9
%define min_fedora 41

%define arches_qemu_kvm         %{ix86} x86_64 %{power64} aarch64 s390x riscv64
%if 0%{?rhel}
    %if 0%{?rhel} >= 10
        %define arches_qemu_kvm     x86_64 aarch64 s390x riscv64
    %else
        %define arches_qemu_kvm     x86_64 aarch64 s390x
    %endif
%endif

%define arches_64bit            x86_64 %{power64} aarch64 s390x riscv64
%define arches_x86              %{ix86} x86_64

%define arches_systemtap_64bit  %{arches_64bit}
%define arches_dmidecode        %{arches_x86} aarch64 riscv64
%define arches_xen              %{arches_x86} aarch64
%if 0%{?fedora}
    %define arches_xen          x86_64 aarch64
%endif
%define arches_vbox             %{arches_x86}
%define arches_ceph             %{arches_64bit}
%define arches_zfs              %{arches_x86} %{power64} %{arm} aarch64
%define arches_numactl          %{arches_x86} %{power64} aarch64 s390x
%define arches_numad            %{arches_x86} %{power64} aarch64
%define arches_ch               x86_64 aarch64

# The hypervisor drivers that run in libvirtd
%define with_lxc           0%{!?_without_lxc:1}
%define with_libxl         0%{!?_without_libxl:1}
%define with_vbox          0%{!?_without_vbox:1}
%define with_ch            0%{!?_without_ch:1}

%ifarch %{arches_64bit}
    %define with_qemu      0%{!?_without_qemu:1}
%else
    # QEMU drops 32-bit in Fedora 44
    %if 0%{?fedora} > 43
        %define with_qemu  0
    %else
        %define with_qemu  0%{!?_without_qemu:1}
    %endif
%endif

%ifarch %{arches_qemu_kvm}
    %define with_qemu_kvm      %{with_qemu}
%else
    %define with_qemu_kvm      0
%endif

%if 0%{?fedora} >= 42
    %define with_account_add 0
%else
    %define with_account_add 1
%endif

%define with_qemu_tcg      %{with_qemu}

# RHEL disables TCG on all architectures
%if 0%{?rhel}
    %define with_qemu_tcg 0
%endif

%if ! %{with_qemu_tcg} && ! %{with_qemu_kvm}
    %define with_qemu 0
%endif

# Then the hypervisor drivers that run outside libvirtd, in libvirt.so
%define with_openvz        0%{!?_without_openvz:1}
%define with_vmware        0%{!?_without_vmware:1}
%define with_esx           0%{!?_without_esx:1}
%define with_hyperv        0%{!?_without_hyperv:1}

# Then the secondary host drivers, which run inside libvirtd
%define with_storage_rbd      0%{!?_without_storage_rbd:1}

%define with_storage_gluster 0%{!?_without_storage_gluster:1}
%if 0%{?rhel}
    # Glusterfs has been dropped in RHEL-9.
    %define with_storage_gluster 0
%endif

%define with_storage_zfs      1

%define with_storage_iscsi_direct 0%{!?_without_storage_iscsi_direct:1}
# libiscsi has been dropped in RHEL-9
%if 0%{?rhel}
    %define with_storage_iscsi_direct 0
%endif

# Other optional features
%define with_numactl          0%{!?_without_numactl:1}

# A few optional bits off by default, we enable later
%define with_fuse             0
%define with_sanlock          0
%define with_numad            0
%define with_nbdkit           0
%define with_nbdkit_config_default 0
%define with_firewalld_zone   0
%define with_netcf            0
%define with_libssh2          0
%define with_wireshark        0
%define with_libssh           0
%define with_dmidecode        0

# Finally set the OS / architecture specific special cases

# Architecture-dependent features
%ifnarch %{arches_xen}
    %define with_libxl 0
%endif
%ifnarch %{arches_vbox}
    %define with_vbox 0
%endif
%ifnarch %{arches_numactl}
    %define with_numactl 0
%endif
%ifnarch %{arches_zfs}
    %define with_storage_zfs 0
%endif
%ifnarch %{arches_ceph}
    %define with_storage_rbd 0
%endif
%ifnarch %{arches_ch}
    %define with_ch 0
%endif

# RHEL doesn't ship many hypervisor drivers
%if 0%{?rhel}
    %define with_openvz 0
    %define with_vbox 0
    %define with_vmware 0
    %define with_libxl 0
    %define with_hyperv 0
    %define with_lxc 0
    %define with_ch 0
%endif

%define with_firewalld_zone 0%{!?_without_firewalld_zone:1}

# fuse is used to provide virtualized /proc for LXC
%if %{with_lxc}
    %define with_fuse      0%{!?_without_fuse:1}
%endif

# Enable sanlock library for lock management with QEMU
# Sanlock is available only on arches where kvm is available for RHEL
%if 0%{?fedora}
    %define with_sanlock 0%{!?_without_sanlock:1}
%endif
%if 0%{?rhel}
    %ifarch %{arches_qemu_kvm}
        %define with_sanlock 0%{!?_without_sanlock:1}
    %endif
%endif

# Enable libssh2 transport for new enough distros
%if 0%{?fedora}
    %define with_libssh2 0%{!?_without_libssh2:1}
%endif

# Enable wireshark plugins for all distros
%define with_wireshark 0%{!?_without_wireshark:1}
%define wireshark_plugindir %(pkg-config --variable plugindir wireshark)/epan

# Enable libssh transport for all distros
%define with_libssh 0%{!?_without_libssh:1}

%if %{with_qemu} || %{with_lxc}
# numad is used to manage the CPU and memory placement dynamically,
# it's not available on many non-x86 architectures.
    %ifarch %{arches_numad}
        %define with_numad    0%{!?_without_numad:1}
    %endif
%endif

# We want to build with nbdkit support, but should only enable nbdkit by
# default if the OS ships a SELinux policy that allows libvirt to launch it.
# Right now that's not the case anywhere, but things should be fine by the time
# Fedora 40 is released.
%if %{with_qemu}
    %if 0%{?fedora} || 0%{?rhel}
        %define with_nbdkit 0%{!?_without_nbdkit:1}

        # setting 'with_nbdkit_config_default' must be done only when compiling
        # in nbdkit support
        #
        # TODO: add RHEL 9 once a minor release that contains the necessary SELinux
        #       bits exists (we only support the most recent minor release)
        %if 0%{?fedora}
            %define with_nbdkit_config_default 0%{!?_without_nbdkit_config_default:1}
        %endif
    %endif
%endif

%ifarch %{arches_dmidecode}
    %define with_dmidecode 0%{!?_without_dmidecode:1}
%endif

%define with_modular_daemons 0
%if 0%{?fedora} || 0%{?rhel}
    %define with_modular_daemons 1
%endif

# Prefer nftables for future OS releases but keep using iptables
# for existing ones
%if 0%{?rhel} >= 10 || 0%{?fedora}
    %define prefer_nftables 1
    %define firewall_backend_priority nftables,iptables
%else
    %define prefer_nftables 0
    %define firewall_backend_priority iptables,nftables
%endif



# Force QEMU to run as non-root
%define qemu_user  qemu
%define qemu_group  qemu

# Locations for QEMU data
%define qemu_moddir %{_libdir}/qemu
%define qemu_datadir %{_datadir}/qemu

# Native / MinGW builds
%define with_native 0%{!?_without_native:1}

%define with_mingw32 0
%define with_mingw64 0

%if 0%{?fedora}
    %if 0%{!?_without_mingw:1}
        %define with_mingw32 0%{!?_without_mingw32:1}
        %define with_mingw64 0%{!?_without_mingw64:1}
    %endif

    # These tell the other mingw macros whether to perform or
    # skip the 32-bit and 64-bit specific steps respectively
    %define mingw_build_win32 %{with_mingw32}
    %define mingw_build_win64 %{with_mingw64}
%endif

%if !%{with_native}
    # Building the debugsource package apparently only works if the
    # native build is enabled. debuginfo packages don't have this
    # problem and setting this doesn't disable them
    %global debug_package %{nil}
%endif

# RHEL releases provide stable tool chains and so it is safe to turn
# compiler warning into errors without being worried about frequent
# changes in reported warnings
%if 0%{?rhel}
    %define enable_werror -Dwerror=true
%else
    %define enable_werror -Dwerror=false -Dgit_werror=disabled
%endif

%define tls_priority "@LIBVIRT,SYSTEM"

# libvirt 8.1.0 stops distributing any sysconfig files.
# If the user has customized their sysconfig file,
# the RPM upgrade path will rename it to .rpmsave
# because the file is no longer managed by RPM.
# To prevent a regression we rename it back after the
# transaction to preserve the user's modifications
%define libvirt_sysconfig_pre() \
    for sc in %{?*} ; do \
        test -f "%{_sysconfdir}/sysconfig/${sc}.rpmsave" || continue ; \
        mv -v "%{_sysconfdir}/sysconfig/${sc}.rpmsave" "%{_sysconfdir}/sysconfig/${sc}.rpmsave.old" ; \
    done \
    %{nil}
%define libvirt_sysconfig_posttrans() \
    for sc in %{?*} ; do \
        test -f "%{_sysconfdir}/sysconfig/${sc}.rpmsave" || continue ; \
        mv -v "%{_sysconfdir}/sysconfig/${sc}.rpmsave" "%{_sysconfdir}/sysconfig/${sc}" ; \
    done \
    %{nil}

Summary: Library providing a simple virtualization API
Name: libvirt
Version: 11.10.0
Release: 4%{?dist}%{?extra_release}
License: GPL-2.0-or-later AND LGPL-2.1-only AND LGPL-2.1-or-later AND OFL-1.1
URL: https://libvirt.org/

%if %(echo %{version} | grep "\.0$" >/dev/null; echo $?) == 1
    %define mainturl stable_updates/
%endif
Source: https://download.libvirt.org/%{?mainturl}libvirt-%{version}.tar.xz
Patch1: libvirt-qemu-tpm-Account-for-possible-migration-without-actually-sharing-storage.patch
Patch2: libvirt-tests-Test-virFileIsSharedFSOverride.patch
Patch3: libvirt-util-Fix-race-condition-in-virFileIsSharedFSType.patch
Patch4: libvirt-util-Fix-race-condition-in-virFileIsSharedFSOverride.patch
Patch5: libvirt-util-Rework-virFileIsSharedFSOverride-using-virFileCheckParents.patch
Patch6: libvirt-util-json-Increase-JSON-nesting-limit-when-parsing-to-300.patch
Patch7: libvirt-virjsontest-Add-test-for-nesting-depth.patch
Patch8: libvirt-qemu_validate-Drop-VIR_DOMAIN_HYPERV_SYNIC-dependency-on-VIR_DOMAIN_HYPERV_VPINDEX.patch
Patch9: libvirt-qemu_validate-Drop-VIR_DOMAIN_HYPERV_STIMER-dependency-on-VIR_DOMAIN_HYPERV_VPINDEX.patch
Patch10: libvirt-esx_util-Introduce-esxUtil_EscapeInventoryObject.patch
Patch11: libvirt-esx-URI-encode-inventory-objects-twice.patch
Patch12: libvirt-qemuSecurityMoveImageMetadata-Move-seclabels-only-to-virStorageSource-of-same-type.patch
Patch13: libvirt-qemuDomainSetThrottleGroup-Enforce-non-zero-groupname-string-length.patch
Patch14: libvirt-qemuDomainSetBlockIoTuneField-Move-setting-of-group_name-out-of-the-loop.patch
Patch15: libvirt-qemuDomainSetThrottleGroup-Always-honour-thottle-group-name-passed-as-argument.patch
Patch16: libvirt-qemuDomainSetThrottleGroup-Don-t-put-group-name-into-the-tunable-event-twice.patch
Patch17: libvirt-qemuSnapshotDiskHasBackingDisk-Avoid-call-of-virStorageSourceIsSameLocation-with-NULL-argument.patch
Patch18: libvirt-qemuSnapshotUpdateBackingStore-Remove-stale-comment.patch
Patch19: libvirt-qemuSnapshotDiskHasBackingDisk-Use-proper-max_depth-when-calling-virStorageSourceGetMetadata.patch
Patch20: libvirt-virDomainSnapshotDefAssignExternalNames-Improve-error-message.patch
Patch21: libvirt-qemuSnapshotUpdateBackingStore-Retry-as-curent-user-if-qemu-img-fails.patch


Requires: libvirt-daemon = %{version}-%{release}
Requires: libvirt-daemon-config-network = %{version}-%{release}
Requires: libvirt-daemon-config-nwfilter = %{version}-%{release}
%if %{with_libxl}
Requires: libvirt-daemon-driver-libxl = %{version}-%{release}
%endif
%if %{with_lxc}
Requires: libvirt-daemon-driver-lxc = %{version}-%{release}
%endif
%if %{with_qemu}
Requires: libvirt-daemon-driver-qemu = %{version}-%{release}
Requires: libvirt-client-qemu = %{version}-%{release}
%endif
# We had UML driver, but we've removed it.
Obsoletes: libvirt-daemon-driver-uml <= 5.0.0
Obsoletes: libvirt-daemon-uml <= 5.0.0
%if %{with_vbox}
Requires: libvirt-daemon-driver-vbox = %{version}-%{release}
%endif
%if %{with_ch}
Requires: libvirt-daemon-driver-ch = %{version}-%{release}
%endif
Requires: libvirt-daemon-driver-nwfilter = %{version}-%{release}
Requires: libvirt-daemon-driver-interface = %{version}-%{release}
Requires: libvirt-daemon-driver-secret = %{version}-%{release}
Requires: libvirt-daemon-driver-storage = %{version}-%{release}
Requires: libvirt-daemon-driver-network = %{version}-%{release}
Requires: libvirt-daemon-driver-nodedev = %{version}-%{release}
Requires: libvirt-client = %{version}-%{release}
Requires: libvirt-libs = %{version}-%{release}

# All build-time requirements. Run-time requirements are
# listed against each sub-RPM
BuildRequires: python3-docutils
BuildRequires: meson >= 0.56.0
BuildRequires: ninja-build
BuildRequires: git-core
BuildRequires: perl-interpreter
BuildRequires: python3
BuildRequires: python3-pytest
# For xmllint
BuildRequires: libxml2
# For xsltproc
BuildRequires: libxslt
BuildRequires: gettext
BuildRequires: systemd-rpm-macros
# Fedora build root suckage
BuildRequires: gawk
%if %{with_native}
BuildRequires: gcc
    %if %{with_libxl}
BuildRequires: xen-devel
    %endif
BuildRequires: glib2-devel >= 2.66
BuildRequires: libxml2-devel
BuildRequires: readline-devel
BuildRequires: pkgconfig(bash-completion) >= 2.0
BuildRequires: libtasn1-devel
BuildRequires: gnutls-devel
BuildRequires: libattr-devel
# For pool-build probing for existing pools
BuildRequires: libblkid-devel >= 2.17
# for augparse, optionally used in testing
BuildRequires: augeas
BuildRequires: systemd-devel >= 185
BuildRequires: libpciaccess-devel >= 0.10.9
BuildRequires: json-c-devel
    %if %{with_sanlock}
BuildRequires: sanlock-devel >= 2.4
    %endif
BuildRequires: libpcap-devel >= 1.5.0
BuildRequires: libnl3-devel
BuildRequires: libselinux-devel
BuildRequires: cyrus-sasl-devel
    %if %{with_qemu}
# For managing ACLs
BuildRequires: libacl-devel
# From QEMU RPMs, used by virstoragetest
BuildRequires: /usr/bin/qemu-img
    %endif
# nbdkit support requires libnbd
    %if %{with_nbdkit}
BuildRequires: libnbd-devel
    %endif
    %if %{with_storage_iscsi_direct}
# For pool type=iscsi-direct
BuildRequires: libiscsi-devel
    %endif
# For disk driver
BuildRequires: parted-devel
# For Multipath support
BuildRequires: device-mapper-devel
    %if %{with_storage_rbd}
BuildRequires: librados-devel
BuildRequires: librbd-devel
    %endif
    %if %{with_storage_gluster}
BuildRequires: glusterfs-api-devel >= 3.4.1
BuildRequires: glusterfs-devel >= 3.4.1
    %endif
    %if %{with_numactl}
# For QEMU/LXC numa info
BuildRequires: numactl-devel
    %endif
BuildRequires: libcap-ng-devel >= 0.5.0
    %if %{with_fuse}
BuildRequires: fuse3-devel
    %endif
    %if %{with_libssh2}
BuildRequires: libssh2-devel >= 1.3.0
    %endif
    %if %{with_netcf}
BuildRequires: netcf-devel >= 0.2.2
    %endif
    %if %{with_esx}
BuildRequires: libcurl-devel
    %endif
    %if %{with_hyperv}
BuildRequires: libwsman-devel >= 2.6.3
    %endif
BuildRequires: audit-libs-devel
BuildRequires: systemtap-sdt-devel
BuildRequires: /usr/bin/dtrace
    %if %{with_wireshark}
BuildRequires: wireshark-devel
    %endif
    %if %{with_libssh}
BuildRequires: libssh-devel >= 0.8.1
    %endif
BuildRequires: libtirpc-devel
    %if %{with_firewalld_zone}
# Needed for the firewalld_reload macro
BuildRequires: firewalld-filesystem
    %endif
%endif

%if %{with_mingw32}
BuildRequires: mingw32-filesystem
BuildRequires: mingw32-gcc
BuildRequires: mingw32-binutils
BuildRequires: mingw32-glib2 >= 2.48
BuildRequires: mingw32-gnutls
BuildRequires: mingw32-gettext
BuildRequires: mingw32-libxml2
BuildRequires: mingw32-portablexdr
BuildRequires: mingw32-dlfcn
BuildRequires: mingw32-libssh2
BuildRequires: mingw32-curl
%endif
%if %{with_mingw64}
BuildRequires: mingw64-filesystem
BuildRequires: mingw64-gcc
BuildRequires: mingw64-binutils
BuildRequires: mingw64-glib2 >= 2.48
BuildRequires: mingw64-gnutls
BuildRequires: mingw64-gettext
BuildRequires: mingw64-libxml2
BuildRequires: mingw64-portablexdr
BuildRequires: mingw64-dlfcn
BuildRequires: mingw64-libssh2
BuildRequires: mingw64-curl
%endif

%description
Libvirt is a C toolkit to interact with the virtualization capabilities
of recent versions of Linux (and other OSes). The main package includes
the libvirtd server exporting the virtualization support.

%if %{with_native}
%package docs
Summary: API reference and website documentation

%description docs
Includes the API reference for the libvirt C library, and a complete
copy of the libvirt.org website documentation.

%package daemon
Summary: Server side daemon and supporting files for libvirt library

# All runtime requirements for the libvirt package (runtime requrements
# for subpackages are listed later in those subpackages)

# The client side, i.e. shared libs are in a subpackage
Requires: libvirt-libs = %{version}-%{release}
Requires: libvirt-daemon-common = %{version}-%{release}
Requires: libvirt-daemon-lock = %{version}-%{release}
Requires: libvirt-daemon-plugin-lockd = %{version}-%{release}
Requires: libvirt-daemon-log = %{version}-%{release}
Requires: libvirt-daemon-proxy = %{version}-%{release}

%description daemon
Server side daemon required to manage the virtualization capabilities
of recent versions of Linux. Requires a hypervisor specific sub-RPM
for specific drivers.

%package daemon-common
Summary: Files and utilities used by daemons
Requires: libvirt-libs = %{version}-%{release}
# The libvirt-guests.sh script requires virsh from libvirt-client subpackage,
# but not every deployment wants to use libvirt-guests service. Using
# Recommends here will install libvirt-client by default (if available), but
# RPM won't complain if the package is unavailable, masked, or removed later.
Recommends: libvirt-client = %{version}-%{release}
# For modprobe and rmmod
Requires: kmod
# for /sbin/ip
Requires: iproute
# for /sbin/tc
Requires: iproute-tc
Requires: polkit >= 0.112
    %if %{with_dmidecode}
# For virConnectGetSysinfo
Requires: dmidecode
    %endif
# For service management
Requires(posttrans): /usr/bin/systemctl
Requires(preun): /usr/bin/systemctl
# libvirtd depends on 'messagebus' service
Requires: dbus
    %if %{with_account_add}
# For uid creation during pre
Requires(pre): shadow-utils
    %endif
# Needed by /usr/libexec/libvirt-guests.sh script.
    %if 0%{?fedora}
Requires: gettext-runtime
    %else
Requires: gettext
    %endif

# Ensure smooth upgrades
Obsoletes: libvirt-admin < 7.3.0
Provides: libvirt-admin = %{version}-%{release}
Obsoletes: libvirt-bash-completion < 7.3.0

%description daemon-common
Miscellaneous files and utilities used by other libvirt daemons

%package daemon-lock
Summary: Server side daemon for managing locks
Requires: libvirt-libs = %{version}-%{release}

%description daemon-lock
Server side daemon used to manage locks held against virtual machine
resources

%package daemon-plugin-lockd
Summary: lockd client plugin for virtlockd
Requires: libvirt-libs = %{version}-%{release}
Requires: libvirt-daemon-common = %{version}-%{release}
Requires: libvirt-daemon-lock = %{version}-%{release}

%description daemon-plugin-lockd
A client-side plugin that implements disk locking using POSIX fcntl advisory
locks via communication with the virtlockd daemon

%package daemon-log
Summary: Server side daemon for managing logs
Requires: libvirt-libs = %{version}-%{release}

%description daemon-log
Server side daemon used to manage logs from virtual machine consoles

%package daemon-proxy
Summary: Server side daemon providing libvirtd proxy
Requires: libvirt-libs = %{version}-%{release}
# netcat is needed on the server side so that clients that have
# libvirt < 6.9.0 can connect, but newer versions will prefer
# virt-ssh-helper. Making this a Recommends means that it gets
# installed by default, but can still be removed if compatibility
# with old clients is not required
Recommends: /usr/bin/nc

%description daemon-proxy
Server side daemon providing functionality previously provided by
the monolithic libvirtd

%package daemon-config-network
Summary: Default configuration files for the libvirtd daemon

Requires: libvirt-daemon-driver-network = %{version}-%{release}

%description daemon-config-network
Default configuration files for setting up NAT based networking

%package daemon-config-nwfilter
Summary: Network filter configuration files for the libvirtd daemon

Requires: libvirt-daemon-driver-nwfilter = %{version}-%{release}

%description daemon-config-nwfilter
Network filter configuration files for cleaning guest traffic

%package daemon-driver-network
Summary: Network driver plugin for the libvirtd daemon
Requires: libvirt-daemon-common = %{version}-%{release}
Requires: libvirt-libs = %{version}-%{release}
Requires: dnsmasq >= 2.41
    %if %{prefer_nftables}
Requires: nftables
    %else
Requires: iptables
    %endif

%description daemon-driver-network
The network driver plugin for the libvirtd daemon, providing
an implementation of the virtual network APIs using the Linux
bridge capabilities.

%package daemon-driver-nwfilter
Summary: Nwfilter driver plugin for the libvirtd daemon
Requires: libvirt-daemon-common = %{version}-%{release}
Requires: libvirt-libs = %{version}-%{release}
Requires: iptables
Requires: ebtables

%description daemon-driver-nwfilter
The nwfilter driver plugin for the libvirtd daemon, providing
an implementation of the firewall APIs using the ebtables,
iptables and ip6tables capabilities

%package daemon-driver-nodedev
Summary: Nodedev driver plugin for the libvirtd daemon
Requires: libvirt-daemon-common = %{version}-%{release}
Requires: libvirt-libs = %{version}-%{release}
# needed for device enumeration
Requires: systemd >= 185
# For managing persistent mediated devices
# Note: for nodedev-update support at least mdevctl v1.3.0 is required
Requires: mdevctl
# for modprobe of pci devices
Requires: module-init-tools

%description daemon-driver-nodedev
The nodedev driver plugin for the libvirtd daemon, providing
an implementation of the node device APIs using the udev
capabilities.

%package daemon-driver-interface
Summary: Interface driver plugin for the libvirtd daemon
Requires: libvirt-daemon-common = %{version}-%{release}
Requires: libvirt-libs = %{version}-%{release}
    %if %{with_netcf}
Requires: netcf-libs >= 0.2.2
    %endif

%description daemon-driver-interface
The interface driver plugin for the libvirtd daemon, providing
an implementation of the host network interface APIs.

%package daemon-driver-secret
Summary: Secret driver plugin for the libvirtd daemon
Requires: libvirt-daemon-common = %{version}-%{release}
Requires: libvirt-libs = %{version}-%{release}

%description daemon-driver-secret
The secret driver plugin for the libvirtd daemon, providing
an implementation of the secret key APIs.

%package daemon-driver-storage-core
Summary: Storage driver plugin including base backends for the libvirtd daemon
Requires: libvirt-daemon-common = %{version}-%{release}
Requires: libvirt-libs = %{version}-%{release}
Recommends: nfs-utils
# For mkfs and mount/umount
Requires: util-linux
# For storage wiping with different algorithms
Requires: scrub
    %if %{with_qemu}
# From QEMU RPMs
Requires: /usr/bin/qemu-img
    %endif
    %if !%{with_storage_rbd}
Obsoletes: libvirt-daemon-driver-storage-rbd < 5.2.0
    %endif
Obsoletes: libvirt-daemon-driver-storage-sheepdog < 8.8.0

%description daemon-driver-storage-core
The storage driver plugin for the libvirtd daemon, providing
an implementation of the storage APIs using files, local disks, LVM, SCSI,
iSCSI, and multipath storage.

%package daemon-driver-storage-logical
Summary: Storage driver plugin for lvm volumes
Requires: libvirt-daemon-driver-storage-core = %{version}-%{release}
Requires: libvirt-libs = %{version}-%{release}
Requires: lvm2

%description daemon-driver-storage-logical
The storage driver backend adding implementation of the storage APIs for block
volumes using lvm.

%package daemon-driver-storage-disk
Summary: Storage driver plugin for disk
Requires: libvirt-daemon-driver-storage-core = %{version}-%{release}
Requires: libvirt-libs = %{version}-%{release}
Requires: parted
Requires: device-mapper

%description daemon-driver-storage-disk
The storage driver backend adding implementation of the storage APIs for block
volumes using the host disks.

%package daemon-driver-storage-scsi
Summary: Storage driver plugin for local scsi devices
Requires: libvirt-daemon-driver-storage-core = %{version}-%{release}
Requires: libvirt-libs = %{version}-%{release}

%description daemon-driver-storage-scsi
The storage driver backend adding implementation of the storage APIs for scsi
host devices.

%package daemon-driver-storage-iscsi
Summary: Storage driver plugin for iscsi
Requires: libvirt-daemon-driver-storage-core = %{version}-%{release}
Requires: libvirt-libs = %{version}-%{release}
Requires: iscsi-initiator-utils

%description daemon-driver-storage-iscsi
The storage driver backend adding implementation of the storage APIs for iscsi
volumes using the host iscsi stack.

    %if %{with_storage_iscsi_direct}
%package daemon-driver-storage-iscsi-direct
Summary: Storage driver plugin for iscsi-direct
Requires: libvirt-daemon-driver-storage-core = %{version}-%{release}
Requires: libvirt-libs = %{version}-%{release}

%description daemon-driver-storage-iscsi-direct
The storage driver backend adding implementation of the storage APIs for iscsi
volumes using libiscsi direct connection.
    %endif

%package daemon-driver-storage-mpath
Summary: Storage driver plugin for multipath volumes
Requires: libvirt-daemon-driver-storage-core = %{version}-%{release}
Requires: libvirt-libs = %{version}-%{release}
Requires: device-mapper

%description daemon-driver-storage-mpath
The storage driver backend adding implementation of the storage APIs for
multipath storage using device mapper.

    %if %{with_storage_gluster}
%package daemon-driver-storage-gluster
Summary: Storage driver plugin for gluster
Requires: libvirt-daemon-driver-storage-core = %{version}-%{release}
Requires: libvirt-libs = %{version}-%{release}
        %if 0%{?fedora}
Requires: glusterfs-client >= 2.0.1
        %endif
        %if 0%{?fedora} || 0%{?with_storage_gluster}
Requires: /usr/sbin/gluster
        %endif

%description daemon-driver-storage-gluster
The storage driver backend adding implementation of the storage APIs for gluster
volumes using libgfapi.
    %endif

    %if %{with_storage_rbd}
%package daemon-driver-storage-rbd
Summary: Storage driver plugin for rbd
Requires: libvirt-daemon-driver-storage-core = %{version}-%{release}
Requires: libvirt-libs = %{version}-%{release}

%description daemon-driver-storage-rbd
The storage driver backend adding implementation of the storage APIs for rbd
volumes using the ceph protocol.
    %endif

    %if %{with_storage_zfs}
%package daemon-driver-storage-zfs
Summary: Storage driver plugin for ZFS
Requires: libvirt-daemon-driver-storage-core = %{version}-%{release}
Requires: libvirt-libs = %{version}-%{release}
# Starting with Fedora 43 the 'zfs-fuse' is no longer shipped but obtainable
# externally. The package builds fine without these. Users will have to provide
# their own implementation.
        %if 0%{?fedora} && 0%{?fedora} < 43
Requires: /sbin/zfs
Requires: /sbin/zpool
        %endif

%description daemon-driver-storage-zfs
The storage driver backend adding implementation of the storage APIs for
ZFS volumes.
    %endif

%package daemon-driver-storage
Summary: Storage driver plugin including all backends for the libvirtd daemon
Requires: libvirt-daemon-driver-storage-core = %{version}-%{release}
Requires: libvirt-daemon-driver-storage-disk = %{version}-%{release}
Requires: libvirt-daemon-driver-storage-logical = %{version}-%{release}
Requires: libvirt-daemon-driver-storage-scsi = %{version}-%{release}
Requires: libvirt-daemon-driver-storage-iscsi = %{version}-%{release}
Requires: libvirt-daemon-driver-storage-mpath = %{version}-%{release}
    %if %{with_storage_iscsi_direct}
Requires: libvirt-daemon-driver-storage-iscsi-direct = %{version}-%{release}
    %endif
    %if %{with_storage_gluster}
Requires: libvirt-daemon-driver-storage-gluster = %{version}-%{release}
    %endif
    %if %{with_storage_rbd}
Requires: libvirt-daemon-driver-storage-rbd = %{version}-%{release}
    %endif
# Starting with Fedora 43 the 'zfs-fuse' is no longer shipped but obtainable
# externally. We do not want to install this as part of 'daemon-driver-storage'
# any more.
    %if %{with_storage_zfs} && 0%{?fedora} && 0%{?fedora} < 43
Requires: libvirt-daemon-driver-storage-zfs = %{version}-%{release}
    %endif

%description daemon-driver-storage
The storage driver plugin for the libvirtd daemon, providing
an implementation of the storage APIs using LVM, iSCSI,
parted and more.

    %if %{with_qemu}
%package daemon-driver-qemu
Summary: QEMU driver plugin for the libvirtd daemon
Requires: libvirt-daemon-common = %{version}-%{release}
Requires: libvirt-daemon-log = %{version}-%{release}
Requires: libvirt-libs = %{version}-%{release}
Requires: /usr/bin/qemu-img
# For image compression
Requires: gzip
Requires: bzip2
Requires: lzop
Requires: xz
Requires: zstd
Requires: systemd-container
Requires: swtpm-tools
        %if %{with_numad}
Requires: numad
        %endif
        %if 0%{?fedora} || 0%{?rhel}
Recommends: passt
Recommends: passt-selinux
        %endif
        %if %{with_nbdkit}
Recommends: nbdkit
Recommends: nbdkit-curl-plugin
Recommends: nbdkit-ssh-plugin
        %endif

%description daemon-driver-qemu
The qemu driver plugin for the libvirtd daemon, providing
an implementation of the hypervisor driver APIs using
QEMU
    %endif

    %if %{with_lxc}
%package daemon-driver-lxc
Summary: LXC driver plugin for the libvirtd daemon
Requires: libvirt-daemon-common = %{version}-%{release}
Requires: libvirt-libs = %{version}-%{release}
# There really is a hard cross-driver dependency here
Requires: libvirt-daemon-driver-network = %{version}-%{release}
Requires: systemd-container
# for modprobe of nbd driver
Requires: module-init-tools
        %if %{with_numad}
Requires: numad
        %endif

%description daemon-driver-lxc
The LXC driver plugin for the libvirtd daemon, providing
an implementation of the hypervisor driver APIs using
the Linux kernel
    %endif

    %if %{with_vbox}
%package daemon-driver-vbox
Summary: VirtualBox driver plugin for the libvirtd daemon
Requires: libvirt-daemon-common = %{version}-%{release}
Requires: libvirt-libs = %{version}-%{release}

%description daemon-driver-vbox
The vbox driver plugin for the libvirtd daemon, providing
an implementation of the hypervisor driver APIs using
VirtualBox
    %endif

    %if %{with_libxl}
%package daemon-driver-libxl
Summary: Libxl driver plugin for the libvirtd daemon
Requires: libvirt-daemon-common = %{version}-%{release}
Requires: libvirt-libs = %{version}-%{release}
Obsoletes: libvirt-daemon-driver-xen < 4.3.0

%description daemon-driver-libxl
The Libxl driver plugin for the libvirtd daemon, providing
an implementation of the hypervisor driver APIs using
Libxl
    %endif

    %if %{with_qemu_tcg}
%package daemon-qemu
Summary: Server side daemon & driver required to run QEMU guests

        %if %{with_modular_daemons}
Requires: libvirt-daemon-common = %{version}-%{release}
Requires: libvirt-daemon-log = %{version}-%{release}
Requires: libvirt-daemon-lock = %{version}-%{release}
Requires: libvirt-daemon-plugin-lockd = %{version}-%{release}
Requires: libvirt-daemon-proxy = %{version}-%{release}
Recommends: libvirt-daemon = %{version}-%{release}
        %else
Requires: libvirt-daemon = %{version}-%{release}
        %endif
Requires: libvirt-daemon-driver-qemu = %{version}-%{release}
Requires: libvirt-daemon-driver-interface = %{version}-%{release}
Requires: libvirt-daemon-driver-network = %{version}-%{release}
Requires: libvirt-daemon-driver-nodedev = %{version}-%{release}
Requires: libvirt-daemon-driver-nwfilter = %{version}-%{release}
Requires: libvirt-daemon-driver-secret = %{version}-%{release}
Requires: libvirt-daemon-driver-storage = %{version}-%{release}
Requires: libvirt-ssh-proxy = %{version}-%{release}
Requires: qemu

%description daemon-qemu
Server side daemon and driver required to manage the virtualization
capabilities of the QEMU TCG emulators
    %endif

    %if %{with_qemu_kvm}
%package daemon-kvm
Summary: Server side daemon & driver required to run KVM guests

        %if %{with_modular_daemons}
Requires: libvirt-daemon-common = %{version}-%{release}
Requires: libvirt-daemon-log = %{version}-%{release}
Requires: libvirt-daemon-lock = %{version}-%{release}
Requires: libvirt-daemon-plugin-lockd = %{version}-%{release}
Requires: libvirt-daemon-proxy = %{version}-%{release}
Recommends: libvirt-daemon = %{version}-%{release}
        %else
Requires: libvirt-daemon = %{version}-%{release}
        %endif
Requires: libvirt-daemon-driver-qemu = %{version}-%{release}
Requires: libvirt-daemon-driver-interface = %{version}-%{release}
Requires: libvirt-daemon-driver-network = %{version}-%{release}
Requires: libvirt-daemon-driver-nodedev = %{version}-%{release}
Requires: libvirt-daemon-driver-nwfilter = %{version}-%{release}
Requires: libvirt-daemon-driver-secret = %{version}-%{release}
Requires: libvirt-daemon-driver-storage = %{version}-%{release}
Requires: libvirt-ssh-proxy = %{version}-%{release}
Requires: qemu-kvm

%description daemon-kvm
Server side daemon and driver required to manage the virtualization
capabilities of the KVM hypervisor
    %endif

    %if %{with_lxc}
%package daemon-lxc
Summary: Server side daemon & driver required to run LXC guests

        %if %{with_modular_daemons}
Requires: libvirt-daemon-common = %{version}-%{release}
Requires: libvirt-daemon-proxy = %{version}-%{release}
Recommends: libvirt-daemon = %{version}-%{release}
        %else
Requires: libvirt-daemon = %{version}-%{release}
        %endif
Requires: libvirt-daemon-driver-lxc = %{version}-%{release}
Requires: libvirt-daemon-driver-interface = %{version}-%{release}
Requires: libvirt-daemon-driver-network = %{version}-%{release}
Requires: libvirt-daemon-driver-nodedev = %{version}-%{release}
Requires: libvirt-daemon-driver-nwfilter = %{version}-%{release}
Requires: libvirt-daemon-driver-secret = %{version}-%{release}
Requires: libvirt-daemon-driver-storage = %{version}-%{release}

%description daemon-lxc
Server side daemon and driver required to manage the virtualization
capabilities of LXC
    %endif

    %if %{with_libxl}
%package daemon-xen
Summary: Server side daemon & driver required to run XEN guests

        %if %{with_modular_daemons}
Requires: libvirt-daemon-common = %{version}-%{release}
Requires: libvirt-daemon-lock = %{version}-%{release}
Requires: libvirt-daemon-plugin-lockd = %{version}-%{release}
Requires: libvirt-daemon-proxy = %{version}-%{release}
Recommends: libvirt-daemon = %{version}-%{release}
        %else
Requires: libvirt-daemon = %{version}-%{release}
        %endif
Requires: libvirt-daemon-driver-libxl = %{version}-%{release}
Requires: libvirt-daemon-driver-interface = %{version}-%{release}
Requires: libvirt-daemon-driver-network = %{version}-%{release}
Requires: libvirt-daemon-driver-nodedev = %{version}-%{release}
Requires: libvirt-daemon-driver-secret = %{version}-%{release}
Requires: libvirt-daemon-driver-storage = %{version}-%{release}
Requires: xen

%description daemon-xen
Server side daemon and driver required to manage the virtualization
capabilities of XEN
    %endif

    %if %{with_vbox}
%package daemon-vbox
Summary: Server side daemon & driver required to run VirtualBox guests

        %if %{with_modular_daemons}
Requires: libvirt-daemon-common = %{version}-%{release}
Requires: libvirt-daemon-proxy = %{version}-%{release}
Recommends: libvirt-daemon = %{version}-%{release}
        %else
Requires: libvirt-daemon = %{version}-%{release}
        %endif
Requires: libvirt-daemon-driver-vbox = %{version}-%{release}
Requires: libvirt-daemon-driver-interface = %{version}-%{release}
Requires: libvirt-daemon-driver-network = %{version}-%{release}
Requires: libvirt-daemon-driver-nodedev = %{version}-%{release}
Requires: libvirt-daemon-driver-nwfilter = %{version}-%{release}
Requires: libvirt-daemon-driver-secret = %{version}-%{release}
Requires: libvirt-daemon-driver-storage = %{version}-%{release}

%description daemon-vbox
Server side daemon and driver required to manage the virtualization
capabilities of VirtualBox
    %endif

    %if %{with_ch}
%package daemon-driver-ch
Summary: Cloud-Hypervisor driver plugin for libvirtd daemon
Requires: libvirt-daemon-common = %{version}-%{release}
Requires: libvirt-daemon-log = %{version}-%{release}
Requires: libvirt-libs = %{version}-%{release}

%description daemon-driver-ch
The ch driver plugin for the libvirtd daemon, providing
an implementation of the hypervisor driver APIs by
Cloud-Hypervisor
    %endif


%package client
Summary: Client side utilities of the libvirt library
Requires: libvirt-libs = %{version}-%{release}

# Ensure smooth upgrades
Obsoletes: libvirt-bash-completion < 7.3.0

%description client
The client binaries needed to access the virtualization
capabilities of recent versions of Linux (and other OSes).

%package client-qemu
Summary: Additional client side utilities for QEMU
Requires: libvirt-libs = %{version}-%{release}
Requires: python3-libvirt >= 3.7.0
Requires: python3-cryptography
Requires: python3-lxml

%description client-qemu
The additional client binaries are used to interact
with some QEMU specific features of libvirt.

%package libs
Summary: Client side libraries
# Needed by default sasl.conf - no onerous extra deps, since
# 100's of other things on a system already pull in krb5-libs
Requires: cyrus-sasl-gssapi

%description libs
Shared libraries for accessing the libvirt daemon.

    %if %{with_wireshark}
%package wireshark
Summary: Wireshark dissector plugin for libvirt RPC transactions
Requires: wireshark
Requires: libvirt-libs = %{version}-%{release}

%description wireshark
Wireshark dissector plugin for better analysis of libvirt RPC traffic.
    %endif

    %if %{with_lxc}
%package login-shell
Summary: Login shell for connecting users to an LXC container
Requires: libvirt-libs = %{version}-%{release}
        %if %{with_account_add}
# For uid creation during pre
Requires(pre): shadow-utils
        %endif

%description login-shell
Provides the set-uid virt-login-shell binary that is used to
connect a user to an LXC container when they login, by switching
namespaces.
    %endif

%package devel
Summary: Libraries, includes, etc. to compile with the libvirt library
Requires: libvirt-libs = %{version}-%{release}
Requires: pkgconfig

%description devel
Include header files & development libraries for the libvirt C library.

    %if %{with_sanlock}
%package daemon-plugin-sanlock
Summary: Sanlock lock manager plugin for QEMU driver
Requires: sanlock >= 2.4
#for virt-sanlock-cleanup require augeas
Requires: augeas
Requires: libvirt-libs = %{version}-%{release}
Requires: libvirt-daemon-common = %{version}-%{release}
Obsoletes: libvirt-lock-sanlock < 9.1.0
Provides: libvirt-lock-sanlock = %{version}-%{release}

%description daemon-plugin-sanlock
Includes the Sanlock lock manager plugin for the QEMU
driver
    %endif

%package nss
Summary: Libvirt plugin for Name Service Switch
Requires: libvirt-daemon-driver-network = %{version}-%{release}

%description nss
Libvirt plugin for NSS for translating domain names into IP addresses.
%endif

%package ssh-proxy
Summary: Libvirt SSH proxy
Requires: libvirt-libs = %{version}-%{release}

%description ssh-proxy
Allows SSH into domains via VSOCK without need for network.

%if %{with_mingw32}
%package -n mingw32-libvirt
Summary: %{summary}
Obsoletes: mingw32-libvirt-static < 7.0.0
BuildArch: noarch

%description -n mingw32-libvirt
MinGW Windows libvirt virtualization library.

%{?mingw32_debug_package}
%endif

%if %{with_mingw64}
%package -n mingw64-libvirt
Summary: %{summary}
Obsoletes: mingw64-libvirt-static < 7.0.0
BuildArch: noarch

%description -n mingw64-libvirt
MinGW Windows libvirt virtualization library.

%{?mingw64_debug_package}
%endif

%prep
%autosetup -S git_am -N

%autopatch


%build
%if 0%{?fedora} >= %{min_fedora} || 0%{?rhel} >= %{min_rhel}
    %define supported_platform 1
%else
    %define supported_platform 0
%endif

%if ! %{supported_platform}
echo "This RPM requires either Fedora >= %{min_fedora} or RHEL >= %{min_rhel}"
exit 1
%endif

%if %{with_qemu}
    %define arg_qemu -Ddriver_qemu=enabled
%else
    %define arg_qemu -Ddriver_qemu=disabled
%endif

%if %{with_openvz}
    %define arg_openvz -Ddriver_openvz=enabled
%else
    %define arg_openvz -Ddriver_openvz=disabled
%endif

%if %{with_lxc}
    %define arg_lxc -Ddriver_lxc=enabled
    %define arg_login_shell -Dlogin_shell=enabled
%else
    %define arg_lxc -Ddriver_lxc=disabled
    %define arg_login_shell -Dlogin_shell=disabled
%endif

%if %{with_vbox}
    %define arg_vbox -Ddriver_vbox=enabled
%else
    %define arg_vbox -Ddriver_vbox=disabled
%endif

%if %{with_libxl}
    %define arg_libxl -Ddriver_libxl=enabled
%else
    %define arg_libxl -Ddriver_libxl=disabled
%endif

%if %{with_esx}
    %define arg_esx -Ddriver_esx=enabled
%else
    %define arg_esx -Ddriver_esx=disabled
%endif

%if %{with_esx} || %{with_ch}
    %define arg_curl -Dcurl=enabled
%else
    %define arg_curl -Dcurl=disabled
%endif

%if %{with_hyperv}
    %define arg_hyperv -Ddriver_hyperv=enabled -Dopenwsman=enabled
%else
    %define arg_hyperv -Ddriver_hyperv=disabled -Dopenwsman=disabled
%endif

%if %{with_vmware}
    %define arg_vmware -Ddriver_vmware=enabled
%else
    %define arg_vmware -Ddriver_vmware=disabled
%endif

%if %{with_ch}
    %define arg_ch -Ddriver_ch=enabled
%else
    %define arg_ch -Ddriver_ch=disabled
%endif

%if %{with_storage_rbd}
    %define arg_storage_rbd -Dstorage_rbd=enabled
%else
    %define arg_storage_rbd -Dstorage_rbd=disabled
%endif

%if %{with_storage_gluster}
    %define arg_storage_gluster -Dstorage_gluster=enabled -Dglusterfs=enabled
%else
    %define arg_storage_gluster -Dstorage_gluster=disabled -Dglusterfs=disabled
%endif

%if %{with_storage_zfs}
    %define arg_storage_zfs -Dstorage_zfs=enabled
%else
    %define arg_storage_zfs -Dstorage_zfs=disabled
%endif

%if %{with_numactl}
    %define arg_numactl -Dnumactl=enabled
%else
    %define arg_numactl -Dnumactl=disabled
%endif

%if %{with_numad}
    %define arg_numad -Dnumad=enabled
%else
    %define arg_numad -Dnumad=disabled
%endif

%if %{with_nbdkit}
    %define arg_nbdkit -Dnbdkit=enabled
%else
    %define arg_nbdkit -Dnbdkit=disabled
%endif

%if %{with_nbdkit_config_default}
    %define arg_nbdkit_config_default -Dnbdkit_config_default=enabled
%else
    %define arg_nbdkit_config_default -Dnbdkit_config_default=disabled
%endif

%if %{with_fuse}
    %define arg_fuse -Dfuse=enabled
%else
    %define arg_fuse -Dfuse=disabled
%endif

%if %{with_sanlock}
    %define arg_sanlock -Dsanlock=enabled
%else
    %define arg_sanlock -Dsanlock=disabled
%endif

%if %{with_firewalld_zone}
    %define arg_firewalld_zone -Dfirewalld_zone=enabled
%else
    %define arg_firewalld_zone -Dfirewalld_zone=disabled
%endif

%if %{with_netcf}
    %define arg_netcf -Dnetcf=enabled
%else
    %define arg_netcf -Dnetcf=disabled
%endif

%if %{with_wireshark}
    %define arg_wireshark -Dwireshark_dissector=enabled
%else
    %define arg_wireshark -Dwireshark_dissector=disabled
%endif

%if %{with_storage_iscsi_direct}
    %define arg_storage_iscsi_direct -Dstorage_iscsi_direct=enabled -Dlibiscsi=enabled
%else
    %define arg_storage_iscsi_direct -Dstorage_iscsi_direct=disabled -Dlibiscsi=disabled
%endif

%if %{with_libssh}
    %define arg_libssh -Dlibssh=enabled
%else
    %define arg_libssh -Dlibssh=disabled
%endif

%if %{with_libssh2}
    %define arg_libssh2 -Dlibssh2=enabled
%else
    %define arg_libssh2 -Dlibssh2=disabled
%endif

%if %{with_modular_daemons}
    %define arg_remote_mode -Dremote_default_mode=direct
%else
    %define arg_remote_mode -Dremote_default_mode=legacy
%endif

%define when  %(date +"%%F-%%T")
%define where %(hostname)
%define who   %{?packager}%{!?packager:Unknown}
%define arg_packager -Dpackager="%{who}, %{when}, %{where}"
%define arg_packager_version -Dpackager_version="%{release}"
%define arg_selinux_mount -Dselinux_mount="/sys/fs/selinux"

# place macros above and build commands below this comment

export SOURCE_DATE_EPOCH=$(stat --printf='%Y' %{_specdir}/libvirt.spec)

%if %{with_native}
%meson \
           -Drunstatedir=%{_rundir} \
           -Dinitconfdir=%{_sysconfdir}/sysconfig \
           -Dunitdir=%{_unitdir} \
           -Dsysusersdir=%{_sysusersdir} \
           %{?arg_qemu} \
           %{?arg_openvz} \
           %{?arg_lxc} \
           %{?arg_vbox} \
           %{?arg_libxl} \
           -Dsasl=enabled \
           -Dpolkit=enabled \
           -Ddriver_libvirtd=enabled \
           -Ddriver_remote=enabled \
           -Ddriver_test=enabled \
           %{?arg_esx} \
           %{?arg_curl} \
           %{?arg_hyperv} \
           %{?arg_vmware} \
           %{?arg_ch} \
           -Ddriver_vz=disabled \
           -Ddriver_bhyve=disabled \
           %{?arg_remote_mode} \
           -Ddriver_interface=enabled \
           -Ddriver_network=enabled \
           -Dstorage_fs=enabled \
           -Dstorage_lvm=enabled \
           -Dstorage_iscsi=enabled \
           %{?arg_storage_iscsi_direct} \
           -Dstorage_scsi=enabled \
           -Dstorage_disk=enabled \
           -Dstorage_mpath=enabled \
           %{?arg_storage_rbd} \
           %{?arg_storage_gluster} \
           %{?arg_storage_zfs} \
           -Dstorage_vstorage=disabled \
           %{?arg_numactl} \
           %{?arg_numad} \
           -Dcapng=enabled \
           %{?arg_fuse} \
           %{?arg_netcf} \
           -Dnls=enabled \
           -Dselinux=enabled \
           %{?arg_selinux_mount} \
           -Dapparmor=disabled \
           -Dapparmor_profiles=disabled \
           -Dsecdriver_apparmor=disabled \
           -Dudev=enabled \
           -Djson_c=enabled \
           %{?arg_sanlock} \
           -Dlibpcap=enabled \
           %{?arg_nbdkit} \
           %{?arg_nbdkit_config_default} \
           -Dlibnl=enabled \
           -Daudit=enabled \
           -Ddtrace=enabled \
           -Dfirewalld=enabled \
           %{?arg_firewalld_zone} \
           %{?arg_wireshark} \
           %{?arg_libssh} \
           %{?arg_libssh2} \
           -Dpm_utils=disabled \
           -Dnss=enabled \
           %{arg_packager} \
           %{arg_packager_version} \
           -Dqemu_user=%{qemu_user} \
           -Dqemu_group=%{qemu_group} \
           -Dqemu_moddir=%{qemu_moddir} \
           -Dqemu_datadir=%{qemu_datadir} \
           -Dtls_priority=%{tls_priority} \
           -Dsysctl_config=enabled \
           -Dssh_proxy=enabled \
           %{?enable_werror} \
           -Dexpensive_tests=enabled \
           -Dinit_script=systemd \
           -Dfirewall_backend_priority=%{firewall_backend_priority} \
           -Ddocs=enabled \
           -Dtests=enabled \
           -Drpath=disabled \
           %{?arg_login_shell}

%meson_build
%endif

%if %{with_mingw32} || %{with_mingw64}
%mingw_meson \
  --auto-features=enabled \
  -Ddriver_remote=enabled \
  -Ddriver_test=enabled \
  -Ddriver_esx=enabled \
  -Dcurl=enabled \
  -Ddocs=enabled \
  -Dapparmor=disabled \
  -Dapparmor_profiles=disabled \
  -Dattr=disabled \
  -Daudit=disabled \
  -Dbash_completion=disabled \
  -Dblkid=disabled \
  -Dcapng=disabled \
  -Ddriver_bhyve=disabled \
  -Ddriver_ch=disabled \
  -Ddriver_hyperv=disabled \
  -Ddriver_interface=disabled \
  -Ddriver_libvirtd=disabled \
  -Ddriver_libxl=disabled \
  -Ddriver_lxc=disabled \
  -Ddriver_network=disabled \
  -Ddriver_openvz=disabled \
  -Ddriver_qemu=disabled \
  -Ddriver_secrets=disabled \
  -Ddriver_vbox=disabled \
  -Ddriver_vmware=disabled \
  -Ddriver_vz=disabled \
  -Ddtrace=disabled \
  -Dexpensive_tests=disabled \
  -Dfirewalld=disabled \
  -Dfirewalld_zone=disabled \
  -Dfuse=disabled \
  -Dglusterfs=disabled \
  -Dhost_validate=disabled \
  -Djson_c=disabled \
  -Dlibiscsi=disabled \
  -Dnbdkit=disabled \
  -Dnbdkit_config_default=disabled \
  -Dlibnl=disabled \
  -Dlibpcap=disabled \
  -Dlibssh2=disabled \
  -Dlibssh=disabled \
  -Dlogin_shell=disabled \
  -Dnetcf=disabled \
  -Dnls=enabled \
  -Dnss=disabled \
  -Dnumactl=disabled \
  -Dnumad=disabled \
  -Dopenwsman=disabled \
  -Dpciaccess=disabled \
  -Dpm_utils=disabled \
  -Dpolkit=disabled \
  -Dreadline=disabled \
  -Drpath=disabled \
  -Dsanlock=disabled \
  -Dsasl=disabled \
  -Dsecdriver_apparmor=disabled \
  -Dsecdriver_selinux=disabled \
  -Dselinux=disabled \
  -Dstorage_dir=disabled \
  -Dstorage_disk=disabled \
  -Dstorage_fs=disabled \
  -Dstorage_gluster=disabled \
  -Dstorage_iscsi_direct=disabled \
  -Dstorage_iscsi=disabled \
  -Dstorage_lvm=disabled \
  -Dstorage_mpath=disabled \
  -Dstorage_rbd=disabled \
  -Dstorage_scsi=disabled \
  -Dstorage_vstorage=disabled \
  -Dstorage_zfs=disabled \
  -Dsysctl_config=disabled \
  -Dssh_proxy=disabled \
  -Dtests=disabled \
  -Dudev=disabled \
  -Dwireshark_dissector=disabled \
  %{?enable_werror}
%mingw_ninja
%endif

%install
rm -fr %{buildroot}

export SOURCE_DATE_EPOCH=$(stat --printf='%Y' %{_specdir}/libvirt.spec)

%if %{with_native}
%meson_install

# We don't want to install /etc/libvirt/qemu/networks in the main %%files list
# because if the admin wants to delete the default network completely, we don't
# want to end up re-incarnating it on every RPM upgrade.
install -d -m 0755 $RPM_BUILD_ROOT%{_datadir}/libvirt/networks/
cp $RPM_BUILD_ROOT%{_sysconfdir}/libvirt/qemu/networks/default.xml \
   $RPM_BUILD_ROOT%{_datadir}/libvirt/networks/default.xml
# libvirt saves this file with mode 0600
chmod 0600 $RPM_BUILD_ROOT%{_sysconfdir}/libvirt/qemu/networks/default.xml

# nwfilter files are installed in /usr/share/libvirt and copied to /etc in %%post
# to avoid verification errors on changed files in /etc
install -d -m 0755 $RPM_BUILD_ROOT%{_datadir}/libvirt/nwfilter/
cp -a $RPM_BUILD_ROOT%{_sysconfdir}/libvirt/nwfilter/*.xml \
    $RPM_BUILD_ROOT%{_datadir}/libvirt/nwfilter/
# libvirt saves these files with mode 600
chmod 600 $RPM_BUILD_ROOT%{_sysconfdir}/libvirt/nwfilter/*.xml

    %if ! %{with_qemu}
rm -f $RPM_BUILD_ROOT%{_datadir}/augeas/lenses/libvirtd_qemu.aug
rm -f $RPM_BUILD_ROOT%{_datadir}/augeas/lenses/tests/test_libvirtd_qemu.aug
rm -f $RPM_BUILD_ROOT%{_sysusersdir}/libvirt-qemu.conf
    %endif
%find_lang %{name}

    %if ! %{with_sanlock}
rm -f $RPM_BUILD_ROOT%{_datadir}/augeas/lenses/libvirt_sanlock.aug
rm -f $RPM_BUILD_ROOT%{_datadir}/augeas/lenses/tests/test_libvirt_sanlock.aug
    %endif

    %if ! %{with_lxc}
rm -f $RPM_BUILD_ROOT%{_datadir}/augeas/lenses/libvirtd_lxc.aug
rm -f $RPM_BUILD_ROOT%{_datadir}/augeas/lenses/tests/test_libvirtd_lxc.aug
    %endif

    %if ! %{with_qemu}
rm -rf $RPM_BUILD_ROOT%{_sysconfdir}/libvirt/qemu.conf
rm -rf $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/libvirtd.qemu
    %endif
    %if ! %{with_lxc}
rm -rf $RPM_BUILD_ROOT%{_sysconfdir}/libvirt/lxc.conf
rm -rf $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/libvirtd.lxc
    %endif
    %if ! %{with_libxl}
rm -rf $RPM_BUILD_ROOT%{_sysconfdir}/libvirt/libxl.conf
rm -rf $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/libvirtd.libxl
rm -f $RPM_BUILD_ROOT%{_datadir}/augeas/lenses/libvirtd_libxl.aug
rm -f $RPM_BUILD_ROOT%{_datadir}/augeas/lenses/tests/test_libvirtd_libxl.aug
    %endif
    %if ! %{with_ch}
rm -f $RPM_BUILD_ROOT%{_datadir}/augeas/lenses/libvirtd_ch.aug
rm -f $RPM_BUILD_ROOT%{_datadir}/augeas/lenses/tests/test_libvirtd_ch.aug
    %endif

# Copied into libvirt-docs subpackage eventually
mv $RPM_BUILD_ROOT%{_datadir}/doc/libvirt libvirt-docs

    %ifarch %{arches_systemtap_64bit}
mv $RPM_BUILD_ROOT%{_datadir}/systemtap/tapset/libvirt_probes.stp \
   $RPM_BUILD_ROOT%{_datadir}/systemtap/tapset/libvirt_probes-64.stp

        %if %{with_qemu}
mv $RPM_BUILD_ROOT%{_datadir}/systemtap/tapset/libvirt_qemu_probes.stp \
   $RPM_BUILD_ROOT%{_datadir}/systemtap/tapset/libvirt_qemu_probes-64.stp
        %endif
    %endif
%endif

%if %{with_mingw32} || %{with_mingw64}
%mingw_ninja_install
%endif

%if %{with_mingw32}
rm -rf $RPM_BUILD_ROOT%{mingw32_sysconfdir}/libvirt/nwfilter
rm -rf $RPM_BUILD_ROOT%{mingw32_datadir}/doc/*
rm -rf $RPM_BUILD_ROOT%{mingw32_datadir}/gtk-doc/*
rm -rf $RPM_BUILD_ROOT%{mingw32_libexecdir}/libvirt_iohelper.exe
rm -rf $RPM_BUILD_ROOT%{mingw32_libexecdir}/libvirt-guests.sh
%endif

%if %{with_mingw64}
rm -rf $RPM_BUILD_ROOT%{mingw64_sysconfdir}/libvirt/nwfilter
rm -rf $RPM_BUILD_ROOT%{mingw64_datadir}/doc/*
rm -rf $RPM_BUILD_ROOT%{mingw64_datadir}/gtk-doc/*
rm -rf $RPM_BUILD_ROOT%{mingw64_libexecdir}/libvirt_iohelper.exe
rm -rf $RPM_BUILD_ROOT%{mingw64_libexecdir}/libvirt-guests.sh
%endif

%if %{with_mingw32} || %{with_mingw64}
%mingw_debug_install_post

%mingw_find_lang %{name}

%endif

%check

%if %{with_native}
# Building on slow archs, like emulated s390x in Fedora copr, requires
# raising the test timeout
export VIR_TEST_DEBUG=1
%meson_test --no-suite syntax-check --timeout-multiplier 10
%endif

%define libvirt_rpmstatedir %{_localstatedir}/lib/rpm-state/libvirt

# Mark units such that presets will later be applied to them. Meant
# to be called during %pre. Units that already exist on the system
# will not be marked, with the assumption that presets have already
# been applied at some point in the past. This makes it safe to call
# this macro for all units each time %pre runs.
%define libvirt_systemd_schedule_preset() \
    mkdir -p %{libvirt_rpmstatedir} || : \
    for unit in %{?*}; do \
        if ! test -e %{_unitdir}/$unit; then \
            touch %{libvirt_rpmstatedir}/preset-$unit || : \
        fi \
    done \
    %{nil}

# Apply presets for units that have previously been marked. Meant to
# be called during %posttrans. Note that foo.service must be passed
# as the first argument, before all the various foo*.socket
# associated with it, for things to work correctly. This is necessary
# because Also=foo.socket is usually present in foo.service's
# [Install] section, and we want that configuration to take
# precedence over foo.socket's own presets.
%define libvirt_systemd_perform_preset() \
    %{?7:%{error:Too many arguments}} \
    for unit in %{?2} %{?3} %{?4} %{?5} %{?6} %1; do \
        if test -e %{libvirt_rpmstatedir}/preset-$unit; then \
            /usr/bin/systemctl --no-reload preset $unit || : \
        fi \
        rm -f %{libvirt_rpmstatedir}/preset-$unit \
    done \
    rmdir %{libvirt_rpmstatedir} 2>/dev/null || : \
    %{nil}

# Mark a single unit for restart. Meant to be called during %pre.
%define libvirt_systemd_schedule_restart() \
    mkdir -p %{libvirt_rpmstatedir} || : \
    touch %{libvirt_rpmstatedir}/restart-%1 || : \
    %{nil}

# Restart a unit that was previously marked. Meant to be called
# during %posttrans. If systemd is not running, no action will be
# performed.
%define libvirt_systemd_perform_restart() \
    if test -d /run/systemd/system && \
       test -e %{libvirt_rpmstatedir}/restart-%1; then \
        /usr/bin/systemctl try-restart %1 >/dev/null 2>&1 || : \
    fi \
    rm -f %{libvirt_rpmstatedir}/restart-%1 \
    rmdir %{libvirt_rpmstatedir} 2>/dev/null || : \
    %{nil}

# Mark a single unit for reload. Meant to be called during %pre.
%define libvirt_systemd_schedule_reload() \
    mkdir -p %{libvirt_rpmstatedir} || : \
    touch %{libvirt_rpmstatedir}/reload-%1 || : \
    %{nil}

# Reload a unit that was previously marked. Meant to be called during
# %posttrans. If systemd is not running, no action will be performed.
%define libvirt_systemd_perform_reload() \
    if test -d /run/systemd/system && \
       test -e %{libvirt_rpmstatedir}/reload-%1; then \
        /usr/bin/systemctl try-reload-or-restart %1 >/dev/null 2>&1 || : \
    fi \
    rm -f %{libvirt_rpmstatedir}/reload-%1 \
    rmdir %{libvirt_rpmstatedir} 2>/dev/null || : \
    %{nil}

# Disable a single unit, optionally stopping it if systemd is
# running. Meant to be called during %preun.
%define libvirt_systemd_disable() \
    if test -d /run/systemd/system; then \
        /usr/bin/systemctl --no-reload disable --now %{?*} || : \
    else \
        /usr/bin/systemctl --no-reload disable %{?*} || : \
    fi \
    %{nil}

# %pre implementation for services that should be restarted on
# upgrade. Note that foo.service must be passed as the first
# argument, before all the various foo*.socket associated with it.
%define libvirt_systemd_restart_pre() \
    %libvirt_systemd_schedule_preset %{?*} \
    %libvirt_systemd_schedule_restart %1 \
    %{nil}

# %pre implementation for services that should be reloaded on
# upgrade. Note that foo.service must be passed as the first
# argument, before all the various foo*.socket associated with it.
%define libvirt_systemd_reload_pre() \
    %libvirt_systemd_schedule_preset %{?*} \
    %libvirt_systemd_schedule_reload %1 \
    %{nil}

# %pre implementation for services that should be neither restarted
# nor reloaded on upgrade.
%define libvirt_systemd_noaction_pre() \
    %libvirt_systemd_schedule_preset %{?*} \
    %{nil}

# %posttrans implementation for all services. We can use a single
# macro to cover all scenarios, because each operation will only be
# performed if it had previously been scheduled. Note that
# foo.service must be passed as the first argument, before all the
# various foo*.socket associated with it.
%define libvirt_systemd_posttrans() \
    %libvirt_systemd_perform_preset %{?*} \
    %libvirt_systemd_perform_reload %1 \
    %libvirt_systemd_perform_restart %1 \
    %{nil}

# %preun implementation for all services.
%define libvirt_systemd_preun() \
    if [ $1 -lt 1 ]; then \
        %libvirt_systemd_disable %{?*} \
    fi \
    %{nil}

# For daemons with only UNIX sockets

%define libvirt_systemd_unix_pre() %libvirt_systemd_restart_pre %1.service %1.socket %1-ro.socket %1-admin.socket
%define libvirt_systemd_unix_posttrans() %libvirt_systemd_posttrans %1.service %1.socket %1-ro.socket %1-admin.socket
%define libvirt_systemd_unix_preun() %libvirt_systemd_preun %1.service %1.socket %1-ro.socket %1-admin.socket

# For daemons with UNIX and INET sockets
%define libvirt_systemd_inet_pre() %libvirt_systemd_restart_pre %1.service %1.socket %1-ro.socket %1-admin.socket %1-tls.socket %1-tcp.socket
%define libvirt_systemd_inet_posttrans() %libvirt_systemd_posttrans %1.service %1.socket %1-ro.socket %1-admin.socket %1-tls.socket %1-tcp.socket
%define libvirt_systemd_inet_preun() %libvirt_systemd_preun %1.service %1.socket %1-ro.socket %1-admin.socket %1-tls.socket %1-tcp.socket

# For daemons with only UNIX sockets and no unprivileged read-only access
%define libvirt_systemd_privileged_pre() %libvirt_systemd_reload_pre %1.service %1.socket %1-admin.socket
%define libvirt_systemd_privileged_posttrans() %libvirt_systemd_posttrans %1.service %1.socket %1-admin.socket
%define libvirt_systemd_privileged_preun() %libvirt_systemd_preun %1.service %1.socket %1-admin.socket

# For one-shot daemons that have no associated sockets and should never be restarted
%define libvirt_systemd_oneshot_pre() %libvirt_systemd_noaction_pre %1.service
%define libvirt_systemd_oneshot_posttrans() %libvirt_systemd_posttrans %1.service
%define libvirt_systemd_oneshot_preun() %libvirt_systemd_preun %1.service

# For packages that install configuration for other daemons
%define libvirt_systemd_config_pre() %libvirt_systemd_schedule_restart %1.service
%define libvirt_systemd_config_posttrans() %libvirt_systemd_perform_restart %1.service

%if %{with_native}
%pre daemon
%libvirt_sysconfig_pre libvirtd
%libvirt_systemd_inet_pre libvirtd

%posttrans daemon
%libvirt_sysconfig_posttrans libvirtd
%libvirt_systemd_inet_posttrans libvirtd

%preun daemon
%libvirt_systemd_inet_preun libvirtd

%pre daemon-common
%libvirt_sysconfig_pre libvirt-guests
%libvirt_systemd_oneshot_pre libvirt-guests
    %if %{with_account_add}
# 'libvirt' group is just to allow password-less polkit access to libvirt
# daemons. The uid number is irrelevant, so we use dynamic allocation.
getent group libvirt >/dev/null || groupadd -r libvirt
exit 0
    %endif

%posttrans daemon-common
%libvirt_sysconfig_posttrans libvirt-guests
%libvirt_systemd_oneshot_posttrans libvirt-guests

%preun daemon-common
%libvirt_systemd_oneshot_preun libvirt-guests

%pre daemon-lock
%libvirt_sysconfig_pre virtlockd
%libvirt_systemd_privileged_pre virtlockd

%posttrans daemon-lock
%libvirt_sysconfig_posttrans virtlockd
%libvirt_systemd_privileged_posttrans virtlockd

%preun daemon-lock
%libvirt_systemd_privileged_preun virtlockd

%pre daemon-log
%libvirt_sysconfig_pre virtlogd
%libvirt_systemd_privileged_pre virtlogd

%posttrans daemon-log
%libvirt_sysconfig_posttrans virtlogd
%libvirt_systemd_privileged_posttrans virtlogd

%preun daemon-log
%libvirt_systemd_privileged_preun virtlogd

%pre daemon-proxy
%libvirt_sysconfig_pre virtproxyd
%libvirt_systemd_inet_pre virtproxyd

%posttrans daemon-proxy
%libvirt_sysconfig_posttrans virtproxyd
%libvirt_systemd_inet_posttrans virtproxyd

%preun daemon-proxy
%libvirt_systemd_inet_preun virtproxyd

%pre daemon-driver-network
%libvirt_sysconfig_pre virtnetworkd
%libvirt_systemd_unix_pre virtnetworkd

%post daemon-driver-network
    %if %{with_firewalld_zone}
    %firewalld_reload
    %endif

%posttrans daemon-driver-network
%libvirt_sysconfig_posttrans virtnetworkd
%libvirt_systemd_unix_posttrans virtnetworkd

%preun daemon-driver-network
%libvirt_systemd_unix_preun virtnetworkd

%postun daemon-driver-network
    %if %{with_firewalld_zone}
    %firewalld_reload
    %endif

%pre daemon-driver-nwfilter
%libvirt_sysconfig_pre virtnwfilterd
%libvirt_systemd_unix_pre virtnwfilterd

%posttrans daemon-driver-nwfilter
%libvirt_sysconfig_posttrans virtnwfilterd
%libvirt_systemd_unix_posttrans virtnwfilterd

%preun daemon-driver-nwfilter
%libvirt_systemd_unix_preun virtnwfilterd

%pre daemon-driver-nodedev
%libvirt_sysconfig_pre virtnodedevd
%libvirt_systemd_unix_pre virtnodedevd

%posttrans daemon-driver-nodedev
%libvirt_sysconfig_posttrans virtnodedevd
%libvirt_systemd_unix_posttrans virtnodedevd

%preun daemon-driver-nodedev
%libvirt_systemd_unix_preun virtnodedevd

%pre daemon-driver-interface
%libvirt_sysconfig_pre virtinterfaced
%libvirt_systemd_unix_pre virtinterfaced

%posttrans daemon-driver-interface
%libvirt_sysconfig_posttrans virtinterfaced
%libvirt_systemd_unix_posttrans virtinterfaced

%preun daemon-driver-interface
%libvirt_systemd_unix_preun virtinterfaced

%pre daemon-driver-secret
%libvirt_sysconfig_pre virtsecretd
%libvirt_systemd_unix_pre virtsecretd

%posttrans daemon-driver-secret
%libvirt_sysconfig_posttrans virtsecretd
%libvirt_systemd_unix_posttrans virtsecretd

%preun daemon-driver-secret
%libvirt_systemd_unix_preun virtsecretd

%pre daemon-driver-storage-core
%libvirt_sysconfig_pre virtstoraged
%libvirt_systemd_unix_pre virtstoraged

%posttrans daemon-driver-storage-core
%libvirt_sysconfig_posttrans virtstoraged
%libvirt_systemd_unix_posttrans virtstoraged

%preun daemon-driver-storage-core
%libvirt_systemd_unix_preun virtstoraged

    %if %{with_qemu}
%pre daemon-driver-qemu
%libvirt_sysconfig_pre virtqemud
%libvirt_systemd_unix_pre virtqemud

        %if %{with_account_add}
# We want soft static allocation of well-known ids, as disk images
# are commonly shared across NFS mounts by id rather than name.
# See https://docs.fedoraproject.org/en-US/packaging-guidelines/UsersAndGroups/
# We can not use the sysusers_create_compat macro here as we want to keep the
# specfile standalone and not relying on additionnal files.
getent group 'kvm' >/dev/null || groupadd -f -g '36' -r 'kvm' || :
getent group 'qemu' >/dev/null || groupadd -f -g '107' -r 'qemu' || :
if ! getent passwd 'qemu' >/dev/null; then
  if ! getent passwd '107' >/dev/null; then
    useradd -r -u '107' -g 'qemu' -G 'kvm' -d '/' -s '/sbin/nologin' -c 'qemu user' 'qemu' || :
  else
    useradd -r -g 'qemu' -G 'kvm' -d '/' -s '/sbin/nologin' -c 'qemu user' 'qemu' || :
  fi
fi
exit 0
        %endif

%posttrans daemon-driver-qemu
%libvirt_sysconfig_posttrans virtqemud
%libvirt_systemd_unix_posttrans virtqemud

%preun daemon-driver-qemu
%libvirt_systemd_unix_preun virtqemud
    %endif

    %if %{with_lxc}
%pre daemon-driver-lxc
%libvirt_sysconfig_pre virtlxcd
%libvirt_systemd_unix_pre virtlxcd

%posttrans daemon-driver-lxc
%libvirt_sysconfig_posttrans virtlxcd
%libvirt_systemd_unix_posttrans virtlxcd

%preun daemon-driver-lxc
%libvirt_systemd_unix_preun virtlxcd
    %endif

    %if %{with_vbox}
%pre daemon-driver-vbox
%libvirt_sysconfig_pre virtvboxd
%libvirt_systemd_unix_pre virtvboxd

%posttrans daemon-driver-vbox
%libvirt_sysconfig_posttrans virtvboxd
%libvirt_systemd_unix_posttrans virtvboxd

%preun daemon-driver-vbox
%libvirt_systemd_unix_preun virtvboxd
    %endif

    %if %{with_libxl}
%pre daemon-driver-libxl
%libvirt_sysconfig_pre virtxend
%libvirt_systemd_unix_pre virtxend

%posttrans daemon-driver-libxl
%libvirt_sysconfig_posttrans virtxend
%libvirt_systemd_unix_posttrans virtxend

%preun daemon-driver-libxl
%libvirt_systemd_unix_preun virtxend
    %endif

    %if %{with_ch}
%pre daemon-driver-ch
%libvirt_sysconfig_pre virtchd
%libvirt_systemd_unix_pre virtchd

%posttrans daemon-driver-ch
%libvirt_sysconfig_posttrans virtchd
%libvirt_systemd_unix_posttrans virtchd

%preun daemon-driver-ch
%libvirt_systemd_unix_preun virtchd
    %endif

%pre daemon-config-network
%libvirt_systemd_config_pre libvirtd
%libvirt_systemd_config_pre virtnetworkd

%post daemon-config-network
if test $1 -eq 1 && test ! -f %{_sysconfdir}/libvirt/qemu/networks/default.xml ; then
    # see if the network used by default network creates a conflict,
    # and try to resolve it
    # NB: 192.168.122.0/24 is used in the default.xml template file;
    # do not modify any of those values here without also modifying
    # them in the template.
    orig_sub=122
    sub=${orig_sub}
    nl='
'
    routes="${nl}$(ip route show | cut -d' ' -f1)${nl}"
    case ${routes} in
      *"${nl}192.168.${orig_sub}.0/24${nl}"*)
        # there was a match, so we need to look for an unused subnet
        for new_sub in $(seq 124 254); do
          case ${routes} in
          *"${nl}192.168.${new_sub}.0/24${nl}"*)
            ;;
          *)
            sub=$new_sub
            break;
            ;;
          esac
        done
        ;;
      *)
        ;;
    esac

    sed -e "s/${orig_sub}/${sub}/g" \
         < %{_datadir}/libvirt/networks/default.xml \
         > %{_sysconfdir}/libvirt/qemu/networks/default.xml
    ln -s ../default.xml %{_sysconfdir}/libvirt/qemu/networks/autostart/default.xml
    # libvirt saves this file with mode 0600
    chmod 0600 %{_sysconfdir}/libvirt/qemu/networks/default.xml
fi

%posttrans daemon-config-network
%libvirt_systemd_config_posttrans libvirtd
%libvirt_systemd_config_posttrans virtnetworkd

%pre daemon-config-nwfilter
%libvirt_systemd_config_pre libvirtd
%libvirt_systemd_config_pre virtnwfilterd

%post daemon-config-nwfilter
for datadir_file in %{_datadir}/libvirt/nwfilter/*.xml; do
  sysconfdir_file=%{_sysconfdir}/libvirt/nwfilter/$(basename "$datadir_file")
  if [ ! -f "$sysconfdir_file" ]; then
    # libvirt saves these files with mode 600
    install -m 0600 "$datadir_file" "$sysconfdir_file"
  fi
done

%posttrans daemon-config-nwfilter
%libvirt_systemd_config_posttrans libvirtd
%libvirt_systemd_config_posttrans virtnwfilterd

    %if %{with_lxc}
%pre login-shell
        %if %{with_account_add}
getent group virtlogin >/dev/null || groupadd -r virtlogin
exit 0
        %endif
    %endif
%endif

%if %{with_native}
%files

%files docs
%doc AUTHORS.rst NEWS.rst README.rst
%doc libvirt-docs/*

%files daemon
%{_unitdir}/libvirtd.service
%{_unitdir}/libvirtd.socket
%{_unitdir}/libvirtd-ro.socket
%{_unitdir}/libvirtd-admin.socket
%{_unitdir}/libvirtd-tcp.socket
%{_unitdir}/libvirtd-tls.socket
%config(noreplace) %{_sysconfdir}/libvirt/libvirtd.conf
%config(noreplace) %{_prefix}/lib/sysctl.d/60-libvirtd.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/libvirtd
%dir %{_datadir}/augeas/lenses
%{_datadir}/augeas/lenses/libvirtd.aug
%dir %{_datadir}/augeas/lenses/tests
%{_datadir}/augeas/lenses/tests/test_libvirtd.aug
%attr(0755, root, root) %{_sbindir}/libvirtd
%{_mandir}/man8/libvirtd.8*

%files daemon-common
%{_unitdir}/virt-guest-shutdown.target
%{_unitdir}/libvirt-guests.service
%config(noreplace) %{_sysconfdir}/sasl2/libvirt.conf
%dir %{_datadir}/libvirt/
%ghost %dir %{_rundir}/libvirt/
%ghost %dir %attr(0700, root, root) %{_rundir}/libvirt/common/
%dir %attr(0755, root, root) %{_localstatedir}/lib/libvirt/
%dir %attr(0711, root, root) %{_localstatedir}/lib/libvirt/images/
%dir %attr(0711, root, root) %{_localstatedir}/lib/libvirt/filesystems/
%dir %attr(0711, root, root) %{_localstatedir}/lib/libvirt/boot/
%dir %attr(0711, root, root) %{_localstatedir}/cache/libvirt/
%dir %attr(0755, root, root) %{_libdir}/libvirt/
%dir %attr(0755, root, root) %{_libdir}/libvirt/connection-driver/
%dir %attr(0755, root, root) %{_libdir}/libvirt/storage-backend/
%dir %attr(0755, root, root) %{_libdir}/libvirt/storage-file/
%dir %attr(0755, root, root) %{_libdir}/libvirt/lock-driver/
%{_datadir}/polkit-1/actions/org.libvirt.unix.policy
%{_datadir}/polkit-1/actions/org.libvirt.api.policy
%{_datadir}/polkit-1/rules.d/50-libvirt.rules
%{_sysusersdir}/libvirt.conf
%dir %attr(0700, root, root) %{_localstatedir}/log/libvirt/
%attr(0755, root, root) %{_libexecdir}/libvirt_iohelper
%attr(0755, root, root) %{_bindir}/virt-ssh-helper
%attr(0755, root, root) %{_libexecdir}/libvirt-guests.sh
%{_mandir}/man1/virt-admin.1*
%{_mandir}/man1/virt-host-validate.1*
%{_mandir}/man8/virt-ssh-helper.8*
%{_mandir}/man8/libvirt-guests.8*
%{_bindir}/virt-host-validate
%{_bindir}/virt-admin
%{_datadir}/bash-completion/completions/virt-admin

%files daemon-lock
%{_unitdir}/virtlockd.service
%{_unitdir}/virtlockd.socket
%{_unitdir}/virtlockd-admin.socket
%config(noreplace) %{_sysconfdir}/libvirt/virtlockd.conf
%{_datadir}/augeas/lenses/virtlockd.aug
%{_datadir}/augeas/lenses/tests/test_virtlockd.aug
%{_datadir}/augeas/lenses/libvirt_lockd.aug
    %if %{with_qemu}
%{_datadir}/augeas/lenses/tests/test_libvirt_lockd.aug
    %endif
%attr(0755, root, root) %{_sbindir}/virtlockd
%{_mandir}/man8/virtlockd.8*

%files daemon-plugin-lockd
%attr(0755, root, root) %{_libdir}/libvirt/lock-driver/lockd.so

%files daemon-log
%{_unitdir}/virtlogd.service
%{_unitdir}/virtlogd.socket
%{_unitdir}/virtlogd-admin.socket
%config(noreplace) %{_sysconfdir}/libvirt/virtlogd.conf
%{_datadir}/augeas/lenses/virtlogd.aug
%{_datadir}/augeas/lenses/tests/test_virtlogd.aug
%attr(0755, root, root) %{_sbindir}/virtlogd
%{_mandir}/man8/virtlogd.8*

%files daemon-proxy
%{_unitdir}/virtproxyd.service
%{_unitdir}/virtproxyd.socket
%{_unitdir}/virtproxyd-ro.socket
%{_unitdir}/virtproxyd-admin.socket
%{_unitdir}/virtproxyd-tcp.socket
%{_unitdir}/virtproxyd-tls.socket
%config(noreplace) %{_sysconfdir}/libvirt/virtproxyd.conf
%{_datadir}/augeas/lenses/virtproxyd.aug
%{_datadir}/augeas/lenses/tests/test_virtproxyd.aug
%attr(0755, root, root) %{_sbindir}/virtproxyd
%{_mandir}/man8/virtproxyd.8*

%files daemon-config-network
%dir %{_datadir}/libvirt/networks/
%{_datadir}/libvirt/networks/default.xml
%ghost %{_sysconfdir}/libvirt/qemu/networks/default.xml
%ghost %{_sysconfdir}/libvirt/qemu/networks/autostart/default.xml

%files daemon-config-nwfilter
%dir %{_datadir}/libvirt/nwfilter/
%{_datadir}/libvirt/nwfilter/*.xml
%ghost %{_sysconfdir}/libvirt/nwfilter/*.xml

%files daemon-driver-interface
%config(noreplace) %{_sysconfdir}/libvirt/virtinterfaced.conf
%{_datadir}/augeas/lenses/virtinterfaced.aug
%{_datadir}/augeas/lenses/tests/test_virtinterfaced.aug
%{_unitdir}/virtinterfaced.service
%{_unitdir}/virtinterfaced.socket
%{_unitdir}/virtinterfaced-ro.socket
%{_unitdir}/virtinterfaced-admin.socket
%attr(0755, root, root) %{_sbindir}/virtinterfaced
%ghost %dir %attr(0700, root, root) %{_rundir}/libvirt/interface/
%{_libdir}/libvirt/connection-driver/libvirt_driver_interface.so
%{_mandir}/man8/virtinterfaced.8*

%files daemon-driver-network
%config(noreplace) %{_sysconfdir}/libvirt/virtnetworkd.conf
%{_datadir}/augeas/lenses/virtnetworkd.aug
%{_datadir}/augeas/lenses/tests/test_virtnetworkd.aug
%config(noreplace) %{_sysconfdir}/libvirt/network.conf
%{_datadir}/augeas/lenses/libvirtd_network.aug
%{_datadir}/augeas/lenses/tests/test_libvirtd_network.aug
%{_unitdir}/virtnetworkd.service
%{_unitdir}/virtnetworkd.socket
%{_unitdir}/virtnetworkd-ro.socket
%{_unitdir}/virtnetworkd-admin.socket
%attr(0755, root, root) %{_sbindir}/virtnetworkd
%dir %attr(0700, root, root) %{_sysconfdir}/libvirt/qemu/
%dir %attr(0700, root, root) %{_sysconfdir}/libvirt/qemu/networks/
%dir %attr(0700, root, root) %{_sysconfdir}/libvirt/qemu/networks/autostart
%ghost %dir %{_rundir}/libvirt/network/
%dir %attr(0700, root, root) %{_localstatedir}/lib/libvirt/network/
%dir %attr(0755, root, root) %{_localstatedir}/lib/libvirt/dnsmasq/
%attr(0755, root, root) %{_libexecdir}/libvirt_leaseshelper
%{_libdir}/libvirt/connection-driver/libvirt_driver_network.so
%{_mandir}/man8/virtnetworkd.8*
    %if %{with_firewalld_zone}
%{_prefix}/lib/firewalld/zones/libvirt.xml
%{_prefix}/lib/firewalld/zones/libvirt-routed.xml
%{_prefix}/lib/firewalld/policies/libvirt-routed-in.xml
%{_prefix}/lib/firewalld/policies/libvirt-routed-out.xml
%{_prefix}/lib/firewalld/policies/libvirt-to-host.xml
    %endif

%files daemon-driver-nodedev
%config(noreplace) %{_sysconfdir}/libvirt/virtnodedevd.conf
%{_datadir}/augeas/lenses/virtnodedevd.aug
%{_datadir}/augeas/lenses/tests/test_virtnodedevd.aug
%{_unitdir}/virtnodedevd.service
%{_unitdir}/virtnodedevd.socket
%{_unitdir}/virtnodedevd-ro.socket
%{_unitdir}/virtnodedevd-admin.socket
%attr(0755, root, root) %{_sbindir}/virtnodedevd
%ghost %dir %attr(0700, root, root) %{_rundir}/libvirt/nodedev/
%{_libdir}/libvirt/connection-driver/libvirt_driver_nodedev.so
%{_mandir}/man8/virtnodedevd.8*

%files daemon-driver-nwfilter
%config(noreplace) %{_sysconfdir}/libvirt/virtnwfilterd.conf
%{_datadir}/augeas/lenses/virtnwfilterd.aug
%{_datadir}/augeas/lenses/tests/test_virtnwfilterd.aug
%{_unitdir}/virtnwfilterd.service
%{_unitdir}/virtnwfilterd.socket
%{_unitdir}/virtnwfilterd-ro.socket
%{_unitdir}/virtnwfilterd-admin.socket
%attr(0755, root, root) %{_sbindir}/virtnwfilterd
%dir %attr(0700, root, root) %{_sysconfdir}/libvirt/nwfilter/
%ghost %dir %{_rundir}/libvirt/network/
%ghost %dir %attr(0700, root, root) %{_rundir}/libvirt/nwfilter-binding/
%ghost %dir %attr(0700, root, root) %{_rundir}/libvirt/nwfilter/
%{_libdir}/libvirt/connection-driver/libvirt_driver_nwfilter.so
%{_mandir}/man8/virtnwfilterd.8*

%files daemon-driver-secret
%config(noreplace) %{_sysconfdir}/libvirt/virtsecretd.conf
%{_datadir}/augeas/lenses/virtsecretd.aug
%{_datadir}/augeas/lenses/tests/test_virtsecretd.aug
%{_unitdir}/virtsecretd.service
%{_unitdir}/virtsecretd.socket
%{_unitdir}/virtsecretd-ro.socket
%{_unitdir}/virtsecretd-admin.socket
%attr(0755, root, root) %{_sbindir}/virtsecretd
%dir %attr(0700, root, root) %{_sysconfdir}/libvirt/secrets/
%ghost %dir %attr(0700, root, root) %{_rundir}/libvirt/secrets/
%{_libdir}/libvirt/connection-driver/libvirt_driver_secret.so
%{_mandir}/man8/virtsecretd.8*

%files daemon-driver-storage

%files daemon-driver-storage-core
%config(noreplace) %{_sysconfdir}/libvirt/virtstoraged.conf
%{_datadir}/augeas/lenses/virtstoraged.aug
%{_datadir}/augeas/lenses/tests/test_virtstoraged.aug
%{_unitdir}/virtstoraged.service
%{_unitdir}/virtstoraged.socket
%{_unitdir}/virtstoraged-ro.socket
%{_unitdir}/virtstoraged-admin.socket
%attr(0755, root, root) %{_sbindir}/virtstoraged
%attr(0755, root, root) %{_libexecdir}/libvirt_parthelper
%dir %attr(0700, root, root) %{_sysconfdir}/libvirt/storage/
%dir %attr(0700, root, root) %{_sysconfdir}/libvirt/storage/autostart/
%ghost %dir %{_rundir}/libvirt/storage/
%{_libdir}/libvirt/connection-driver/libvirt_driver_storage.so
%{_libdir}/libvirt/storage-backend/libvirt_storage_backend_fs.so
%{_mandir}/man8/virtstoraged.8*

%files daemon-driver-storage-disk
%{_libdir}/libvirt/storage-backend/libvirt_storage_backend_disk.so

%files daemon-driver-storage-logical
%{_libdir}/libvirt/storage-backend/libvirt_storage_backend_logical.so

%files daemon-driver-storage-scsi
%{_libdir}/libvirt/storage-backend/libvirt_storage_backend_scsi.so

%files daemon-driver-storage-iscsi
%{_libdir}/libvirt/storage-backend/libvirt_storage_backend_iscsi.so

    %if %{with_storage_iscsi_direct}
%files daemon-driver-storage-iscsi-direct
%{_libdir}/libvirt/storage-backend/libvirt_storage_backend_iscsi-direct.so
    %endif

%files daemon-driver-storage-mpath
%{_libdir}/libvirt/storage-backend/libvirt_storage_backend_mpath.so

    %if %{with_storage_gluster}
%files daemon-driver-storage-gluster
%{_libdir}/libvirt/storage-backend/libvirt_storage_backend_gluster.so
%{_libdir}/libvirt/storage-file/libvirt_storage_file_gluster.so
    %endif

    %if %{with_storage_rbd}
%files daemon-driver-storage-rbd
%{_libdir}/libvirt/storage-backend/libvirt_storage_backend_rbd.so
    %endif

    %if %{with_storage_zfs}
%files daemon-driver-storage-zfs
%{_libdir}/libvirt/storage-backend/libvirt_storage_backend_zfs.so
    %endif

    %if %{with_qemu}
%files daemon-driver-qemu
%config(noreplace) %{_sysconfdir}/libvirt/virtqemud.conf
%{_datadir}/augeas/lenses/virtqemud.aug
%{_datadir}/augeas/lenses/tests/test_virtqemud.aug
%{_unitdir}/virtqemud.service
%{_unitdir}/virtqemud.socket
%{_unitdir}/virtqemud-ro.socket
%{_unitdir}/virtqemud-admin.socket
%attr(0755, root, root) %{_sbindir}/virtqemud
%dir %attr(0700, root, root) %{_sysconfdir}/libvirt/qemu/
%dir %attr(0700, root, root) %{_sysconfdir}/libvirt/qemu/autostart/
%dir %attr(0700, root, root) %{_localstatedir}/log/libvirt/qemu/
%config(noreplace) %{_sysconfdir}/libvirt/qemu.conf
%config(noreplace) %{_sysconfdir}/libvirt/qemu-lockd.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/libvirtd.qemu
%ghost %dir %attr(0755, %{qemu_user}, %{qemu_group}) %{_rundir}/libvirt/qemu/
%ghost %dir %attr(0770, %{qemu_user}, %{qemu_group}) %{_rundir}/libvirt/qemu/dbus/
%ghost %dir %attr(0755, %{qemu_user}, %{qemu_group}) %{_rundir}/libvirt/qemu/passt/
%ghost %dir %attr(0755, %{qemu_user}, %{qemu_group}) %{_rundir}/libvirt/qemu/slirp/
%ghost %dir %attr(0770, %{qemu_user}, %{qemu_group}) %{_rundir}/libvirt/qemu/swtpm/
%dir %attr(0751, %{qemu_user}, %{qemu_group}) %{_localstatedir}/lib/libvirt/qemu/
%dir %attr(0751, %{qemu_user}, %{qemu_group}) %{_localstatedir}/lib/libvirt/qemu/checkpoint/
%dir %attr(0751, %{qemu_user}, %{qemu_group}) %{_localstatedir}/lib/libvirt/qemu/dump/
%dir %attr(0751, %{qemu_user}, %{qemu_group}) %{_localstatedir}/lib/libvirt/qemu/nvram/
%dir %attr(0751, %{qemu_user}, %{qemu_group}) %{_localstatedir}/lib/libvirt/qemu/ram/
%dir %attr(0751, %{qemu_user}, %{qemu_group}) %{_localstatedir}/lib/libvirt/qemu/save/
%dir %attr(0751, %{qemu_user}, %{qemu_group}) %{_localstatedir}/lib/libvirt/qemu/snapshot/
%dir %attr(0750, root, root) %{_localstatedir}/cache/libvirt/qemu/
%{_datadir}/augeas/lenses/libvirtd_qemu.aug
%{_datadir}/augeas/lenses/tests/test_libvirtd_qemu.aug
%{_libdir}/libvirt/connection-driver/libvirt_driver_qemu.so
%dir %attr(0711, root, root) %{_localstatedir}/lib/libvirt/swtpm/
%dir %attr(0730, tss, tss) %{_localstatedir}/log/swtpm/libvirt/qemu/
%{_bindir}/virt-qemu-run
%{_mandir}/man1/virt-qemu-run.1*
%{_mandir}/man8/virtqemud.8*
%{_sysusersdir}/libvirt-qemu.conf
    %endif

    %if %{with_lxc}
%files daemon-driver-lxc
%config(noreplace) %{_sysconfdir}/libvirt/virtlxcd.conf
%{_datadir}/augeas/lenses/virtlxcd.aug
%{_datadir}/augeas/lenses/tests/test_virtlxcd.aug
%{_unitdir}/virtlxcd.service
%{_unitdir}/virtlxcd.socket
%{_unitdir}/virtlxcd-ro.socket
%{_unitdir}/virtlxcd-admin.socket
%attr(0755, root, root) %{_sbindir}/virtlxcd
%dir %attr(0700, root, root) %{_localstatedir}/log/libvirt/lxc/
%dir %attr(0700, root, root) %{_sysconfdir}/libvirt/lxc/
%dir %attr(0700, root, root) %{_sysconfdir}/libvirt/lxc/autostart/
%config(noreplace) %{_sysconfdir}/libvirt/lxc.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/libvirtd.lxc
%ghost %dir %{_rundir}/libvirt/lxc/
%dir %attr(0700, root, root) %{_localstatedir}/lib/libvirt/lxc/
%{_datadir}/augeas/lenses/libvirtd_lxc.aug
%{_datadir}/augeas/lenses/tests/test_libvirtd_lxc.aug
%attr(0755, root, root) %{_libexecdir}/libvirt_lxc
%{_libdir}/libvirt/connection-driver/libvirt_driver_lxc.so
%{_mandir}/man8/virtlxcd.8*
    %endif

    %if %{with_libxl}
%files daemon-driver-libxl
%config(noreplace) %{_sysconfdir}/libvirt/virtxend.conf
%{_datadir}/augeas/lenses/virtxend.aug
%{_datadir}/augeas/lenses/tests/test_virtxend.aug
%{_unitdir}/virtxend.service
%{_unitdir}/virtxend.socket
%{_unitdir}/virtxend-ro.socket
%{_unitdir}/virtxend-admin.socket
%attr(0755, root, root) %{_sbindir}/virtxend
%config(noreplace) %{_sysconfdir}/libvirt/libxl.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/libvirtd.libxl
%config(noreplace) %{_sysconfdir}/libvirt/libxl-lockd.conf
%dir %attr(0700, root, root) %{_sysconfdir}/libvirt/libxl/
%dir %attr(0700, root, root) %{_sysconfdir}/libvirt/libxl/autostart/
%{_datadir}/augeas/lenses/libvirtd_libxl.aug
%{_datadir}/augeas/lenses/tests/test_libvirtd_libxl.aug
%dir %attr(0700, root, root) %{_localstatedir}/log/libvirt/libxl/
%ghost %dir %{_rundir}/libvirt/libxl/
%dir %attr(0700, root, root) %{_localstatedir}/lib/libvirt/libxl/
%dir %attr(0700, root, root) %{_localstatedir}/lib/libvirt/libxl/channel/
%dir %attr(0700, root, root) %{_localstatedir}/lib/libvirt/libxl/channel/target/
%dir %attr(0700, root, root) %{_localstatedir}/lib/libvirt/libxl/dump/
%dir %attr(0700, root, root) %{_localstatedir}/lib/libvirt/libxl/save/
%{_libdir}/libvirt/connection-driver/libvirt_driver_libxl.so
%{_mandir}/man8/virtxend.8*
    %endif

    %if %{with_vbox}
%files daemon-driver-vbox
%config(noreplace) %{_sysconfdir}/libvirt/virtvboxd.conf
%{_datadir}/augeas/lenses/virtvboxd.aug
%{_datadir}/augeas/lenses/tests/test_virtvboxd.aug
%{_unitdir}/virtvboxd.service
%{_unitdir}/virtvboxd.socket
%{_unitdir}/virtvboxd-ro.socket
%{_unitdir}/virtvboxd-admin.socket
%attr(0755, root, root) %{_sbindir}/virtvboxd
%{_libdir}/libvirt/connection-driver/libvirt_driver_vbox.so
%{_mandir}/man8/virtvboxd.8*
    %endif

    %if %{with_qemu_tcg}
%files daemon-qemu
    %endif

    %if %{with_qemu_kvm}
%files daemon-kvm
    %endif

    %if %{with_lxc}
%files daemon-lxc
    %endif

    %if %{with_libxl}
%files daemon-xen
    %endif

    %if %{with_vbox}
%files daemon-vbox
    %endif

    %if %{with_sanlock}
%files daemon-plugin-sanlock
        %if %{with_qemu}
%config(noreplace) %{_sysconfdir}/libvirt/qemu-sanlock.conf
        %endif
        %if %{with_libxl}
%config(noreplace) %{_sysconfdir}/libvirt/libxl-sanlock.conf
        %endif
%attr(0755, root, root) %{_libdir}/libvirt/lock-driver/sanlock.so
%{_datadir}/augeas/lenses/libvirt_sanlock.aug
%{_datadir}/augeas/lenses/tests/test_libvirt_sanlock.aug
%dir %attr(0770, root, sanlock) %{_localstatedir}/lib/libvirt/sanlock
%{_sbindir}/virt-sanlock-cleanup
%{_mandir}/man8/virt-sanlock-cleanup.8*
%attr(0755, root, root) %{_libexecdir}/libvirt_sanlock_helper
    %endif

    %if %{with_ch}
%files daemon-driver-ch
%attr(0755, root, root) %{_sbindir}/virtchd
%config(noreplace) %{_sysconfdir}/libvirt/virtchd.conf
%{_datadir}/augeas/lenses/virtchd.aug
%{_datadir}/augeas/lenses/tests/test_virtchd.aug
%{_unitdir}/virtchd-admin.socket
%{_unitdir}/virtchd-ro.socket
%{_unitdir}/virtchd.service
%{_unitdir}/virtchd.socket
%{_libdir}/libvirt/connection-driver/libvirt_driver_ch.so
%config(noreplace) %{_sysconfdir}/libvirt/ch.conf
%{_datadir}/augeas/lenses/libvirtd_ch.aug
%{_datadir}/augeas/lenses/tests/test_libvirtd_ch.aug
    %endif

%files client
%{_mandir}/man1/virsh.1*
%{_mandir}/man1/virt-xml-validate.1*
%{_mandir}/man1/virt-pki-query-dn.1*
%{_mandir}/man1/virt-pki-validate.1*
%{_mandir}/man7/virkey*.7*
%{_bindir}/virsh
%{_bindir}/virt-xml-validate
%{_bindir}/virt-pki-query-dn
%{_bindir}/virt-pki-validate
%{_datadir}/bash-completion/completions/virsh

    %if %{with_qemu}
%files client-qemu
%{_mandir}/man1/virt-qemu-qmp-proxy.1*
%{_mandir}/man1/virt-qemu-sev-validate.1*
%{_bindir}/virt-qemu-qmp-proxy
%{_bindir}/virt-qemu-sev-validate
    %endif

%files libs -f %{name}.lang
%license COPYING COPYING.LESSER
%dir %attr(0700, root, root) %{_sysconfdir}/libvirt/
%config(noreplace) %{_sysconfdir}/libvirt/libvirt.conf
%config(noreplace) %{_sysconfdir}/libvirt/libvirt-admin.conf
%{_libdir}/libvirt.so.*
%{_libdir}/libvirt-qemu.so.*
%{_libdir}/libvirt-lxc.so.*
%{_libdir}/libvirt-admin.so.*
%dir %{_datadir}/libvirt/
%{_datadir}/libvirt/test-screenshot.png
%dir %{_datadir}/libvirt/schemas/
%{_datadir}/libvirt/schemas/*.rng
%dir %{_datadir}/systemtap/tapset/
%{_datadir}/systemtap/tapset/libvirt_probes*.stp
%{_datadir}/systemtap/tapset/libvirt_functions.stp
    %if %{with_qemu}
%{_datadir}/systemtap/tapset/libvirt_qemu_probes*.stp
    %endif
%dir %{_datadir}/libvirt/cpu_map
%{_datadir}/libvirt/cpu_map/*.xml

    %if %{with_wireshark}
%files wireshark
%{wireshark_plugindir}/libvirt.so
    %endif

%files nss
%{_libdir}/libnss_libvirt.so.2
%{_libdir}/libnss_libvirt_guest.so.2

%files ssh-proxy
%config(noreplace) %{_sysconfdir}/ssh/ssh_config.d/30-libvirt-ssh-proxy.conf
%{_libexecdir}/libvirt-ssh-proxy

    %if %{with_lxc}
%files login-shell
%attr(4750, root, virtlogin) %{_bindir}/virt-login-shell
%{_libexecdir}/virt-login-shell-helper
%config(noreplace) %{_sysconfdir}/libvirt/virt-login-shell.conf
%{_sysusersdir}/libvirt-login-shell.conf
%{_mandir}/man1/virt-login-shell.1*
    %endif

%files devel
%{_libdir}/libvirt.so
%{_libdir}/libvirt-admin.so
%{_libdir}/libvirt-qemu.so
%{_libdir}/libvirt-lxc.so
%dir %{_includedir}/libvirt
%{_includedir}/libvirt/virterror.h
%{_includedir}/libvirt/libvirt.h
%{_includedir}/libvirt/libvirt-admin.h
%{_includedir}/libvirt/libvirt-common.h
%{_includedir}/libvirt/libvirt-domain.h
%{_includedir}/libvirt/libvirt-domain-checkpoint.h
%{_includedir}/libvirt/libvirt-domain-snapshot.h
%{_includedir}/libvirt/libvirt-event.h
%{_includedir}/libvirt/libvirt-host.h
%{_includedir}/libvirt/libvirt-interface.h
%{_includedir}/libvirt/libvirt-network.h
%{_includedir}/libvirt/libvirt-nodedev.h
%{_includedir}/libvirt/libvirt-nwfilter.h
%{_includedir}/libvirt/libvirt-secret.h
%{_includedir}/libvirt/libvirt-storage.h
%{_includedir}/libvirt/libvirt-stream.h
%{_includedir}/libvirt/libvirt-qemu.h
%{_includedir}/libvirt/libvirt-lxc.h
%{_libdir}/pkgconfig/libvirt.pc
%{_libdir}/pkgconfig/libvirt-admin.pc
%{_libdir}/pkgconfig/libvirt-qemu.pc
%{_libdir}/pkgconfig/libvirt-lxc.pc
%dir %{_datadir}/libvirt/api/
%{_datadir}/libvirt/api/libvirt-api.xml
%{_datadir}/libvirt/api/libvirt-admin-api.xml
%{_datadir}/libvirt/api/libvirt-qemu-api.xml
%{_datadir}/libvirt/api/libvirt-lxc-api.xml
%endif

%if %{with_mingw32}
%files -n mingw32-libvirt -f mingw32-libvirt.lang
%dir %{mingw32_sysconfdir}/libvirt/
%config(noreplace) %{mingw32_sysconfdir}/libvirt/libvirt.conf
%config(noreplace) %{mingw32_sysconfdir}/libvirt/libvirt-admin.conf
%{mingw32_bindir}/libvirt-0.dll
%{mingw32_bindir}/virsh.exe
%{mingw32_bindir}/virt-admin.exe
%{mingw32_bindir}/virt-xml-validate
%{mingw32_bindir}/virt-pki-query-dn.exe
%{mingw32_bindir}/virt-pki-validate.exe
%{mingw32_bindir}/libvirt-lxc-0.dll
%{mingw32_bindir}/libvirt-qemu-0.dll
%{mingw32_bindir}/libvirt-admin-0.dll
%{mingw32_libdir}/libvirt.dll.a
%{mingw32_libdir}/pkgconfig/libvirt.pc
%{mingw32_libdir}/pkgconfig/libvirt-qemu.pc
%{mingw32_libdir}/pkgconfig/libvirt-lxc.pc
%{mingw32_libdir}/pkgconfig/libvirt-admin.pc
%{mingw32_libdir}/libvirt-lxc.dll.a
%{mingw32_libdir}/libvirt-qemu.dll.a
%{mingw32_libdir}/libvirt-admin.dll.a
%dir %{mingw32_datadir}/libvirt/
%dir %{mingw32_datadir}/libvirt/schemas/
%{mingw32_datadir}/libvirt/schemas/*.rng
%dir %{mingw32_datadir}/libvirt/api/
%{mingw32_datadir}/libvirt/api/libvirt-api.xml
%{mingw32_datadir}/libvirt/api/libvirt-lxc-api.xml
%{mingw32_datadir}/libvirt/api/libvirt-qemu-api.xml
%{mingw32_datadir}/libvirt/api/libvirt-admin-api.xml
%{mingw32_datadir}/libvirt/cpu_map/*.xml
%{mingw32_datadir}/libvirt/test-screenshot.png
%dir %{mingw32_includedir}/libvirt
%{mingw32_includedir}/libvirt/libvirt.h
%{mingw32_includedir}/libvirt/libvirt-common.h
%{mingw32_includedir}/libvirt/libvirt-domain.h
%{mingw32_includedir}/libvirt/libvirt-domain-checkpoint.h
%{mingw32_includedir}/libvirt/libvirt-domain-snapshot.h
%{mingw32_includedir}/libvirt/libvirt-event.h
%{mingw32_includedir}/libvirt/libvirt-host.h
%{mingw32_includedir}/libvirt/libvirt-interface.h
%{mingw32_includedir}/libvirt/libvirt-network.h
%{mingw32_includedir}/libvirt/libvirt-nodedev.h
%{mingw32_includedir}/libvirt/libvirt-nwfilter.h
%{mingw32_includedir}/libvirt/libvirt-secret.h
%{mingw32_includedir}/libvirt/libvirt-storage.h
%{mingw32_includedir}/libvirt/libvirt-stream.h
%{mingw32_includedir}/libvirt/virterror.h
%{mingw32_includedir}/libvirt/libvirt-lxc.h
%{mingw32_includedir}/libvirt/libvirt-qemu.h
%{mingw32_includedir}/libvirt/libvirt-admin.h
%{mingw32_mandir}/man1/virsh.1*
%{mingw32_mandir}/man1/virt-admin.1*
%{mingw32_mandir}/man1/virt-xml-validate.1*
%{mingw32_mandir}/man1/virt-pki-query-dn.1*
%{mingw32_mandir}/man1/virt-pki-validate.1*
%{mingw32_mandir}/man7/virkey*.7*
%endif

%if %{with_mingw64}
%files -n mingw64-libvirt -f mingw64-libvirt.lang
%dir %{mingw64_sysconfdir}/libvirt/
%config(noreplace) %{mingw64_sysconfdir}/libvirt/libvirt.conf
%config(noreplace) %{mingw64_sysconfdir}/libvirt/libvirt-admin.conf
%{mingw64_bindir}/libvirt-0.dll
%{mingw64_bindir}/virsh.exe
%{mingw64_bindir}/virt-admin.exe
%{mingw64_bindir}/virt-xml-validate
%{mingw64_bindir}/virt-pki-query-dn.exe
%{mingw64_bindir}/virt-pki-validate.exe
%{mingw64_bindir}/libvirt-lxc-0.dll
%{mingw64_bindir}/libvirt-qemu-0.dll
%{mingw64_bindir}/libvirt-admin-0.dll
%{mingw64_libdir}/libvirt.dll.a
%{mingw64_libdir}/pkgconfig/libvirt.pc
%{mingw64_libdir}/pkgconfig/libvirt-qemu.pc
%{mingw64_libdir}/pkgconfig/libvirt-lxc.pc
%{mingw64_libdir}/pkgconfig/libvirt-admin.pc
%{mingw64_libdir}/libvirt-lxc.dll.a
%{mingw64_libdir}/libvirt-qemu.dll.a
%{mingw64_libdir}/libvirt-admin.dll.a
%dir %{mingw64_datadir}/libvirt/
%dir %{mingw64_datadir}/libvirt/schemas/
%{mingw64_datadir}/libvirt/schemas/*.rng
%dir %{mingw64_datadir}/libvirt/api/
%{mingw64_datadir}/libvirt/api/libvirt-api.xml
%{mingw64_datadir}/libvirt/api/libvirt-lxc-api.xml
%{mingw64_datadir}/libvirt/api/libvirt-qemu-api.xml
%{mingw64_datadir}/libvirt/api/libvirt-admin-api.xml
%{mingw64_datadir}/libvirt/cpu_map/*.xml
%{mingw64_datadir}/libvirt/test-screenshot.png
%dir %{mingw64_includedir}/libvirt
%{mingw64_includedir}/libvirt/libvirt.h
%{mingw64_includedir}/libvirt/libvirt-common.h
%{mingw64_includedir}/libvirt/libvirt-domain.h
%{mingw64_includedir}/libvirt/libvirt-domain-checkpoint.h
%{mingw64_includedir}/libvirt/libvirt-domain-snapshot.h
%{mingw64_includedir}/libvirt/libvirt-event.h
%{mingw64_includedir}/libvirt/libvirt-host.h
%{mingw64_includedir}/libvirt/libvirt-interface.h
%{mingw64_includedir}/libvirt/libvirt-network.h
%{mingw64_includedir}/libvirt/libvirt-nodedev.h
%{mingw64_includedir}/libvirt/libvirt-nwfilter.h
%{mingw64_includedir}/libvirt/libvirt-secret.h
%{mingw64_includedir}/libvirt/libvirt-storage.h
%{mingw64_includedir}/libvirt/libvirt-stream.h
%{mingw64_includedir}/libvirt/virterror.h
%{mingw64_includedir}/libvirt/libvirt-lxc.h
%{mingw64_includedir}/libvirt/libvirt-qemu.h
%{mingw64_includedir}/libvirt/libvirt-admin.h
%{mingw64_mandir}/man1/virsh.1*
%{mingw64_mandir}/man1/virt-admin.1*
%{mingw64_mandir}/man1/virt-xml-validate.1*
%{mingw64_mandir}/man1/virt-pki-query-dn.1*
%{mingw64_mandir}/man1/virt-pki-validate.1*
%{mingw64_mandir}/man7/virkey*.7*
%endif

%changelog
* Thu Jan 29 2026 Jiri Denemark <jdenemar@redhat.com> - 11.10.0-4
- qemuSecurityMoveImageMetadata: Move seclabels only to virStorageSource of same type (RHEL-140624)
- qemuDomainSetThrottleGroup: Enforce non-zero 'groupname' string length (RHEL-144010)
- qemuDomainSetBlockIoTuneField: Move setting of 'group_name' out of the loop (RHEL-144010)
- qemuDomainSetThrottleGroup: Always honour thottle group name passed as argument (RHEL-144010)
- qemuDomainSetThrottleGroup: Don't put group name into the 'tunable' event twice (RHEL-144010)
- qemuSnapshotDiskHasBackingDisk: Avoid call of virStorageSourceIsSameLocation with NULL argument (RHEL-144090)
- qemuSnapshotUpdateBackingStore: Remove stale comment (RHEL-144090)
- qemuSnapshotDiskHasBackingDisk: Use proper 'max_depth' when calling 'virStorageSourceGetMetadata' (RHEL-144090)
- virDomainSnapshotDefAssignExternalNames: Improve error message (RHEL-144090)
- qemuSnapshotUpdateBackingStore: Retry as curent user if qemu-img fails (RHEL-144090)

* Tue Jan 13 2026 Jiri Denemark <jdenemar@redhat.com> - 11.10.0-3
- util: json: Increase JSON nesting limit when parsing to 300 (RHEL-135128)
- virjsontest: Add test for nesting depth (RHEL-135128)
- qemu_validate: Drop VIR_DOMAIN_HYPERV_SYNIC dependency on VIR_DOMAIN_HYPERV_VPINDEX (RHEL-138689)
- qemu_validate: Drop VIR_DOMAIN_HYPERV_STIMER dependency on VIR_DOMAIN_HYPERV_VPINDEX (RHEL-138689)
- esx_util: Introduce esxUtil_EscapeInventoryObject() (RHEL-134127)
- esx: URI encode inventory objects twice (RHEL-134127)

* Thu Dec 18 2025 Jiri Denemark <jdenemar@redhat.com> - 11.10.0-2
- qemu: tpm: Account for possible migration without actually sharing storage (RHEL-108915)
- tests: Test virFileIsSharedFSOverride (RHEL-135287)
- util: Fix race condition in virFileIsSharedFSType (RHEL-135287)
- util: Fix race condition in virFileIsSharedFSOverride (RHEL-135287)
- util: Rework virFileIsSharedFSOverride using virFileCheckParents (RHEL-135287)

* Tue Dec  2 2025 Jiri Denemark <jdenemar@redhat.com> - 11.10.0-1
- Rebased to libvirt-11.10.0 (RHEL-118197)
- The rebase also fixes the following bugs:
    RHEL-126090, RHEL-128107
- spec: Fix RPM build when %{fedora} is undefined (RHEL-118197)

* Tue Nov  4 2025 Jiri Denemark <jdenemar@redhat.com> - 11.9.0-1
- Rebased to libvirt-11.9.0 (RHEL-118197)
- The rebase also fixes the following bugs:
    RHEL-114003

* Wed Oct  1 2025 Jiri Denemark <jdenemar@redhat.com> - 11.8.0-1
- Rebased to libvirt-11.8.0 (RHEL-118197)
- The rebase also fixes the following bugs:
    RHEL-15693, RHEL-95397, RHEL-111609, RHEL-116847, RHEL-117774

* Mon Aug 18 2025 Jiri Denemark <jdenemar@redhat.com> - 10.10.0-15
- qemu: fix order of VNC TLS config entries (RHEL-106276)
- qemu: sanitize blank lines in config file (RHEL-106276)
- qemu: add ability to set TLS priority string with QEMU (RHEL-106276)

* Thu Jul 17 2025 Jiri Denemark <jdenemar@redhat.com> - 10.10.0-14
- qemu: introduce QEMU_CAPS_AMD_IOMMU (RHEL-50560)
- qemu: introduce QEMU_CAPS_PCI_ID (RHEL-50560)
- docs: formatdomain: document intel-only IOMMU attributes (RHEL-50560)
- qemu: add IOMMU model amd (RHEL-50560)
- conf: add passthrough and xtsup attributes for IOMMU (RHEL-50560)
- esx: Allow specifying different CA bundle for remote connections (RHEL-97440)

* Wed Jun 18 2025 Jiri Denemark <jdenemar@redhat.com> - 10.10.0-13
- qemuPrepareNVRAMFile: Fix NVRAM image conversion check (RHEL-97758)

* Wed Jun  4 2025 Jiri Denemark <jdenemar@redhat.com> - 10.10.0-12
- qemuMonitorJSONGetCPUModelExpansion: refactor parsing functions (RHEL-89415)
- qemu: parse deprecated-props from query-cpu-model-expansion response (RHEL-89415)
- qemu_capabilities: query deprecated features for host-model (RHEL-89415)
- libvirt-domain: introduce VIR_CONNECT_GET_DOMAIN_CAPABILITIES_DISABLE_DEPRECATED_FEATURES (RHEL-89415)
- qemu_capabilities: filter deprecated features if requested (RHEL-89415)
- virsh: add --disable-deprecated-features flag to domcapabilities (RHEL-89415)
- conf: add deprecated_features attribute (RHEL-89415)
- redhat: Restore hunks in tests/qemucapabilitiesdata/caps_10.0.0_s390x.* (RHEL-89415)

* Thu May 22 2025 Jiri Denemark <jdenemar@redhat.com> - 10.10.0-11
- Add load average information type into virDomainGetGuestInfo (RHEL-88447)
- qemu_agent: Add qemuAgentGetLoadAvg() (RHEL-88447)
- qemu: Add support for VIR_DOMAIN_GUEST_INFO_LOAD (RHEL-88447)
- virsh: Add support for VIR_DOMAIN_GUEST_INFO_LOAD (RHEL-88447)
- qemu_capabilities: Fetch caps for virtio-mem-ccw too (RHEL-87532)
- cpu_map: Add avx10* CPU features (RHEL-87796)
- cpu_map: Add GraniteRapids-v2 CPU model (RHEL-87796)
- cpu_map: Add sha512, sm3, and sm4 CPU features (RHEL-87796)
- virsh: Introduce new hypervisor-cpu-models command (RHEL-11435)
- qemu: remove nonsensical sanity check in processNetdevStreamDisconnectedEvent() (RHEL-80169)
- qemu: make processNetDevStreamDisconnectedEvent() reusable (RHEL-80169)
- qemu: respond to NETDEV_VHOST_USER_DISCONNECTED event (RHEL-80169)
- qemu: put vhost-user code that's special for passt in a helper function (RHEL-80169)
- qemu: make passt+vhostuser reconnect behave identically to passt+user (RHEL-80169)

* Thu Apr 17 2025 Jiri Denemark <jdenemar@redhat.com> - 10.10.0-10
- esxConnectListAllDomains: Don't propagate failure to lookup a single domain (RHEL-80606)
- conf: parse interface/source/@dev for all interface types (with backend type='passt') (RHEL-82539)
- libvirt-host: Clarify/fix description of the CPU frequency field (RHEL-86197)
- virNodeGetInfo: Improve description of the case when fake data is reported (RHEL-86197)
- manpages: virsh: Use disclaimer from 'virNodeGetInfo()' for 'virsh nodeinfo' (RHEL-86197)
- esx: Accept empty "path" URI component same way as "/" (RHEL-86459)
- qemu: Rename outgoingMigration parameter in various TPM functions (RHEL-86800)
- qemu: Properly propagate migration state to TPM cleanup code (RHEL-86800)
- qemuDomainBlockCopyCommon: Don't revoke access to file twice on failure (RHEL-7357)
- qemuxmlconftest: Drop s390-default-cpu-...ccw-virtio-2.7 test cases (RHEL-72976)
- tests: add capabilities for QEMU 10.0.0 on s390x (RHEL-72976)
- qemu: Do NOT autoadd NUMA node for s390 (RHEL-72976)
- qemu_command: Use qemuBuildVirtioDevProps() to build cmd line for virtio-mem and virtio-pmem (RHEL-72976)
- qemuxmlconftest: Introduce memory-hotplug-virtio-mem-pci-s390x.xml (RHEL-72976)
- qemu_caps: Introduce QEMU_CAPS_DEVICE_VIRTIO_MEM_CCW (RHEL-72976)
- qemu: Validate virtio-mem-ccw (RHEL-72976)
- qemu: Allow virtio-mem on CCW (RHEL-72976)
- qemuxmlconftest: Introduce memory-hotplug-virtio-mem-ccw-s390x.xml (RHEL-72976)
- qemu_domain_address: fix CCW virtio-mem hotplug (RHEL-72976)

* Wed Mar 26 2025 Jiri Denemark <jdenemar@redhat.com> - 10.10.0-9
- util: introduce object for holding a system inhibitor lock (RHEL-83064)
- src: convert drivers over to new virInhibitor APIs (RHEL-83064)
- rpc: remove logind support for virNetDaemon (RHEL-83064)
- util: fix off-by-1 in inhibitor constants (RHEL-83064)
- util: don't attempt to acquire logind inhibitor if not requested (RHEL-83064)
- network: Free inhibitor in networkStateCleanup() (RHEL-83064)
- conf: introduce support for multiple ACPI tables (RHEL-81041)
- src: validate permitted ACPI table types in libxl/qemu drivers (RHEL-81041)
- src: introduce 'raw' and 'rawset' ACPI table types (RHEL-81041)
- qemu: support 'raw' ACPI table type (RHEL-81041)
- libxl: support 'rawset' ACPI table type (RHEL-81041)
- conf: support MSDM ACPI table type (RHEL-81041)
- qemu: support MSDM ACPI table type (RHEL-81041)
- qemuxmlconftest: Include shared memory 'net-vhostuser' test cases (RHEL-84133)
- qemuValidateDomainDeviceDefNetwork: Require shared memory for all vhost-user interfaces (RHEL-84133)
- qemu: process: Remove un-updated 'qemuProcessStartWarnShmem' (RHEL-84133)

* Thu Mar 13 2025 Jiri Denemark <jdenemar@redhat.com> - 10.10.0-8
- remote: add sysusers file to create 'libvirt' group (RHEL-81749)
- qemu: Avoid crash in qemuDomainCheckCPU with unknown host CPU (RHEL-81747)
- qemu_snapshot: allow reverting to external disk only snapshot (RHEL-21549)
- qemu: snapshot: error out early when reverting snapshot for VM with non-file disk (RHEL-30971)

* Mon Feb 17 2025 Jiri Denemark <jdenemar@redhat.com> - 10.10.0-7
- qemu_migration: Refactor qemuMigrationSrcRestoreDomainState (RHEL-79168)
- qemu_migration: Do not automatically resume domain after I/O error (RHEL-79168)
- qemucapabilitiestest: Add data for the qemu-10.0 dev cycle on x86_64 (RHEL-79095)
- qemucapabilitiestest: Update 'caps_10.0.0_x86_64' to 'v9.2.0-1636-gffaf7f0376' (RHEL-79095)
- qemu: capabilies: Introduce QEMU_CAPS_BLOCKDEV_SET_ACTIVE (RHEL-79095)
- qemu: monitor: Add monitor backend for 'blockdev-set-active' (RHEL-79095)
- qemu: migration: Reactivate block nodes after migration if VM is left paused (RHEL-79095)
- conf: change virDomainHostdevInsert() to return void (RHEL-69455)
- qemu: fix qemu validation to forbid guest-side IP address for type='vdpa' (RHEL-69455)
- qemu: validate that model is virtio for vhostuser and vdpa interfaces in the same place (RHEL-69455)
- qemu: automatically set model type='virtio' for interface type='vhostuser' (RHEL-69455)
- qemu: do all vhostuser attribute validation in qemu driver (RHEL-69455)
- conf/qemu: make <source> element *almost* optional for type=vhostuser (RHEL-69455)
- qemu: use switch instead of if in qemuProcessPrepareDomainNetwork() (RHEL-69455)
- qemu: make qemuPasstCreateSocketPath() public (RHEL-69455)
- qemu: complete vhostuser + passt support (RHEL-69455)
- qemu: fail validation if a domain def has vhostuser/passt but no shared mem (RHEL-69455)
- docs: improve type='user' docs to higlight differences between SLIRP and passt (RHEL-69455)
- docs: document using passt backend with <interface type='vhostuser'> (RHEL-69455)
- utils: Canonicalize paths before comparing them (RHEL-79166)

* Fri Feb  7 2025 Jiri Denemark <jdenemar@redhat.com> - 10.10.0-6
- build: Bump minimum glib2 version to 2.66.0 (RHEL-77884)
- qemuProcessHandleIOError: Refactor to extract 'priv' instead of 'driver' (RHEL-77884)
- qemu: Handle quirks of 'device' field of BLOCK_IO_ERROR event in monitor code (RHEL-77884)
- qemu: Rename 'diskAlias' to 'device' in qemu IO error event handling (RHEL-77884)
- qemuProcessHandleIOError: Rename local variables (RHEL-77884)
- qemuMonitorJSONHandleIOError: Do not munge 'reason' field of IO error event (RHEL-77884)
- qemuProcessHandleIOError: Prefer lookup by node name (RHEL-77884)
- qemuMonitorJSONHandleIOError: Propagate new 'qom-path' field (RHEL-77884)
- virStorageSource: Add fields for storing last I/O error message (RHEL-77884)
- qemuProcessHandleIOError: Populate I/O error reason to virStorageSource (RHEL-77884)
- qemuProcessHandleIOError: Log IO errors in the VM log file (RHEL-77884)
- libxlDomainGetMessages: Add existing flags to 'virCheckFlags' (RHEL-77884)
- virDomainObjGetMessages: Refactor using GPtrArray (RHEL-77884)
- virDomainGetMessages: Introduce VIR_DOMAIN_MESSAGE_IOERRORS (RHEL-77884)
- include: libvirt-domain: Reword documentation for @reason of VIR_DOMAIN_EVENT_ID_IO_ERROR_REASON (RHEL-77884)
- include: libvirt-domain: Add 'message' @reason of VIR_DOMAIN_EVENT_ID_IO_ERROR_REASON (RHEL-77884)
- qemuSnapshotForEachQcow2: Don't initialize 'nrollback' (RHEL-73315)
- qemu: process: Export qemuPrepareNVRAM for use in snapshot code (RHEL-73315)
- qemu: snapshot: Ensure that NVRAM image exists when taking inactive internal snapshot (RHEL-73315)
- qemuxmlconftest: Allow testing of the 'writable' flag for passed FDs for disks (RHEL-37519)
- qemuxmlconftest: Add testing of FDs with 'writable' flag in 'disk-source-fd' (RHEL-37519)
- qemu: domain: Initialize FD passthrough for a virStorageSource before using it (RHEL-37519)

* Fri Jan 24 2025 Jiri Denemark <jdenemar@redhat.com> - 10.10.0-5
- qemu: allow migration of guest with mdev vGPU to VF vGPU (RHEL-68064)
- storage_file: Refuse qcow2 images with empty string as 'data_file' (RHEL-73504)
- virstoragetest: Add case for qcow2 image with empty string as 'data_file' (RHEL-73504)
- qemu: snapshot: delete disk image only if parent snapshot is external (RHEL-74041)
- storage_file: de-modularize the local file backend (RHEL-73507)
- libvirt.spec: Move ownership of 'storage-file' backends directory to gluster (RHEL-73507)
- qemu: re-use existing ActualNetDef for more interface types during update-device (RHEL-7036)
- tools: ssh-proxy: Check for domain status before parsing its CID (RHEL-75577)

* Thu Jan 16 2025 Jiri Denemark <jdenemar@redhat.com> - 10.10.0-4
- conf, docs: Add support for direct and extended tlbflush features (RHEL-7122)
- qemu: Add support for direct and extended tlbflush features (RHEL-7122)
- conf: refactor hyperv features formatting (RHEL-7122)
- conf: Adjust hyperv tlbflush formatting (RHEL-7122)
- qemu_migration: Do not consider post-copy active in postcopy-recover (RHEL-73085)

* Fri Dec 20 2024 Jiri Denemark <jdenemar@redhat.com> - 10.10.0-3
- qemu: Enable I/O APIC even more frequently (RHEL-65844)

* Tue Dec 17 2024 Jiri Denemark <jdenemar@redhat.com> - 10.10.0-2
- util: Fix typo in virNetDevOpenvswitchInterfaceSetQos (RHEL-69938)
- qemu: tpm: do not update profile name for transient domains (RHEL-71072)
- qemu: Enable I/O APIC if needed (RHEL-65844)
- cpu_map: Sort data files in meson.build (RHEL-70052)
- sync_qemu_models_i386: Update meson.build (RHEL-70052)
- sync_qemu_models_i386: Generate missing -v1 variants (RHEL-70052)
- cpu_map: Add 486-v1 CPU model (RHEL-70052)
- cpu_map: Add pentium-v1 CPU model (RHEL-70052)
- cpu_map: Add pentium2-v1 CPU model (RHEL-70052)
- cpu_map: Add pentium3-v1 CPU model (RHEL-70052)
- cpu_map: Add coreduo-v1 CPU model (RHEL-70052)
- cpu_map: Add n270-v1 CPU model (RHEL-70052)
- cpu_map: Add core2duo-v1 CPU model (RHEL-70052)
- cpu_map: Add qemu32-v1 CPU model (RHEL-70052)
- cpu_map: Add kvm32-v1 CPU model (RHEL-70052)
- cpu_map: Add qemu64-v1 CPU model (RHEL-70052)
- cpu_map: Add kvm64-v1 CPU model (RHEL-70052)
- cpu_map: Add Conroe-v1 CPU model (RHEL-70052)
- cpu_map: Add Penryn-v1 CPU model (RHEL-70052)
- cpu_map: Add KnightsMill-v1 CPU model (RHEL-70052)
- cpu_map: Add athlon-v1 CPU model (RHEL-70052)
- cpu_map: Add phenom-v1 CPU model (RHEL-70052)
- cpu_map: Add Opteron_G1-v1 CPU model (RHEL-70052)
- cpu_map: Add Opteron_G2-v1 CPU model (RHEL-70052)
- cpu_map: Add Opteron_G3-v1 CPU model (RHEL-70052)
- cpu_map: Add Opteron_G4-v1 CPU model (RHEL-70052)
- cpu_map: Add Opteron_G5-v1 CPU model (RHEL-70052)
- cpu_map: Add EPYC-Genoa-v1 CPU model (RHEL-70052)

* Mon Dec  2 2024 Jiri Denemark <jdenemar@redhat.com> - 10.10.0-1
- Rebased to libvirt-10.10.0 (RHEL-50574)
- The rebase also fixes the following bugs:
    RHEL-23607, RHEL-24850, RHEL-29267, RHEL-30842, RHEL-53963
    RHEL-54325, RHEL-54326, RHEL-55240, RHEL-64341, RHEL-65372
    RHEL-65780, RHEL-65844, RHEL-67702, RHEL-67836, RHEL-68614
    RHEL-69417

* Fri Nov  1 2024 Jiri Denemark <jdenemar@redhat.com> - 10.9.0-1
- Rebased to libvirt-10.9.0 (RHEL-50574)
- The rebase also fixes the following bugs:
    RHEL-7036, RHEL-7122, RHEL-35752, RHEL-46870, RHEL-52314
    RHEL-60030, RHEL-60033, RHEL-64341

* Thu Oct 10 2024 Jiri Denemark <jdenemar@redhat.com> - 10.8.0-2
- Revert "network: *un*set the firewalld zone while shutting down a network" (RHEL-61576)
- Revert "network: support setting firewalld zone for bridge device of open networks" (RHEL-61576)
- network: call network(Add|Remove)FirewallRules() for forward mode='open' (RHEL-61576)
- network: a different way of supporting firewalld zone for mode='open' networks (RHEL-61576)
- network: a different implementation of *un*setting firewalld zone when network is destroyed (RHEL-61576)

* Wed Oct  2 2024 Jiri Denemark <jdenemar@redhat.com> - 10.8.0-1
- Rebased to libvirt-10.8.0 (RHEL-50574)
- The rebase also fixes the following bugs:
    RHEL-688, RHEL-7122, RHEL-19379, RHEL-22166, RHEL-24746
    RHEL-28827, RHEL-45200, RHEL-45952, RHEL-53964, RHEL-54550
    RHEL-56611, RHEL-58446

* Fri Aug  9 2024 Jiri Denemark <jdenemar@redhat.com> - 10.5.0-5
- qemu: virtiofs: cache: use 'never' instead of 'none' (RHEL-50329)
- qemu_domain: Strip <acpi/> from s390(x) definitions (RHEL-49516)
- qemuxmlconftest: Add tests for the ACPI stripping hack on s390 (RHEL-49516)
- vsh: Allow vshReadlineInit() to be called multiple times (RHEL-53560)

* Tue Jul 23 2024 Jiri Denemark <jdenemar@redhat.com> - 10.5.0-4
- virt-host-validate: Allow longer list of CPU flags (RHEL-39969)

* Mon Jul 22 2024 Jiri Denemark <jdenemar@redhat.com> - 10.5.0-3
- vmx: Be even more lax when trying to comprehend serial ports (RHEL-32182)

* Fri Jul 12 2024 Jiri Denemark <jdenemar@redhat.com> - 10.5.0-2
- vmx: Do not require all ID data for VMWare Distributed Switch (RHEL-46099)
- tests: vhostuser: add virtiofsd json descriptor (RHEL-7108, RHEL-40135)
- tests: qemuxmlconf: adjust test case to new virtiofsd (RHEL-7108, RHEL-40135)
- qemu: fill capabilities for virtiofsd (RHEL-7108, RHEL-40135)
- qemu: do not use deprecated options for new virtiofsd (RHEL-7108)
- qemu: migration: allow migration for virtiofs (RHEL-40135)
- virt-host-validate: Drop extra "PASS" (RHEL-46868)
- qemu: Don't leave beingDestroyed=true on inactive domain (RHEL-43309)

* Mon Jul  1 2024 Jiri Denemark <jdenemar@redhat.com> - 10.5.0-1
- Rebased to libvirt-10.5.0 (RHEL-21381)
- The rebase also fixes the following bugs:
    RHEL-23833, RHEL-29642, RHEL-37542, RHEL-39969, RHEL-40899
    RHEL-43309

* Tue Jun  4 2024 Jiri Denemark <jdenemar@redhat.com> - 10.4.0-1
- Rebased to libvirt-10.4.0 (RHEL-7489)
- The rebase also fixes the following bugs:
    RHEL-29642, RHEL-30373, RHEL-32182, RHEL-33044, RHEL-33082
    RHEL-34615, RHEL-35948, RHEL-36565, RHEL-36721, RHEL-39271
    RHEL-39400

* Mon May 27 2024 Jiri Denemark <jdenemar@redhat.com> - 10.3.0-2
- qemu: fix qemu command for pci hostdevs and ramfb='off' (RHEL-28808)

* Thu May  9 2024 Jiri Denemark <jdenemar@redhat.com> - 10.3.0-1
- Rebased to libvirt-10.3.0 (RHEL-29642)
- The rebase also fixes the following bugs:
    RHEL-25993, RHEL-7101, RHEL-7461, RHEL-16333, RHEL-7343
    RHEL-28808, RHEL-32880, RHEL-35879, RHEL-34112, RHEL-30373
    RHEL-23416, RHEL-23608, RHEL-26276, RHEL-22728

* Mon Apr 22 2024 Jiri Denemark <jdenemar@redhat.com> - 10.0.0-7
- qemu: virtiofs: do not crash if cgroups are missing
- qemu: virtiofs: set correct label when creating the socket
- qemu: virtiofs: error out if getting the group or user name fails
- Fix off-by-one error in udevListInterfacesByStatus (CVE-2024-1441)
- remote: check for negative array lengths before allocation (CVE-2024-2494)
- qemu: Fix migration with custom XML (RHEL-30622)

* Tue Mar 19 2024 Jiri Denemark <jdenemar@redhat.com> - 10.0.0-5
- cpu: x86: Add support for adding features to existing CPU models (RHEL-25995)
- qemu: domain: Check arch in qemuDomainMakeCPUMigratable (RHEL-25995)
- conf: cpu: Introduce virCPUDefListFeatures (RHEL-25995)
- qemu: domain: Drop added features from migratable CPU (RHEL-25995)
- Add vmx-* features to Broadwell* (RHEL-25995)
- Add vmx-* features to Cascadelake* (RHEL-25995)
- Add vmx-* features to Conroe (RHEL-25995)
- Add vmx-* features to Cooperlake (RHEL-25995)
- Add vmx-* features to core{,2}duo (RHEL-25995)
- Add vmx-* features to Haswell* (RHEL-25995)
- Add vmx-* features to Icelake* (RHEL-25995)
- Add vmx-* features to IvyBridge* (RHEL-25995)
- Add vmx-* features to kvm* (RHEL-25995)
- Add vmx-* features to Nehalem* (RHEL-25995)
- Add vmx-* features to Penryn (RHEL-25995)
- Add vmx-* features to SandyBridge* (RHEL-25995)
- Add vmx-* features to SapphireRapids (RHEL-25995)
- Add vmx-* features to Skylake* (RHEL-25995)
- Add vmx-* features to Snowridge (RHEL-25995)
- Add vmx-* features to Westmere* (RHEL-25995)

* Thu Feb 22 2024 Jiri Denemark <jdenemar@redhat.com> - 10.0.0-4
- Set stubDriverName from hostdev driver model attribute during pci device setup (RHEL-25858)
- qemuMigrationDstPrepareStorage: Use 'switch' statement to include all storage types (RHEL-24825)
- qemuMigrationDstPrepareStorage: Properly consider path for 'vdpa' devices (RHEL-24825)
- domain_validate: Account for NVDIMM label size properly when checking for memory conflicts (RHEL-4452)

* Thu Feb  8 2024 Jiri Denemark <jdenemar@redhat.com> - 10.0.0-3
- remote_driver: Restore special behavior of remoteDomainGetBlockIoTune() (RHEL-22800)
- conf: Introduce dynamicMemslots attribute for virtio-mem (RHEL-15316)
- qemu_capabilities: Add QEMU_CAPS_DEVICE_VIRTIO_MEM_PCI_DYNAMIC_MEMSLOTS capability (RHEL-15316)
- qemu_validate: Check capability for virtio-mem dynamicMemslots (RHEL-15316)
- qemu_command: Generate cmd line for virtio-mem dynamicMemslots (RHEL-15316)
- qemu_snapshot: fix detection if non-leaf snapshot isn't in active chain (RHEL-23212)
- qemu_snapshot: create: refactor external snapshot detection (RHEL-22797)
- qemu_snapshot: create: don't require disk-only flag for offline external snapshot (RHEL-22797)
- remoteDispatchAuthPolkit: Fix lock ordering deadlock if client closes connection during auth (RHEL-20337)
- util: virtportallocator: Add VIR_DEBUG statements for port allocations and release (RHEL-21543)
- qemu: migration: Properly handle reservation of manually specified NBD port (RHEL-21543)
- qemuMigrationDstStartNBDServer: Refactor cleanup (RHEL-21543)
- virPCIVPDResourceIsValidTextValue: Adjust comment to reflect actual code (RHEL-22314)
- util: pcivpd: Refactor virPCIVPDResourceIsValidTextValue (RHEL-22314)
- virNodeDeviceCapVPDFormatCustom*: Escape unsanitized strings (RHEL-22314)
- virNodeDeviceCapVPDFormat: Properly escape system-originated strings (RHEL-22314)
- schema: nodedev: Adjust allowed characters in 'vpdFieldValueFormat' (RHEL-22314)
- tests: Test the previously mishandled PCI VPD characters (RHEL-22314)
- Don't overwrite error message from 'virXPathNodeSet' (RHEL-22314)
- tests: virpcivpdtest: Remove 'testVirPCIVPDReadVPDBytes' case (RHEL-22314)
- util: virpcivpd: Unexport 'virPCIVPDReadVPDBytes' (RHEL-22314)
- util: pcivpd: Unexport virPCIVPDParseVPDLargeResourceFields (RHEL-22314)
- tests: virpcivpd: Remove 'testVirPCIVPDParseVPDStringResource' case (RHEL-22314)
- util: virpcivpd: Unexport 'virPCIVPDParseVPDLargeResourceString' (RHEL-22314)
- virPCIVPDResourceGetKeywordPrefix: Fix logging (RHEL-22314)
- util: virpcivpd: Remove return value from virPCIVPDResourceCustomUpsertValue (RHEL-22314)
- conf: virNodeDeviceCapVPDParse*: Remove pointless NULL checks (RHEL-22314)
- virpcivpdtest: testPCIVPDResourceBasic: Remove tests for uninitialized 'ro'/'rw' section (RHEL-22314)
- util: virPCIVPDResourceUpdateKeyword: Remove impossible checks (RHEL-22314)
- conf: node_device: Refactor 'virNodeDeviceCapVPDParseCustomFields' to fix error reporting (RHEL-22314)
- virNodeDeviceCapVPDParseXML: Fix error reporting (RHEL-22314)
- util: virpcivpd: Remove return value from virPCIVPDResourceUpdateKeyword (RHEL-22314)
- virPCIDeviceHasVPD: Refactor "debug" messages (RHEL-22314)
- virPCIDeviceGetVPD: Fix multiple error handling bugs (RHEL-22314)
- virPCIDeviceGetVPD: Handle errors in callers (RHEL-22314)
- virPCIVPDReadVPDBytes: Refactor error handling (RHEL-22314)
- virPCIVPDParseVPDLargeResourceString: Properly report errors (RHEL-22314)
- virPCIVPDParseVPDLargeResourceFields: Merge logic conditions (RHEL-22314)
- virPCIVPDParseVPDLargeResourceFields: Remove impossible 'default' switch case (RHEL-22314)
- virPCIVPDParseVPDLargeResourceFields: Refactor processing of read data (RHEL-22314)
- virPCIVPDParseVPDLargeResourceFields: Refactor return logic (RHEL-22314)
- virPCIVPDParseVPDLargeResourceFields: Report proper errors (RHEL-22314)
- virPCIVPDParse: Do reasonable error reporting (RHEL-22314)
- virt-admin: Add warning when connection to default daemon fails (RHEL-23170)

* Mon Jan 29 2024 Jiri Denemark <jdenemar@redhat.com> - 10.0.0-2
- tests: Add hostcpudata for machine with CPU clusters (RHEL-7043)
- conf: Report CPU clusters in capabilities XML (RHEL-7043)
- conf: Allow specifying CPU clusters (RHEL-7043)
- qemu: Introduce QEMU_CAPS_SMP_CLUSTERS (RHEL-7043)
- qemu: Use CPU clusters for guests (RHEL-7043)
- tests: Add test case for CPU clusters (RHEL-7043)
- qemu: Make monitor aware of CPU clusters (RHEL-7043)
- tests: Verify handling of CPU clusters in QMP data (RHEL-7043)
- build: Make daemons depend on generated *_protocol.[ch] (RHEL-15267)
- domain_validate: Check for domain address conflicts fully (RHEL-4452)
- qemu_hotplug: Don't lose 'created' flag in qemuDomainChangeNet() (RHEL-22714)

* Tue Jan 16 2024 Jiri Denemark <jdenemar@redhat.com> - 10.0.0-1
- Rebased to libvirt-10.0.0 (RHEL-15267)
- The rebase also fixes the following bugs:
    RHEL-18782, RHEL-735, RHEL-18165, RHEL-4607, RHEL-700
    RHEL-7100, RHEL-15480, RHEL-7416, RHEL-20609, RHEL-7570
    RHEL-20444, RHEL-17596, RHEL-7569

* Wed Dec 20 2023 Jiri Denemark <jdenemar@redhat.com> - 9.10.0-1
- Rebased to libvirt-9.10.0 (rhbz#RHEL-15267)
- The rebase also fixes the following bugs:
    rhbz#RHEL-16878, rhbz#RHEL-14611, rhbz#RHEL-7384, rhbz#RHEL-16870, rhbz#RHEL-18439
    rhbz#RHEL-16751, rhbz#RHEL-4452, rhbz#RHEL-17841, rhbz#RHEL-15288, rhbz#RHEL-7040

* Tue Nov 21 2023 Jiri Denemark <jdenemar@redhat.com> - 9.9.0-1
- Rebased to libvirt-9.9.0 (rhbz#RHEL-15267)
- The rebase also fixes the following bugs:
    rhbz#RHEL-7525, rhbz#RHEL-7570, rhbz#RHEL-7542, rhbz#RHEL-7568, rhbz#RHEL-7545
    rhbz#RHEL-3231, rhbz#RHEL-7382, rhbz#RHEL-7345, rhbz#RHEL-1717, rhbz#RHEL-7528
    rhbz#RHEL-1833, rhbz#RHEL-7569, rhbz#RHEL-4432, rhbz#RHEL-974, rhbz#RHEL-4994
    rhbz#RHEL-7419

* Fri Aug 25 2023 Jiri Denemark <jdenemar@redhat.com> - 9.5.0-6
- tests: Use DO_TEST_CAPS_*_ABI_UPDATE() for ppc64 (rhbz#2196178)
- tests: Switch to firmware autoselection for hvf (rhbz#2196178)
- tests: Use virt-4.0 machine type for aarch64 (rhbz#2196178)
- tests: Consistently use /path/to/guest_VARS.fd (rhbz#2196178)
- tests: Turn abi-update.xml into a symlink (rhbz#2196178)
- tests: Rename firmware-auto-efi-nvram-path (rhbz#2196178)
- qemu: Fix return value for qemuFirmwareFillDomainLegacy() (rhbz#2196178)
- qemu: Fix lookup against stateless/combined pflash (rhbz#2196178)
- tests: Add some more DO_TEST*ABI_UPDATE* macros (rhbz#2196178)
- tests: Add more tests for firmware selection (rhbz#2196178)
- tests: Update firmware descriptor files (rhbz#2196178)
- tests: Drop tags from BIOS firmware descriptor (rhbz#2196178)
- tests: Include microvm in firmwaretest (rhbz#2196178)
- qemu: Don't overwrite NVRAM template for legacy firmware (rhbz#2196178)
- qemu: Generate NVRAM path in more cases (rhbz#2196178)
- qemu: Filter firmware based on loader.readonly (rhbz#2196178)
- qemu: Match NVRAM template extension for new domains (rhbz#2196178)
- conf: Don't default to raw format for loader/NVRAM (rhbz#2196178)
- tests: Rename firmware-auto-efi-format-loader-qcow2-nvram-path (rhbz#2196178)
- tests: Reintroduce firmware-auto-efi-format-mismatch (rhbz#2196178)
- rpm: Reorder scriptlets (rhbz#2210058)
- rpm: Reduce use of with_modular_daemons (rhbz#2210058)
- rpm: Remove custom libvirtd restart logic (rhbz#2210058)
- rpm: Introduce new macros for handling of systemd units (rhbz#2210058)
- rpm: Switch to new macros for handling of systemd units (rhbz#2210058)
- rpm: Delete unused macros (rhbz#2210058)

* Wed Aug  2 2023 Jiri Denemark <jdenemar@redhat.com> - 9.5.0-5
- Revert "qemu_passt: Actually use @logfd" (rhbz#2209191)
- Revert "qemu_passt: Precreate passt logfile" (rhbz#2209191)

* Mon Jul 31 2023 Jiri Denemark <jdenemar@redhat.com> - 9.5.0-4
- storage: Fix returning of locked objects from 'virStoragePoolObjListSearch' (CVE-2023-3750, rhbz#2221851)

* Fri Jul 21 2023 Jiri Denemark <jdenemar@redhat.com> - 9.5.0-3
- tests: remove acpi support from s390x ccw hotplug tests (rhbz#2168499)
- tests: add capabilities for QEMU 8.1.0 on s390x (rhbz#2168499)
- qemu: add run-with async-teardown capability (rhbz#2168499)
- qemu: allow use of async teardown in domain (rhbz#2168499)
- conf: domcaps: Add 'async-teardown' domain capability (rhbz#2168499)
- qemu: S390 does not provide physical address size (rhbz#2224016)
- nodedev: report mdev persistence properly (rhbz#2143158)
- node_device: Don't leak error message buffer from virMdevctlListDefined|Active (rhbz#2143158)

* Mon Jul 17 2023 Jiri Denemark <jdenemar@redhat.com> - 9.5.0-2
- nodedev: transient mdev update on nodeDeviceCreateXML (rhbz#2143158)
- nodedev: refactor mdevctl thread functions (rhbz#2143158)
- nodedev: update mdevs from the mdevctl thread (rhbz#2143158)

* Mon Jul  3 2023 Jiri Denemark <jdenemar@redhat.com> - 9.5.0-1
- Rebased to libvirt-9.5.0 (rhbz#2175785)

* Wed Jun 28 2023 Jiri Denemark <jdenemar@redhat.com> - 9.5.0-0rc1.1
- Rebased to libvirt-9.5.0-rc1 (rhbz#2175785)
- The rebase also fixes the following bugs:
    rhbz#2160356, rhbz#2209191, rhbz#2210287, rhbz#2209853, rhbz#2171860
    rhbz#2138150, rhbz#2171384

* Fri Jun  2 2023 Jiri Denemark <jdenemar@redhat.com> - 9.4.0-1
- Rebased to libvirt-9.4.0 (rhbz#2175785)
- The rebase also fixes the following bugs:
    rhbz#2119007, rhbz#2193315, rhbz#2209658, rhbz#2143158, rhbz#2208946
    rhbz#2138150, rhbz#2203657, rhbz#2180679, rhbz#2203709

* Tue May 16 2023 Jiri Denemark <jdenemar@redhat.com> - 9.3.0-2
- qemu_domin: Account for NVMe disks when calculating memlock limit on hotplug (rhbz#2014030)

* Fri May  5 2023 Jiri Denemark <jdenemar@redhat.com> - 9.3.0-1
- Rebased to libvirt-9.3.0 (rhbz#2175785)
- The rebase also fixes the following bugs:
    rhbz#2181235, rhbz#2176215, rhbz#2187133, rhbz#2178885, rhbz#2174700
    rhbz#2160435, rhbz#2184966, rhbz#2187278, rhbz#2014030, rhbz#2185184
    rhbz#2156300

* Mon Apr  3 2023 Jiri Denemark <jdenemar@redhat.com> - 9.2.0-1
- Rebased to libvirt-9.2.0 (rhbz#2175785)
- The rebase also fixes the following bugs:
    rhbz#2178885, rhbz#2000410, rhbz#2175582, rhbz#2154750, rhbz#2175449
    rhbz#2181234, rhbz#2078693, rhbz#2176924, rhbz#2156300, rhbz#2173142
    rhbz#2171973, rhbz#2178866, rhbz#2182961, rhbz#2174397, rhbz#2179030
    rhbz#2161965, rhbz#2035985

* Mon Mar 13 2023 Jiri Denemark <jdenemar@redhat.com> - 9.1.0-1
- Rebased to libvirt-9.1.0 (rhbz#2175785)
- The rebase also fixes the following bugs:
    rhbz#2004850, rhbz#2137346, rhbz#2166235, rhbz#1961326

* Wed Feb 22 2023 Jiri Denemark <jdenemar@redhat.com> - 9.0.0-7
- qemu_snapshot: remove memory snapshot when deleting external snapshot (rhbz#2170826)
- qemu_snapshot: refactor qemuSnapshotDeleteExternalPrepare (rhbz#2170826)

* Fri Feb 17 2023 Jiri Denemark <jdenemar@redhat.com> - 9.0.0-6
- rpc: client: Don't check return value of virNetMessageNew (rhbz#2145188)
- rpc: Don't warn about "max_client_requests" in single-threaded daemons (rhbz#2145188)

* Mon Feb 13 2023 Jiri Denemark <jdenemar@redhat.com> - 9.0.0-5
- qemu_extdevice: Do cleanup host only for VIR_DOMAIN_TPM_TYPE_EMULATOR (rhbz#2168762)
- qemu: blockjob: Handle 'pending' blockjob state only when we need it (rhbz#2168769)

* Thu Feb  9 2023 Jiri Denemark <jdenemar@redhat.com> - 9.0.0-4
- qemuProcessStop: Fix detection of outgoing migration for external devices (rhbz#2161557)
- qemuExtTPMStop: Restore TPM state label more often (rhbz#2161557)
- qemuProcessLaunch: Tighten rules for external devices wrt incoming migration (rhbz#2161557)
- qemu_process: Produce better debug message wrt domain namespaces (rhbz#2167302)
- qemu_namespace: Deal with nested mounts when umount()-ing /dev (rhbz#2167302)
- qemuProcessRefreshDisks: Don't skip filling of disk information if tray state didn't change (rhbz#2166411)

* Wed Feb  1 2023 Jiri Denemark <jdenemar@redhat.com> - 9.0.0-3
- src: Don't use virReportSystemError() on virProcessGetStatInfo() failure (rhbz#2148266)
- qemu: Provide virDomainGetCPUStats() implementation for session connection (rhbz#2148266)
- virsh: Make domif-setlink work more than once (rhbz#2165466)
- qemu_fd: Remove declaration for 'qemuFDPassNewDirect' (rhbz#2040272)
- qemuStorageSourcePrivateDataFormat: Rename 'tmp' to 'objectsChildBuf' (rhbz#2040272)
- qemu: command: Handle FD passing commandline via qemuBuildBlockStorageSourceAttachDataCommandline (rhbz#2040272)
- qemuFDPassTransferCommand: Mark that FD was passed (rhbz#2040272)
- qemu: fd: Add helpers allowing storing FD set data in status XML (rhbz#2040272)
- qemu: domain: Store fdset ID for disks passed to qemu via FD (rhbz#2040272)
- qemu: block: Properly handle FD-passed disk hot-(un-)plug (rhbz#2040272)

* Wed Jan 25 2023 Jiri Denemark <jdenemar@redhat.com> - 9.0.0-2
- vircgroupv2: fix cpu.weight limits check (rhbz#2037998)
- domain_validate: drop cpu.shares cgroup check (rhbz#2037998)
- docs: document correct cpu shares limits with both cgroups v1 and v2 (rhbz#2037998)
- qemu_interface: Fix managed='no' case when creating an ethernet interface (rhbz#2144738)
- conf: clarify some external TPM error messages (rhbz#2063723)
- qemu: hotplug: Remove legacy quirk for 'dimm' address generation (rhbz#2158701)
- qemu: alias: Remove 'oldAlias' argument of qemuAssignDeviceMemoryAlias (rhbz#2158701)
- qemu: Remove 'memAliasOrderMismatch' field from VM private data (rhbz#2158701)
- rpc: Fix error message in virNetServerSetClientLimits (rhbz#2033879)

* Mon Jan 16 2023 Jiri Denemark <jdenemar@redhat.com> - 9.0.0-1
- Rebased to libvirt-9.0.0 (rhbz#2124466)
- The rebase also fixes the following bugs:
    rhbz#2151064, rhbz#1874163, rhbz#2130192, rhbz#2111948, rhbz#1824722
    rhbz#2150455, rhbz#2063723, rhbz#1717611, rhbz#2160448, rhbz#2151869
    rhbz#2040272, rhbz#2144738, rhbz#2159851, rhbz#2156289, rhbz#2033879
    rhbz#1820437, rhbz#2151202

* Tue Dec  6 2022 Jiri Denemark <jdenemar@redhat.com> - 8.10.0-2
- qemu_process: Document qemuProcessPrepare{Domain,Host}() order (rhbz#2150760)
- qemu_extdevice: Init paths in qemuExtDevicesPrepareDomain() (rhbz#2150760)
- qemu_extdevice: Expose qemuExtDevicesInitPaths() (rhbz#2150760)
- qemu: Init ext devices paths on reconnect (rhbz#2150760)

* Thu Dec  1 2022 Jiri Denemark <jdenemar@redhat.com> - 8.10.0-1
- Rebased to libvirt-8.10.0 (rhbz#2124466)
- The rebase also fixes the following bugs:
    rhbz#2128993, rhbz#2143235, rhbz#2143840, rhbz#1874163, rhbz#2000075
    rhbz#2143838, rhbz#2104919, rhbz#2072204, rhbz#2137298

* Wed Nov  2 2022 Jiri Denemark <jdenemar@redhat.com> - 8.9.0-2
- RHEL: rpminspect: Disable abidiff inspection (rhbz#2124466)
- spec: Fix python3-libvirt requirement in client-qemu package (rhbz#2124466)

* Tue Nov  1 2022 Jiri Denemark <jdenemar@redhat.com> - 8.9.0-1
- Rebased to libvirt-8.9.0 (rhbz#2124466)
- The rebase also fixes the following bugs:
    rhbz#2074559, rhbz#2134009, rhbz#1777212, rhbz#2013523, rhbz#2114866
    rhbz#1964855

* Mon Oct  3 2022 Jiri Denemark <jdenemar@redhat.com> - 8.8.0-1
- Rebased to libvirt-8.8.0 (rhbz#2124466)
- The rebase also fixes the following bugs:
    rhbz#2122534, rhbz#2121262, rhbz#2130089, rhbz#2121276, rhbz#2121627
    rhbz#2125111, rhbz#2129239, rhbz#1964855, rhbz#2114866

* Tue Sep  6 2022 Jiri Denemark <jdenemar@redhat.com> - 8.7.0-1
- Rebased to libvirt-8.7.0 (rhbz#2124466)
- The rebase also fixes the following bugs:
    rhbz#2084046, rhbz#2108483, rhbz#2123371, rhbz#2101633, rhbz#1988211
    rhbz#2086677, rhbz#2103132, rhbz#2078805, rhbz#2111301, rhbz#2094641

* Thu Aug  4 2022 Jiri Denemark <jdenemar@redhat.com> - 8.5.0-5
- rpc: Pass OPENSSL_CONF through to ssh invocations (rhbz#2112348)

* Fri Jul 29 2022 Jiri Denemark <jdenemar@redhat.com> - 8.5.0-4
- qemu: Pass migration flags to qemuMigrationParamsApply (rhbz#2111070)
- qemu_migration_params: Replace qemuMigrationParamTypes array (rhbz#2111070)
- qemu_migration: Pass migParams to qemuMigrationSrcResume (rhbz#2111070)
- qemu_migration: Apply max-postcopy-bandwidth on post-copy resume (rhbz#2111070)
- qemu: Always assume support for QEMU_CAPS_MIGRATION_PARAM_XBZRLE_CACHE_SIZE (rhbz#2107892)
- qemu_migration: Store original migration params in status XML (rhbz#2107892)
- qemu_migration_params: Refactor qemuMigrationParamsApply (rhbz#2107892)
- qemu_migration_params: Refactor qemuMigrationParamsReset (rhbz#2107892)
- qemu_migration_params: Avoid deadlock in qemuMigrationParamsReset (rhbz#2107892)
- qemu: Restore original memory locking limit on reconnect (rhbz#2107424)
- qemu: Properly release job in qemuDomainSaveInternal (rhbz#1497907)
- qemu: don't call qemuMigrationSrcIsAllowedHostdev() from qemuMigrationDstPrepareFresh() (rhbz#1497907)

* Mon Jul 25 2022 Jiri Denemark <jdenemar@redhat.com> - 8.5.0-3
- qemu: introduce capability QEMU_CAPS_MIGRATION_BLOCKED_REASONS (rhbz#2092833)
- qemu: new function to retrieve migration blocker reasons from QEMU (rhbz#2092833)
- qemu: query QEMU for migration blockers before our own harcoded checks (rhbz#2092833)
- qemu: remove hardcoded migration fail for vDPA devices if we can ask QEMU (rhbz#2092833)
- qemu_migration: Use EnterMonitorAsync in qemuDomainGetMigrationBlockers (rhbz#2092833)
- qemu: don't try to query QEMU about migration blockers during offline migration (rhbz#2092833)
- qemu_migration: Acquire correct job in qemuMigrationSrcIsAllowed (rhbz#2092833)
- virsh: Require --xpath for *dumpxml (rhbz#2103524)
- qemu: skip hardcoded hostdev migration check if QEMU can do it for us (rhbz#1497907)

* Fri Jul 15 2022 Jiri Denemark <jdenemar@redhat.com> - 8.5.0-2
- domain_conf: Format <defaultiothread/> more often (rhbz#2059511)
- domain_conf: Format iothread IDs more often (rhbz#2059511)
- qemu: Make IOThread changing more robust (rhbz#2059511)
- qemuDomainSetIOThreadParams: Accept VIR_DOMAIN_AFFECT_CONFIG flag (rhbz#2059511)
- virsh: Implement --config for iothreadset (rhbz#2059511)
- docs: Document TPM portion of domcaps (rhbz#2103119)
- virtpm: Introduce TPM-1.2 and TPM-2.0 capabilieis (rhbz#2103119)
- domcaps: Introduce TPM backendVersion (rhbz#2103119)
- qemu: Report supported TPM version in domcaps (rhbz#2103119)
- vircpi: Add PCIe 5.0 and 6.0 link speeds (rhbz#2105231)

* Fri Jul  1 2022 Jiri Denemark <jdenemar@redhat.com> - 8.5.0-1
- Rebased to libvirt-8.5.0 (rhbz#2060313)
- The rebase also fixes the following bugs:
    rhbz#1475431, rhbz#2026765, rhbz#2059511, rhbz#2089431, rhbz#2102009

* Fri Jun 24 2022 Jiri Denemark <jdenemar@redhat.com> - 8.4.0-3
- qemu: fd: Fix monitor usage of qemuFDPassDirectGetPath (rhbz#2092856)

* Tue Jun 14 2022 Jiri Denemark <jdenemar@redhat.com> - 8.4.0-2
- Revert "RHEL: Fix virConnectGetMaxVcpus output" (rhbz#2095260)

* Thu Jun  2 2022 Jiri Denemark <jdenemar@redhat.com> - 8.4.0-1
- Rebased to libvirt-8.4.0 (rhbz#2060313)
- The rebase also fixes the following bugs:
    rhbz#2057768, rhbz#2081981, rhbz#2035163, rhbz#2075837, rhbz#2082540
    rhbz#2075383

* Fri May  6 2022 Jiri Denemark <jdenemar@redhat.com> - 8.3.0-1
- Rebased to libvirt-8.3.0 (rhbz#2060313)
- The rebase also fixes the following bugs:
    rhbz#1653327, rhbz#2075765, rhbz#2075464, rhbz#2078274, rhbz#2070380
    rhbz#2073887, rhbz#2073867

* Fri Apr  1 2022 Jiri Denemark <jdenemar@redhat.com> - 8.2.0-1
- Rebased to libvirt-8.2.0 (rhbz#2060313)
- The rebase also fixes the following bugs:
    rhbz#1866400, rhbz#2065381, rhbz#2063903, rhbz#1901394, rhbz#2065399

* Fri Mar  4 2022 Jiri Denemark <jdenemar@redhat.com> - 8.1.0-1
- Rebased to libvirt-8.1.0 (rhbz#2060313)
- The rebase also fixes the following bugs:
    rhbz#1643868, rhbz#2045953, rhbz#1910856, rhbz#2051451, rhbz#1745868
    rhbz#2040548, rhbz#2041665, rhbz#1999372, rhbz#2038045, rhbz#2045959
    rhbz#2046024, rhbz#2040555, rhbz#2057067, rhbz#2037146, rhbz#2036300

* Thu Feb 24 2022 Jiri Denemark <jdenemar@redhat.com> - 8.0.0-5
- Make systemd unit ordering more robust (rhbz#1868537)
- util: Fix machined servicename (rhbz#1868537)

* Thu Feb 10 2022 Jiri Denemark <jdenemar@redhat.com> - 8.0.0-4
- qemu_command: Generate memory only after controllers (rhbz#2047271)
- qemu: Validate domain definition even on migration (rhbz#2048435)

* Wed Feb  2 2022 Jiri Denemark <jdenemar@redhat.com> - 8.0.0-3
- qemuDomainSetupDisk: Initialize 'targetPaths' (rhbz#2046170)

* Tue Jan 25 2022 Jiri Denemark <jdenemar@redhat.com> - 8.0.0-2
- build: Only install libvirt-guests when building libvirtd (rhbz#2042529)
- docs: Add man page for libvirt-guests (rhbz#2042529)
- remove sysconfig files (rhbz#2042529)
- spec: Run pre/post-install stuff on 'daemon-driver-storage-core' (rhbz#2025644)
- qemu: fix inactive snapshot revert (rhbz#2039136)
- Revert "report error when virProcessGetStatInfo() is unable to parse data" (rhbz#2043579)

* Fri Jan 14 2022 Jiri Denemark <jdenemar@redhat.com> - 8.0.0-1
- Rebased to libvirt-8.0.0 (rhbz#2001507)
- The rebase also fixes the following bugs:
    rhbz#2039246, rhbz#2039652, rhbz#2039651, rhbz#2039131

* Mon Jan 10 2022 Jiri Denemark <jdenemar@redhat.com> - 8.0.0-0rc1.1
- Rebased to libvirt-8.0.0-rc1 (rhbz#2001507)
- The rebase also fixes the following bugs:
    rhbz#2034539, rhbz#2027400, rhbz#1945420, rhbz#1851249, rhbz#2032410
    rhbz#2026812, rhbz#2032365, rhbz#2035888, rhbz#2036895, rhbz#2026537

* Wed Dec  1 2021 Jiri Denemark <jdenemar@redhat.com> - 7.10.0-1
- Rebased to libvirt-7.10.0 (rhbz#2001507)
- The rebase also fixes the following bugs:
    rhbz#2024098, rhbz#1964223, rhbz#2018488, rhbz#2021437, rhbz#2022589
    rhbz#2023605, rhbz#1431589, rhbz#2024435, rhbz#2016599, rhbz#1945501
    rhbz#2023674

* Fri Nov  5 2021 Jiri Denemark <jdenemar@redhat.com> - 7.9.0-1
- Rebased to libvirt-7.9.0 (rhbz#2001507)
- The rebase also fixes the following bugs:
    rhbz#2007659, rhbz#2014487, rhbz#1806856, rhbz#2014139, rhbz#1964223
    rhbz#2007168, rhbz#2012386, rhbz#2013573, rhbz#1897708

* Tue Oct  5 2021 Jiri Denemark <jdenemar@redhat.com> - 7.8.0-1
- Rebased to libvirt-7.8.0 (rhbz#2001507)
- The rebase also fixes the following bugs:
    rhbz#1999420, rhbz#2002761, rhbz#1998920, rhbz#1986066, rhbz#1822891
    rhbz#2001627, rhbz#1819160, rhbz#2000861, rhbz#2003092

* Wed Sep 22 2021 Jiri Denemark <jdenemar@redhat.com> - 7.7.0-3
- virshDomainGetVcpuBitmap: Return bitmap when taking the fallback path (rhbz#2004429)

* Tue Sep 21 2021 Jiri Denemark <jdenemar@redhat.com> - 7.7.0-2
- Update gating.yaml by adding subject_type
- Revert "RHEL: spec: Do not enable modular daemons yet" (rhbz#1920012)

* Fri Sep 10 2021 Jiri Denemark <jdenemar@redhat.com> - 7.7.0-1
- Rebased to libvirt-7.7.0 (rhbz#2001507)
- The rebase also fixes the following bugs:
    rhbz#2001326, rhbz#2001391, rhbz#2001322, rhbz#2001389, rhbz#1967187
    rhbz#2001327, rhbz#1977155, rhbz#2001997, rhbz#2001323
- RHEL: spec: Do not enable modular daemons yet (rhbz#2001507)

* Mon Aug 09 2021 Mohan Boddu <mboddu@redhat.com> - 7.6.0-2
- Rebuilt for IMA sigs, glibc 2.34, aarch64 flags
  Related: rhbz#1991688

* Wed Aug  4 2021 Jiri Denemark <jdenemar@redhat.com> - 7.6.0-1
- Rebased to libvirt-7.6.0 (rhbz#1950948)
- The rebase also fixes the following bugs:
    rhbz#1986509, rhbz#1984318, rhbz#1810661, rhbz#1977776, rhbz#1948433
    rhbz#1978526, rhbz#1976690

* Wed Jul 14 2021 Jiri Denemark <jdenemar@redhat.com> - 7.5.0-1
- Rebased to libvirt-7.5.0 (rhbz#1950948)
- The rebase also fixes the following bugs:
    rhbz#1949388, rhbz#1969354, rhbz#1970277, rhbz#1972145, rhbz#1973094
    rhbz#1975071, rhbz#1972468, rhbz#1975677

* Mon Jun  7 2021 Jiri Denemark <jdenemar@redhat.com> - 7.4.0-1
- Rebased to libvirt-7.4.0 (rhbz#1950948)
- The rebase also fixes the following bugs:
    rhbz#1960993

* Mon May 24 2021 Jiri Denemark <jdenemar@redhat.com> - 7.3.0-1
- Rebased to libvirt-7.3.0 (rhbz#1950948)
- The rebase also fixes the following bugs:
    rhbz#1898526, rhbz#1910617, rhbz#1910618, rhbz#1943392, rhbz#1946918
    rhbz#1947718, rhbz#1947720, rhbz#1947824, rhbz#1949342, rhbz#1950228
    rhbz#1950301, rhbz#1950601, rhbz#1950948, rhbz#1953939, rhbz#1958302
    rhbz#1962053
- RHEL: Enable usage of x-blockdev-reopen (rhbz#1953939)
- RHEL: Add gating.yaml for RHEL9 (rhbz#1950601)

* Thu Apr 22 2021 Jiri Denemark <jdenemar@redhat.com> - 7.0.0-6
- spec: Do not build qemu driver for Power on RHEL-9 (rhbz#1946529)

* Fri Apr 16 2021 Mohan Boddu <mboddu@redhat.com> - 7.0.0-5
- Rebuilt for RHEL 9 BETA on Apr 15th 2021. Related: rhbz#1947937

* Wed Feb 03 2021 Cole Robinson <aintdiscole@gmail.com> - 7.0.0-4
- Increase meson test timeout to fix builds on s390x copr

* Tue Feb 02 2021 Laine Stump <laine@redhat.com> - 7.0.0-3
- disable netcf in build

* Tue Jan 26 2021 Fedora Release Engineering <releng@fedoraproject.org> - 7.0.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Fri Jan 15 2021 Daniel P. Berrangé <berrange@redhat.com> - 7.0.0-1
- Rebase to 7.0.0 release

* Fri Dec 04 2020 Cole Robinson <aintdiscole@gmail.com> - 6.10.0-2.1
- Rebuild for wireshark soname bump

* Fri Dec 04 2020 Richard W.M. Jones <rjones@redhat.com> - 6.10.0-2
- Build libvirt-daemon-kvm for riscv64.

* Tue Dec 01 2020 Cole Robinson <crobinso@redhat.com> - 6.10.0-1
- Update to version 6.10.0

* Wed Nov  4 2020 Daniel P. Berrangé <berrange@redhat.com> - 6.9.0-2
- Re-apply reverted fix for disabling glusterfs, curl, openswman and libiscsi

* Tue Nov 03 2020 Cole Robinson <crobinso@redhat.com> - 6.9.0-1
- Update to version 6.9.0

* Mon Nov  2 2020 Daniel P. Berrangé <berrange@redhat.com> - 6.8.0-4
- Really fix meson option for disabling glusterfs
- Fix disabling curl, openswman and libiscsi

* Mon Nov  2 2020 Daniel P. Berrangé <berrange@redhat.com> - 6.8.0-4
- Fix name of meson option for disabling glusterfs

* Fri Oct 30 2020 Daniel P. Berrangé <berrange@redhat.com> - 6.8.0-3
- Fix stat() mocking for new glibc

* Wed Oct 28 2020 Daniel P. Berrangé <berrange@redhat.com> - 6.8.0-2
- Remove obsolete bash_completion conditional
- Pass args to meson based on with_libssh/with_libssh2

* Thu Oct 01 2020 Cole Robinson <crobinso@redhat.com> - 6.8.0-1
- Update to version 6.8.0

* Fri Sep  4 2020 Daniel P. Berrangé <berrange@redhat.com> - 6.7.0-2
- Fix QEMU start when KVM is not loaded (rhbz#1875327)

* Tue Sep 01 2020 Cole Robinson <crobinso@redhat.com> - 6.7.0-1
- Update to version 6.7.0

* Fri Aug 21 2020 Merlin Mathesius <mmathesi@redhat.com> - 6.6.0-3
- Fix so no platforms depend upon ceph for 32-bit architectures
- Include upstream patches to fix GCC 10 warnings

* Fri Aug 21 2020 Daniel P. Berrangé <berrange@redhat.com> - 6.6.0-2
- Fix creation of pools on non-btrfs (rhbz#1870197)

* Tue Aug 04 2020 Cole Robinson <crobinso@redhat.com> - 6.6.0-1
- Update to version 6.6.0

* Tue Jul 28 2020 Fedora Release Engineering <releng@fedoraproject.org> - 6.5.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Fri Jul 03 2020 Cole Robinson <crobinso@redhat.com> - 6.5.0-1
- Update to version 6.5.0

* Tue Jun 02 2020 Cole Robinson <crobinso@redhat.com> - 6.4.0-1
- Update to version 6.4.0

* Tue May 05 2020 Cole Robinson <crobinso@redhat.com> - 6.3.0-1
- Update to version 6.3.0

* Thu Apr 02 2020 Cole Robinson <crobinso@redhat.com> - 6.2.0-1
- Update to version 6.2.0

* Tue Mar 24 2020 Felipe Borges <feborges@redhat.com> - 6.1.0-2
- Check for disk type correctly in virDomainDiskTranslateSourcePool

* Wed Mar 04 2020 Cole Robinson <crobinso@redhat.com> - 6.1.0-1
- Update to version 6.1.0

* Tue Feb 25 2020 Cole Robinson <crobinso@redhat.com> - 6.0.0-3
- Rebuild for libiscsi soname bump

* Wed Jan 29 2020 Fedora Release Engineering <releng@fedoraproject.org> - 6.0.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Wed Jan 15 2020 Cole Robinson <crobinso@redhat.com> - 6.0.0-1
- Update to version 6.0.0
