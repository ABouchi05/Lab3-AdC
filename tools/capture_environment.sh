#!/usr/bin/env bash
set -euo pipefail
mkdir -p results
{
 date -u
 uname -a
 librelane --version
 yosys -V
 openroad -version
 python3 --version
 echo "PDK_ROOT=${PDK_ROOT:-unset}"
 echo 'PDK=gf180mcuD'
 echo 'SCL=gf180mcu_fd_sc_mcu7t5v0'
 if [[ -n "${LIBRELANE_ROOT:-}" ]]; then git -C "$LIBRELANE_ROOT" rev-parse HEAD; fi
} > results/environment.txt
# Keep the installed PDK metadata with the actual final run, not a guessed revision.
if [[ -n "${PDK_ROOT:-}" && -d "$PDK_ROOT/gf180mcuD" ]]; then
 find -L "$PDK_ROOT/gf180mcuD" -maxdepth 3 -name '*SOURCES*' -type f -exec cat {} \; > results/pdk-sources.txt
fi
