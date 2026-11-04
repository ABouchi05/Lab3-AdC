#!/usr/bin/env bash
# Continue the routed unified implementation; retain the original stages as evidence.
set -euo pipefail
librelane --pdk gf180mcuD --run-tag ffq_100_40 \
 --from OpenROAD.DetailedRouting \
 --with-initial-state config/runs/ffq_100_40/44-openroad-detailedrouting/state_out.json \
 --override-config DRT_ANTENNA_REPAIR_ITERS=10 \
 config/ffq_100_40.json > results/ffq_100_40_antenna_repair.log 2>&1
