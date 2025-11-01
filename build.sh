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
  copr_release="${dist//centos/epel}"
  echo "Building packages for $copr_release..."
  for spec in $dist/SPECS/*.spec; do
    spec="${spec#$dist/}"
    package_name="$(basename "$spec" .spec)"
    dist_version="${dist#*-}"
    dist_name="${dist%%-*}"
    copr_args=( --chroot "$copr_release-aarch64" )

    # Special case for libvirt.
    # Since the ZFS driver of libvirt is disabled since Fedora 43, we also build it for x86_64.
    # And CentOS never shipped the Libvirt ZFS driver, so we build it for x86_64 as well.
    if [[ "$package_name" == "libvirt" ]]; then
      if  [[ "$dist_name" == "fedora" && "$dist_version" -ge "43" || "$dist_name" == "centos" ]]; then
        copr_args+=( --chroot "$copr_release-x86_64" )
      fi
    fi

    copr-cli buildscm --clone-url "$GIT_REPOSITORY" --method make_srpm --subdir "$dist" --spec "$spec" "${copr_args[@]}" --background --nowait "$COPR_PROJECT"
  done
done

echo "All builds submitted to COPR project '@$COPR_USERNAME/$COPR_PROJECT'."
echo "You can monitor the build status at: https://copr.fedorainfracloud.org/coprs/$COPR_USERNAME/$COPR_PROJECT/builds/"
