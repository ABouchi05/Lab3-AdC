#!/usr/bin/env bash
set -euo pipefail
. /nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
export NIX_BUILD_SHELL=/bin/bash
export PDK_ROOT=/opt/lab3/pdks
export LIBRELANE_ROOT=/opt/lab3/librelane-linux
if ! test -d "$LIBRELANE_ROOT/.git"; then
 git clone https://github.com/librelane/librelane.git "$LIBRELANE_ROOT"
 git -C "$LIBRELANE_ROOT" checkout 64ef80802d3d189b476636d2a6b17888c03304ee
fi
# Work inside the Linux filesystem; copy only the project sources, never prior runs.
project_src="$PWD"
mkdir -p /opt/lab3/design
for item in rtl sw tools tests config; do
 cp -a "$project_src/$item" /opt/lab3/design/
done
mkdir -p /opt/lab3/design/results
cd "$LIBRELANE_ROOT"
nix-shell --run "cd /opt/lab3/design && $*"
