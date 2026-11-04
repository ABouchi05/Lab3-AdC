#!/usr/bin/env bash
set -euo pipefail
python3 tools/experiments.py --only rom_100_40 --manifest strict_config_manifest.json
for tag in rom_100_40 rom_80_40 rom_60_40; do
 set +e
 librelane --pdk gf180mcuD --run-tag "$tag" --from Checker.SetupViolations "config/$tag.json" > "results/${tag}_strict.log" 2>&1
 code=$?
 set -e
 echo "$tag $code" >> results/strict_corner_exit_codes.txt
done
cat results/strict_corner_exit_codes.txt
