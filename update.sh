#!/bin/bash

set -Eeuo pipefail

find . -name '*.src.rpm' -delete

function install_all_srpm () {
  local dist=$1
  echo "Importing source RPMs of $dist..."
  rpm -ivh "--define=_topdir $PWD/$dist" "$dist/SRPMS/"*.src.rpm
}

function apply_patches () {
  local dist=$1
  for patch in "$dist/PATCHES"/*.patch; do
    echo "Applying patch $(basename "$patch")..."
    patch -d "$dist"* -p1 < "$patch"
  done
}

for v in 41 42 43; do
  dist="fedora-$v"
  mkdir -p "$dist/SRPMS"
  echo "Downloading libvirt source for Fedora $v..."
  dnf download --repofrompath=$dist,https://dl.fedoraproject.org/pub/fedora/linux/releases/$v/Everything/source/tree/ --repofrompath=$dist-updates,https://dl.fedoraproject.org/pub/fedora/linux/updates/$v/Everything/source/tree/ --repo="$dist" --repo="$dist-updates" --source libvirt --destdir $dist/SRPMS/
  echo "Downloading zfs source for Fedora $v..."
  if ! dnf download --repofrompath=zfs-$dist,http://download.zfsonlinux.org/fedora/$v/SRPMS/ --repo=zfs-$dist --source zfs zfs-dkms --destdir $dist/SRPMS/; then
    echo "ZFS source RPM not found for Fedora $v, skipping..."
  fi
  install_all_srpm "$dist"
  apply_patches "$dist"
done

for v in 9 10; do
  dist="centos-$v"
  mkdir -p "$dist/SRPMS"
  echo "Downloading libvirt source for CentOS Stream $v..."
  dnf download --repofrompath=$dist,https://mirror.stream.centos.org/$v-stream/AppStream/source/tree/ --repo="$dist" --source libvirt --destdir $dist/SRPMS/
  echo "Downloading zfs source for CentOS Stream $v..."
  if ! dnf download --repofrompath=zfs-$dist,http://download.zfsonlinux.org/epel/$v/SRPMS/ --repo=zfs-$dist --source zfs zfs-dkms --destdir $dist/SRPMS/; then
    echo "ZFS source RPM not found for CentOS Stream $v, skipping..."
  fi
  install_all_srpm "$dist"
  apply_patches "$dist"
done
