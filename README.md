# TWRP device tree for Huawei MatePad Pro 11 GOT-W29

Initial TWRP 12.1 port based on the stock HarmonyOS/Android 12 recovery and
the stock Qualcomm SM8250 kernel.

## Device facts

- Device: Huawei GOT-W29
- SoC: Qualcomm SM8250 / `kona`
- Android compatibility: Android 12, API 31
- Kernel: 4.19.157-perf+
- Layout: A-only, dynamic `super` partition
- Logical partitions: `system`, `vendor`, `odm`, `hw_product`, `cust`
- Logical file systems: EROFS
- Userdata: F2FS with FBE v2, InlineCrypt and metadata encryption

## Prebuilt artifacts

The following files are taken from the stock recovery image:

- `prebuilt/Image.gz`
- `prebuilt/dtb`
- `prebuilt/dtbo.img`
- `prebuilt/recovery_ramdisk_header.bin`

They preserve the vendor kernel drivers for Huawei THP touch, LCD Kit,
Qualcomm DRM, EROFS and hardware-backed encryption.

## Build

The GitHub Actions workflow syncs the TWRP 12.1 minimal manifest and builds:

```sh
lunch twrp_got_w29-eng
mka recoveryimage
```

### Local Docker build

The local build keeps the AOSP checkout outside the repository:

```sh
chmod +x docker/build-local.sh docker/container-build.sh
./docker/build-local.sh
```

The source is stored in `/home/zzx/twrp-got-w29/local-build` by default.
Override it with `BUILD_ROOT=/path/to/build ./docker/build-local.sh`.

The packaging step uploads:

- `recovery.img`: complete recovery boot image for the `recovery` partition.
- `recovery_ramdisk.img`: split Huawei recovery ramdisk for testing the
  stock `recovery` + `recovery_vbmeta` boot chain.

## Test order

1. Keep verified copies of the stock `recovery`, `recovery_ramdisk`,
   `recovery_vendor`, and `recovery_vbmeta` images.
2. Test `recovery.img` first.
3. If the stock boot chain requires the split layout, test
   `recovery_ramdisk.img` while retaining the stock `recovery.img` and
   `recovery_vendor.img`.
4. Do not flash or format `persist`, `nvme`, `modemst1`, `modemst2`, `fsg`,
   or `metadata` during bring-up.

The first build is intended to confirm display, touch and ADB before enabling
data decryption and dynamic partition workflows.

