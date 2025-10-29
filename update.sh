#!/bin/bash

set -Eeuo pipefail

find . -name '*.src.rpm' -delete

for v in 41 42 43; do
  dist="fedora-$v"
  mkdir -p "$dist/SRPMS"
  echo "Downloading libvirt source for Fedora $v..."
  dnf download --repofrompath=$dist,https://dl.fedoraproject.org/pub/fedora/linux/releases/$v/Everything/source/tree/ --repofrompath=$dist-updates,https://dl.fedoraproject.org/pub/fedora/linux/updates/$v/Everything/source/tree/ --repo="$dist" --repo="$dist-updates" --source libvirt --destdir $dist/SRPMS/
  echo "Downloading zfs source for Fedora $v..."
  dnf download --repofrompath=zfs-$dist,http://download.zfsonlinux.org/fedora/42/SRPMS/ --repo=zfs-$dist --source zfs zfs-dkms --destdir $dist/SRPMS/
  echo "Importing source RPMs for Fedora $v..."
  rpm -ivh "--define=_topdir $PWD/$dist" $dist/SRPMS/*.src.rpm
done

for v in 9 10; do
  dist="centos-$v"
  mkdir -p "$dist/SRPMS"
  echo "Downloading libvirt source for CentOS Stream $v..."
  dnf download --repofrompath=$dist,https://mirror.stream.centos.org/$v-stream/AppStream/source/tree/ --repo="$dist" --source libvirt --destdir $dist/SRPMS/
  echo "Downloading zfs source for CentOS Stream $v..."
  dnf download --repofrompath=zfs-$dist,http://download.zfsonlinux.org/epel/10/SRPMS/ --repo=zfs-$dist --source zfs zfs-dkms --destdir $dist/SRPMS/
  echo "Importing source RPMs for CentOS Stream $v..."
  rpm -ivh "--define=_topdir $PWD/$dist" $dist/SRPMS/*.src.rpm
done
