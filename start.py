#!/usr/bin/env python3
import sys
from pathlib import Path

KEY = 0xAA

for path in Path('.').glob('*.json.bin'):
    data = path.read_bytes()
    orig = bytes(b ^ KEY for b in data)
    out = Path(path.stem)  # removes the final “.bin”
    out.write_bytes(orig)
    print(f"Decoded {path.name} → {out.name}")
