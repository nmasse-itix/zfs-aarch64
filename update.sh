#!/bin/bash

set -Eeuo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

find . -name '*.src.rpm' -delete

if [ $# -gt 0 ]; then
  dists=( "$@" )
else
  echo "Computing a list of currently maintained versions of Fedora and CentOS Stream..."
  dists=( $(get_all_remote_dists) )
fi

for dist in "${dists[@]}"; do
  mkdir -p "$dist/SRPMS"
  find "$dist/SRPMS" -name '*.src.rpm' -delete
  rm -rf "$dist/SOURCES"
  if [[ "$dist" == "fedora-rawhide" ]]; then
    download_sources_fedora_rawhide "$dist"
  elif [[ "$dist" == fedora-* ]]; then
    download_sources_fedora "$dist"
  elif [[ "$dist" == centos-* ]]; then
    download_sources_centos_stream "$dist"
  else
    echo "Unknown distribution: $dist"
    exit 1
  fi
  mapfile -t srpms < <(find "$dist/SRPMS" -name '*.src.rpm')
  if [ ${#srpms[@]} -ne 3 ]; then
    echo "Expecting 3 source RPMs for $dist, got only ${#srpms[@]}, skipping..."
    continue
  fi
  echo "Found 3 source RPMs for $dist:"
  for srpm in "${srpms[@]}"; do
    echo "  - $(basename "$srpm")"
  done
  install_all_srpm "$dist"
  apply_patches "$dist"
done
