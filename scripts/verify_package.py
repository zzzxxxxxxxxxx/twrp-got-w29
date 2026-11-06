#!/usr/bin/env python3
"""Validate and package GOT-W29 TWRP boot images."""

from __future__ import annotations

import argparse
import hashlib
import struct
from pathlib import Path


ANDROID_MAGIC = b"ANDROID!"
RECOVERY_PARTITION_SIZE = 100_663_296
RAMDISK_PARTITION_SIZE = 37_748_736


def align(value: int, page: int) -> int:
    return (value + page - 1) // page * page


def read_header(data: bytes) -> dict[str, int]:
    if data[:8] != ANDROID_MAGIC:
        raise ValueError("not an Android boot image")
    names = [
        "kernel_size",
        "kernel_addr",
        "ramdisk_size",
        "ramdisk_addr",
        "second_size",
        "second_addr",
        "tags_addr",
        "page_size",
        "header_version",
        "os_version",
    ]
    return dict(zip(names, struct.unpack_from("<10I", data, 8)))


def extract_ramdisk(data: bytes, header: dict[str, int]) -> bytes:
    page = header["page_size"]
    offset = align(page + header["kernel_size"], page)
    return data[offset : offset + header["ramdisk_size"]]


def validate_recovery(data: bytes) -> dict[str, int]:
    header = read_header(data)
    expected = {
        "kernel_addr": 0x8000,
        "ramdisk_addr": 0x02000000,
        "tags_addr": 0x100,
        "page_size": 4096,
        "header_version": 2,
    }
    for key, value in expected.items():
        if header[key] != value:
            raise ValueError(f"{key} mismatch: {header[key]:#x} != {value:#x}")

    page = header["page_size"]
    kernel_end = page + header["kernel_size"]
    ramdisk_offset = align(kernel_end, page)
    second_offset = align(ramdisk_offset + header["ramdisk_size"], page)
    dtbo_size, dtbo_offset = struct.unpack_from("<IQ", data, 0x660)
    dtb_size, dtb_addr = struct.unpack_from("<IQ", data, 0x670)
    if not dtbo_size or dtbo_offset != second_offset:
        raise ValueError("recovery DTBO is missing or has an invalid offset")
    dtb_offset = align(dtbo_offset + dtbo_size, page)
    if not dtb_size or struct.unpack_from("<Q", data, 0x674)[0] != 0x01F00000:
        raise ValueError("DTB is missing or has an invalid address")
    if dtb_offset + dtb_size > len(data):
        raise ValueError("DTB extends past the boot image")
    print(
        "recovery image:",
        f"kernel={header['kernel_size']}",
        f"ramdisk={header['ramdisk_size']}",
        f"dtbo={dtbo_size}@{dtbo_offset}",
        f"dtb={dtb_size}@{dtb_offset}",
    )
    return header


def build_split_ramdisk(template: Path, ramdisk: bytes, output: Path) -> None:
    header = template.read_bytes()[:2048]
    if read_header(header)["header_version"] != 0:
        raise ValueError("recovery_ramdisk template is not boot header v0")

    page = 2048
    result = bytearray(header)
    struct.pack_into("<I", result, 8, 0)
    struct.pack_into("<I", result, 16, len(ramdisk))
    struct.pack_into("<I", result, 24, 0)
    digest = hashlib.sha1()
    digest.update(struct.pack("<I", 0))
    digest.update(ramdisk)
    digest.update(struct.pack("<I", len(ramdisk)))
    digest.update(struct.pack("<I", 0))
    result[576:596] = digest.digest()
    result.extend(ramdisk)

    if len(result) > RAMDISK_PARTITION_SIZE:
        raise ValueError(
            f"recovery_ramdisk is too large: {len(result)} > {RAMDISK_PARTITION_SIZE}"
        )
    result.extend(b"\0" * (RAMDISK_PARTITION_SIZE - len(result)))
    output.write_bytes(result)
    print(f"wrote {output} ({len(result)} bytes)")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--recovery", required=True, type=Path)
    parser.add_argument("--template", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    args = parser.parse_args()

    recovery = args.recovery.read_bytes()
    header = validate_recovery(recovery)
    ramdisk = extract_ramdisk(recovery, header)
    if not ramdisk:
        raise ValueError("recovery ramdisk is empty")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    recovery_out = args.out_dir / "recovery.img"
    if len(recovery) > RECOVERY_PARTITION_SIZE:
        raise ValueError(
            f"recovery image is too large: {len(recovery)} > {RECOVERY_PARTITION_SIZE}"
        )
    recovery_out.write_bytes(recovery + b"\0" * (RECOVERY_PARTITION_SIZE - len(recovery)))
    print(f"wrote {recovery_out} ({RECOVERY_PARTITION_SIZE} bytes)")

    build_split_ramdisk(
        args.template,
        ramdisk,
        args.out_dir / "recovery_ramdisk.img",
    )

    for image in sorted(args.out_dir.glob("*.img")):
        checksum = hashlib.sha256(image.read_bytes()).hexdigest()
        (args.out_dir / f"{image.name}.sha256").write_text(
            f"{checksum}  {image.name}\n",
            encoding="ascii",
        )
        print(f"{image.name}: {checksum}")


if __name__ == "__main__":
    main()

