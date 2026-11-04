#!/usr/bin/env bash
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y curl git python3 python3-venv iverilog build-essential locales
locale-gen en_US.UTF-8
if ! test -x /nix/var/nix/profiles/default/bin/nix; then
 curl --proto '=https' --tlsv1.2 -fsSL https://artifacts.nixos.org/nix-installer -o /tmp/lab3-nix-installer.sh
 sh /tmp/lab3-nix-installer.sh install --no-confirm --extra-conf '
extra-substituters = https://nix-cache.fossi-foundation.org
extra-trusted-public-keys = nix-cache.fossi-foundation.org:3+K59iFwXqKsL7BNu6Guy0v+uTlwsxYQxjspXzqLYQs=
extra-experimental-features = nix-command flakes
'
fi
mkdir -p /opt/lab3
if ! test -d /opt/lab3/librelane-linux/.git; then
 git clone https://github.com/librelane/librelane.git /opt/lab3/librelane-linux
 git -C /opt/lab3/librelane-linux checkout 64ef80802d3d189b476636d2a6b17888c03304ee
fi
. /nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh
export NIX_BUILD_SHELL=/bin/bash
cd /opt/lab3/librelane-linux
nix-shell --run 'librelane --version; yosys -V; openroad -version'
