#!/usr/bin/env bash
set -eo pipefail

export LC_ALL=C
export ALLOW_MISSING_DEPENDENCIES=true
export HOME=/work/home
BUILD_JOBS="${BUILD_JOBS:-16}"

mkdir -p "$HOME" /work/aosp

cd /work/aosp
if [ ! -d .repo ]; then
    repo init --depth=1 \
        -u https://github.com/minimal-manifest-twrp/platform_manifest_twrp_aosp.git \
        -b twrp-12.1
fi

repo sync -c -j"$BUILD_JOBS" --force-sync --no-clone-bundle --no-tags

mkdir -p device/huawei/got_w29
rsync -a --delete \
    /project/device/huawei/got_w29/ \
    device/huawei/got_w29/

source build/envsetup.sh
lunch twrp_got_w29-eng
mka recoveryimage -j"$BUILD_JOBS"

python3 /project/scripts/verify_package.py \
    --recovery /work/aosp/out/target/product/got_w29/recovery.img \
    --template /project/device/huawei/got_w29/prebuilt/recovery_ramdisk_header.bin \
    --out-dir /work/out

printf '\nBuild complete:\n'
ls -lh /work/out

