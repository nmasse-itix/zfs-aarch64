#!/bin/bash

set -Eeuo pipefail

GIT_REPOSITORY="https://github.com/nmasse-itix/zfs-aarch64.git"
COPR_PROJECT="zfs-aarch64"
COPR_USERNAME="$(copr-cli whoami)"

for dist in centos-* fedora-*; do
  chroot="${dist//centos/epel}-aarch64"
  echo "Building packages for $dist using $chroot..."
  for spec in $dist/SPECS/*.spec; do
    spec=${spec#$dist/}
    copr-cli buildscm --clone-url "$GIT_REPOSITORY" --subdir "$dist" --spec "$spec" --chroot "$chroot" --nowait "$COPR_PROJECT"
  done
done

echo "All builds submitted to COPR project '@$COPR_USERNAME/$COPR_PROJECT'."
echo "You can monitor the build status at: https://copr.fedorainfracloud.org/coprs/$COPR_USERNAME/$COPR_PROJECT/builds/"
