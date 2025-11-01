#!/bin/bash

set -Eeuo pipefail

if [ ! -f "$HOME/.config/copr" ] && [ -n "$COPR_CONFIG" ]; then
  echo "Copr configuration file not found. Injecting from environment variable..."
  mkdir -p "$HOME/.config"
  echo "$COPR_CONFIG" > "$HOME/.config/copr"
  chmod 0600 "$HOME/.config/copr"
fi

GIT_REPOSITORY="https://github.com/nmasse-itix/zfs-aarch64.git"
COPR_PROJECT="zfs-aarch64"
COPR_USERNAME="$(copr-cli whoami)"

for dist in centos-* fedora-*; do
  chroot="${dist//centos/epel}-aarch64"
  echo "Building packages for $dist using $chroot..."
  for spec in $dist/SPECS/*.spec; do
    spec="${spec#$dist/}"
    package_name="$(basename "$spec" .spec)"
    dist_version="${dist#*-}"
    dist_name="${dist%%-*}"

    copr-cli buildscm --clone-url "$GIT_REPOSITORY" --method make_srpm --subdir "$dist" --spec "$spec" --chroot "$chroot" --background --nowait "$COPR_PROJECT"

    # Special case for libvirt on Fedora 43. Since the ZFS driver of libvirt is disabled since Fedora 43, we also build it for x86_64.
    if [[ "$package_name" == "libvirt" && "$dist_name" == "fedora" && "$dist_version" -ge "43" ]]; then
      echo "Also submitting libvirt build for Fedora 43 using x86_64 chroot..."
      copr-cli buildscm --clone-url "$GIT_REPOSITORY" --method make_srpm --subdir "$dist" --spec "$spec" --chroot "$dist-x86_64" --background --nowait "$COPR_PROJECT"
    fi
  done
done

echo "All builds submitted to COPR project '@$COPR_USERNAME/$COPR_PROJECT'."
echo "You can monitor the build status at: https://copr.fedorainfracloud.org/coprs/$COPR_USERNAME/$COPR_PROJECT/builds/"
