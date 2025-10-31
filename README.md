# ZFS RPM packages for aarch64 architecture for Fedora, CentOS Stream & RHEL

## Purpose

This repository provides ZFS and libvirt RPM packages compiled specifically for the aarch64 (ARM64) architecture on Fedora, CentOS Stream, and RHEL systems. The main goals are:

- **ZFS Support on ARM64**: Provides native ZFS filesystem support for aarch64 systems where official ZFS packages may not be available or up-to-date
- **Libvirt with ZFS Storage**: Patches libvirt to enable ZFS storage pool support on aarch64 architecture, allowing virtualization environments to leverage ZFS storage backends
- **Multi-distribution Support**: Builds packages for multiple Linux distributions (Fedora 41-43, CentOS Stream 9-10) to ensure broad compatibility
- **Automated Building**: Uses COPR (Cool Other Package Repo) infrastructure for automated building and distribution

The repository automatically downloads upstream source RPMs, applies necessary patches (especially the `20-enable-zfs.patch` for libvirt), and builds optimized packages for ARM64 systems.

## Usage

### Installing ZFS Packages

The packages are built and hosted on COPR. To use them on your aarch64 system:

1. **Enable the COPR repository:**
   ```bash
   # Enable the COPR repository
   sudo dnf copr enable nmasse-itix/zfs-aarch64

   # Optionally, limit the packages to only ZFS-related ones
   sudo dnf config-manager setopt 'copr:copr.fedorainfracloud.org:nmasse-itix:zfs-aarch64.includepkgs=zfs zfs-dkms libvirt-daemon-driver-storage-zfs'

   # Verify the repository is enabled and packages are available
   sudo dnf --repo=copr:copr.fedorainfracloud.org:nmasse-itix:zfs-aarch64 search zfs
   ```

2. **Install ZFS packages:**
   ```bash
   # Install ZFS userspace utilities
   sudo dnf install zfs zfs-dkms
   
   # Install libvirt with ZFS support
   sudo dnf install libvirt libvirt-daemon-kvm libvirt-daemon-driver-storage-zfs
   ```

And then follow the [Getting Started](https://openzfs.github.io/openzfs-docs/Getting%20Started/index.html) documentation.

### Supported Distributions

- **Fedora**: 41, 42, 43
- **CentOS Stream**: 9, 10
- **RHEL**: 9, 10 (via EPEL repositories)

### Using ZFS with Libvirt

After installing the patched libvirt package, you can create ZFS storage pools:

```bash
# Create a ZFS storage pool definition
virsh pool-define-as mypool zfs - - - - /path/to/zfs/dataset

# Start and enable the pool
virsh pool-start mypool
virsh pool-autostart mypool
```

## Development

If you want to fork this repo and build it yourself, here are the instructions with `copr-cli`.

```sh
copr-cli create --chroot fedora-41-aarch64 --chroot fedora-42-aarch64 --chroot epel-9-aarch64 --chroot epel-10-aarch64 zfs-aarch64
```

And then send the build to COPR.

```sh
./build.sh
```

## Local compilation

```sh
# Install dependencies
dnf install -y git git-lfs mock rpm-build

# Clone the repository
git clone https://github.com/nmasse-itix/zfs-aarch64.git
cd zfs-aarch64
git lfs install
git lfs pull

# Function to compile a spec file
function build_spec() {
  mock_chroot="$1"
  spec="$2"
  spec_name="$(basename $spec .spec)"
  rootdir="$(dirname $spec)/../"
  rootdir="$(realpath $rootdir)"
  outdir="$rootdir/RPMS/$spec_name-$mock_chroot-$(date -Iseconds)/"
  mkdir -p "$outdir"
  rm -f "$rootdir/$spec_name"-*.src.rpm
  rpmbuild --define "_topdir $rootdir" -bs "$spec"
  mock -r "$mock_chroot" --resultdir="$outdir" "$rootdir/SRPMS/$spec_name"-*.src.rpm
}

# For example, to build libvirt for Fedora 42 aarch64
build_spec "fedora-42-aarch64" "fedora-42/SPECS/libvirt.spec"
```

## License

The source code of ZFS, Libvirt and the Fedora RPM spec files remain licensed under their original license.
The patches and top-level scripts may be too trivial to receive a license.
In case a license is required for them, they are under MIT License.
