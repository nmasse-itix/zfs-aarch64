# Common code shared between build.sh and update.sh

# Prints the list of currently maintained Fedora versions (e.g. "42 43 44"),
# based on the Bodhi releases API.
function get_fedora_versions () {
  curl -fsSL "https://bodhi.fedoraproject.org/releases/?exclude_archived=true&state=current" \
    | jq -r '.releases[] | select(.id_prefix=="FEDORA") | .version' \
    | grep -E '^[0-9]+$' | sort -n
}

# Prints the list of active CentOS Stream versions (e.g. "9 10"),
# based on the directory listing of the official mirror.
function get_centos_stream_versions () {
  curl -fsSL "https://mirror.stream.centos.org/" \
    | grep -oP '(?<=href=")[0-9]+-stream(?=/")' \
    | sed 's/-stream//' | sort -n
}

# Prints the list of currently maintained Fedora and CentOS Stream versions (e.g. "centos-9 centos-10 fedora-42 fedora-43 fedora-44").
function get_all_remote_dists () {
  local dists=()
  for v in $(get_centos_stream_versions); do
    dists+=("centos-$v")
  done
  for v in $(get_fedora_versions); do
    dists+=("fedora-$v")
  done
  echo "${dists[@]}"
}

# Installs locally all source RPMs of a given distribution.
function install_all_srpm () {
  local dist=$1
  echo "Importing source RPMs of $dist..."
  rpm -ivh "--define=_topdir $PWD/$dist" "$dist/SRPMS/"*.src.rpm
}

# Applies all patches for a given distribution.
function apply_patches () {
  local dist=$1
  for patch in "$dist/PATCHES"/*.patch; do
    echo "Applying patch $(basename "$patch")..."
    patch -d "$dist"* -p1 < "$patch"
  done
}

# Downloads the libvirt and zfs source RPMs for a given Fedora distribution.
function download_sources_fedora () {
  local dist=$1
  local v="${dist#*-}"
  echo "Downloading libvirt source for Fedora $v..."
  dnf download --repofrompath=$dist,https://dl.fedoraproject.org/pub/fedora/linux/releases/$v/Everything/source/tree/ --repofrompath=$dist-updates,https://dl.fedoraproject.org/pub/fedora/linux/updates/$v/Everything/source/tree/ --repo="$dist" --repo="$dist-updates" --source libvirt --destdir $dist/SRPMS/
  echo "Downloading zfs source for Fedora $v..."
  if ! dnf download --repofrompath=zfs-$dist,http://download.zfsonlinux.org/fedora/$v/SRPMS/ --repo=zfs-$dist --source zfs zfs-dkms --destdir $dist/SRPMS/; then
    echo "ZFS source RPM not found for Fedora $v, skipping..."
  fi
}

# Downloads the libvirt and zfs source RPMs for a given CentOS Stream distribution.
function download_sources_centos_stream () {
  local dist=$1
  local v="${dist#*-}"
  echo "Downloading libvirt source for CentOS Stream $v..."
  dnf download --repofrompath=$dist,https://mirror.stream.centos.org/$v-stream/AppStream/source/tree/ --repo="$dist" --source libvirt --destdir $dist/SRPMS/
  echo "Downloading zfs source for CentOS Stream $v..."
  if ! dnf download --repofrompath=zfs-$dist,http://download.zfsonlinux.org/epel/$v/SRPMS/ --repo=zfs-$dist --source zfs zfs-dkms --destdir $dist/SRPMS/; then
    echo "ZFS source RPM not found for CentOS Stream $v, skipping..."
  fi
}

# Prints the latest Fedora version for which zfs source RPMs are published on
# download.zfsonlinux.org. This is not necessarily the latest Fedora version.
function get_latest_zfs_fedora_version () {
  curl -fsSL "http://download.zfsonlinux.org/fedora/" \
    | grep -oP '(?<=href=")[0-9]+(?=/")' | sort -n | tail -1
}

# Downloads the libvirt source RPM from Fedora Rawhide and the zfs source RPMs
# from the latest Fedora version published on download.zfsonlinux.org (which
# may lag behind Rawhide).
function download_sources_fedora_rawhide () {
  local dist=$1
  echo "Downloading libvirt source for Fedora Rawhide..."
  dnf download --repofrompath=$dist,https://dl.fedoraproject.org/pub/fedora/linux/development/rawhide/Everything/source/tree/ --repo="$dist" --source libvirt --destdir $dist/SRPMS/
  local zfs_version
  zfs_version="$(get_latest_zfs_fedora_version)"
  echo "Downloading zfs source from Fedora $zfs_version (latest available on download.zfsonlinux.org)..."
  if ! dnf download --repofrompath=zfs-$dist,http://download.zfsonlinux.org/fedora/$zfs_version/SRPMS/ --repo=zfs-$dist --source zfs zfs-dkms --destdir $dist/SRPMS/; then
    echo "ZFS source RPM not found for Fedora $zfs_version, skipping..."
  fi
}
