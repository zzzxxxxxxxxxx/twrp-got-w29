#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_ROOT="${BUILD_ROOT:-/home/zzx/twrp-got-w29/local-build}"
IMAGE_NAME="${IMAGE_NAME:-twrp-got-w29-builder:ubuntu22.04}"

mkdir -p "$BUILD_ROOT/home"

if docker info >/dev/null 2>&1; then
    DOCKER=(docker)
else
    DOCKER=(sudo docker)
fi

"${DOCKER[@]}" build \
    --file "$PROJECT_ROOT/docker/Dockerfile" \
    --tag "$IMAGE_NAME" \
    "$PROJECT_ROOT"

"${DOCKER[@]}" run --rm \
    --user "$(id -u):$(id -g)" \
    --env "BUILD_JOBS=${BUILD_JOBS:-16}" \
    --volume "$BUILD_ROOT:/work" \
    --volume "$PROJECT_ROOT:/project:ro" \
    --workdir /work \
    "$IMAGE_NAME" \
    bash /project/docker/container-build.sh

