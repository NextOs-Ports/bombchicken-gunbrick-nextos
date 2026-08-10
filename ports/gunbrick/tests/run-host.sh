#!/usr/bin/env bash
# Hermetic release gate. It audits/builds but never executes owner game code.
set -euo pipefail

export LC_ALL=C
export TZ=UTC
export PYTHONDONTWRITEBYTECODE=1

PORT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd -P)
REPO_ROOT=$(git -C "$PORT_DIR" rev-parse --show-toplevel)
cd "$PORT_DIR"

for script in build.sh build_universal.sh "Gunbrick.sh" \
              nxextract/run-extractor.sh nxextract/nxextract-runtime-env.sh \
              package/build-package.sh; do
  bash -n "$script"
done

python3 -B nxextract/nxextract.py recipe-check --recipe extractor.json
./build_universal.sh
python3 -B tests/test_gunbrick_contract.py
python3 -B ../../framework/nxrelease/nxrelease.py validate \
  --manifest nxrelease.json

DRY_ADD=$(git -C "$REPO_ROOT" add -n --all ports/gunbrick)
if grep -E \
  "ports/gunbrick/(\.build|build|gamedata|stage|verify)/|ports/gunbrick/(gunbrick|gunbrick-nextos)'|\.(apk|apkm|apks|xapk|obb|so|zip|raw|png)'" \
  <<< "$DRY_ADD"; then
  printf '%s\n' 'Git dry-run would stage built or owner data' >&2
  exit 1
fi

git -C "$REPO_ROOT" diff --check -- ports/gunbrick
printf '%s\n' \
  'GUNBRICK HOST GATE: PASS' \
  'physical_device_evidence=1 proprietary_payload_packaged=0 guest_execution=0'
