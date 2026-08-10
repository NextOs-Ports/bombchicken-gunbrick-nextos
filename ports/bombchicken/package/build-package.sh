#!/usr/bin/env bash
# Build, host-test and atomically bundle the public BYO-data release.
set -euo pipefail

export LC_ALL=C
export TZ=UTC
export PYTHONDONTWRITEBYTECODE=1
umask 077

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
PORT_DIR=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd -P)
REPO_ROOT=$(CDPATH= cd -- "$PORT_DIR/../.." && pwd -P)
NXRELEASE="$REPO_ROOT/framework/nxrelease/nxrelease.py"
NXRELEASE_VERSION=0.2.5
NXRELEASE_SHA256=dd307d3e18cd926be2cc51c2a7e9948193b3c309abcc414dfa8d784332df57ee
MANIFEST="$PORT_DIR/nxrelease.json"
DESTINATION=${1:-"$PORT_DIR/.release/bombchicken-1.1.2"}
ARCHIVE_NAME=bombchicken.zip

fail() {
  printf 'bombchicken package error: %s\n' "$*" >&2
  exit 1
}

[[ -f $NXRELEASE && -f $MANIFEST ]] ||
  fail "canonical NXRelease or manifest is missing"
ACTUAL_NXRELEASE_SHA256=$(sha256sum -- "$NXRELEASE" | awk '{print $1}')
[[ $ACTUAL_NXRELEASE_SHA256 == "$NXRELEASE_SHA256" ]] ||
  fail "NXRelease SHA-256 drifted: $ACTUAL_NXRELEASE_SHA256"
ACTUAL_NXRELEASE_VERSION=$(python3 -B "$NXRELEASE" --version)
[[ $ACTUAL_NXRELEASE_VERSION == "nxrelease $NXRELEASE_VERSION" ]] ||
  fail "NXRelease version drifted: $ACTUAL_NXRELEASE_VERSION"
[[ ! -e $DESTINATION && ! -L $DESTINATION ]] ||
  fail "destination already exists (release outputs are never overwritten): $DESTINATION"
mkdir -p -- "$(dirname -- "$DESTINATION")"

WORK_ROOT=$(mktemp -d "${TMPDIR:-/tmp}/bombchicken-package.XXXXXX")
cleanup() {
  case $WORK_ROOT in
    "${TMPDIR:-/tmp}"/bombchicken-package.*)
      [[ -d $WORK_ROOT ]] && rm -rf -- "$WORK_ROOT"
      ;;
    *)
      printf 'refusing unsafe cleanup target: %s\n' "$WORK_ROOT" >&2
      ;;
  esac
}
trap cleanup EXIT INT TERM

"$PORT_DIR/build.sh"
"$PORT_DIR/tests/run-host.sh"
python3 -B "$NXRELEASE" validate --manifest "$MANIFEST"
python3 -B "$NXRELEASE" bundle \
  --manifest "$MANIFEST" \
  --stage "$WORK_ROOT/stage" \
  --destination "$DESTINATION" \
  --archive-name "$ARCHIVE_NAME"
python3 -B "$NXRELEASE" verify \
  --archive "$DESTINATION/$ARCHIVE_NAME" \
  --sha256-file "$DESTINATION/$ARCHIVE_NAME.sha256"

printf 'BOMBCHICKEN PUBLIC PACKAGE PASS: %s\n' "$DESTINATION/$ARCHIVE_NAME"
printf '%s\n' \
  'physical_device_evidence=1' \
  'owner_data_in_package=0 device_calls=0 network_calls=0 guest_execution=0'
