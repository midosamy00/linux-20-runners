#!/usr/bin/env python3
import argparse
p = argparse.ArgumentParser()
p.add_argument("--total", type=int, required=True)
p.add_argument("--devices", type=int, default=20)
p.add_argument("--device", type=int, required=True)
a = p.parse_args()
assert 1 <= a.device <= a.devices, "device out of range"
assert a.total >= a.devices, "total_frames must be >= devices"
base, rem = divmod(a.total, a.devices)
start = (a.device - 1) * base + min(a.device - 1, rem) + 1
end = start + base - 1 + (1 if a.device <= rem else 0)
open("/tmp/chunk_start.txt", "w").write(str(start))
open("/tmp/chunk_end.txt", "w").write(str(end))
print(f"device {a.device}/{a.devices}: frames {start}-{end} of {a.total}")
