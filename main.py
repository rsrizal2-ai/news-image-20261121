"""Entry point for the make.fun news-image-20261121 competition.

Copies the pre-rendered poster (news.png, beside this file) to
$MAKEFUN_OUTPUT_DIR/entry.png and self-checks the copy against the
competition gate: whole PNG (magic bytes), at most 1024x1024 pixels,
at most 1 MiB. Fails loudly if any check breaches the gate.

Python 3.13, standard library only, no network. Deterministic:
both runs write byte-identical output.
"""

import os
import shutil
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "news.png"
MAX_BYTES = 1_048_576
MAX_DIM = 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def png_dimensions(data: bytes) -> tuple[int, int]:
    """Read width/height from the PNG IHDR chunk (stdlib only)."""
    if len(data) < 33 or data[:8] != PNG_MAGIC:
        raise ValueError("not a PNG file (bad magic bytes)")
    # IHDR: length (4) + type "IHDR" (4) + width (4) + height (4)
    if data[12:16] != b"IHDR":
        raise ValueError("not a PNG file (missing IHDR chunk)")
    width, height = struct.unpack(">II", data[16:24])
    return width, height


def png_is_whole(data: bytes) -> bool:
    """True if the file ends with a complete IEND chunk (whole image)."""
    # IEND chunk: 4-byte length (0) + "IEND" + 4-byte CRC = 12 bytes.
    return len(data) >= 12 and data[-12:-8] == b"\x00\x00\x00\x00" \
        and data[-8:-4] == b"IEND"


def main() -> int:
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or str(HERE / "output")
    out_path = Path(out_dir) / "entry.png"
    if not SOURCE.is_file():
        print(f"ERROR: source image missing: {SOURCE}", file=sys.stderr)
        return 1
    out_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SOURCE, out_path)

    # Self-check the copy against the competition gate.
    data = out_path.read_bytes()
    if len(data) > MAX_BYTES:
        print(f"ERROR: entry.png is {len(data)} bytes, over the "
              f"{MAX_BYTES} byte cap", file=sys.stderr)
        return 1
    width, height = png_dimensions(data)
    if width > MAX_DIM or height > MAX_DIM:
        print(f"ERROR: entry.png is {width}x{height}, over the "
              f"{MAX_DIM}x{MAX_DIM} cap", file=sys.stderr)
        return 1
    if not png_is_whole(data):
        print("ERROR: entry.png is truncated (no complete IEND chunk)",
              file=sys.stderr)
        return 1
    print(f"wrote {out_path} ({width}x{height}, {len(data)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
