#!/usr/bin/env python3
"""Local license-check harness + patch-point map.

This is a *test double* of a typical local comparator. Point the check function
at recovered logic from a sample; do not call third-party activation servers.

    python license_harness.py
    python license_harness.py --serial 0000-GOOD-KEY
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import asdict, dataclass
from typing import Callable, List, Optional, Sequence


@dataclass
class PatchPoint:
    name: str
    where: str
    original: str
    patched: str
    effect: str


@dataclass
class Vector:
    name: str
    serial: str
    machine_id: str
    expect_ok: bool


PATCH_POINTS: List[PatchPoint] = [
    PatchPoint(
        name="local_compare",
        where="check_serial+0x2c  (jz after cmp)",
        original="74 xx    jz fail",
        patched="75 xx    jnz fail   OR  90 90 nop nop",
        effect="treat comparator mismatch as success",
    ),
    PatchPoint(
        name="online_gate",
        where="verify_online() return",
        original="xor eax,eax; ret  (0 = fail)",
        patched="mov eax,1; ret",
        effect="skip network ticket; local harness should still assert",
    ),
    PatchPoint(
        name="machine_bind",
        where="hash(serial || machine_id)",
        original="call mix; cmp digest",
        patched="do not nop this without updating the harness vectors",
        effect="device-bind is a second compare — first jz is not enough",
    ),
]


def mix(serial: str, machine_id: str) -> str:
    blob = f"{serial.strip().upper()}|{machine_id.strip()}".encode("utf-8")
    return hashlib.sha256(blob).hexdigest()[:16]


def check_serial(serial: str, machine_id: str, good_digest: str) -> bool:
    if not serial or not machine_id:
        return False
    return mix(serial, machine_id) == good_digest


def default_vectors(good_digest: str, machine_id: str) -> List[Vector]:
    good = "0000-GOOD-KEY"
    assert mix(good, machine_id) == good_digest
    return [
        Vector("valid", good, machine_id, True),
        Vector("wrong_serial", "1111-BAD-KEY", machine_id, False),
        Vector("wrong_machine", good, "other-host", False),
        Vector("empty", "", machine_id, False),
    ]


def run_vectors(
    vectors: List[Vector],
    checker: Callable[[str, str], bool],
) -> List[dict]:
    rows = []
    for vec in vectors:
        got = checker(vec.serial, vec.machine_id)
        rows.append({**asdict(vec), "got_ok": got, "pass": got is vec.expect_ok})
    return rows


def main(argv: Optional[Sequence[str]] = None) -> int:
    p = argparse.ArgumentParser(description="License check harness")
    p.add_argument("--serial", default="0000-GOOD-KEY")
    p.add_argument("--machine-id", default="lab-host-01")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)

    good_digest = mix("0000-GOOD-KEY", args.machine_id)
    live_ok = check_serial(args.serial, args.machine_id, good_digest)
    rows = run_vectors(
        default_vectors(good_digest, args.machine_id),
        lambda s, m: check_serial(s, m, good_digest),
    )
    failed = [r for r in rows if not r["pass"]]
    payload = {
        "live_serial": args.serial,
        "live_ok": live_ok,
        "good_digest": good_digest,
        "patch_points": [asdict(pp) for pp in PATCH_POINTS],
        "vectors": rows,
        "all_passed": not failed,
    }
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"live_ok={live_ok} digest={good_digest}")
        for r in rows:
            flag = "OK" if r["pass"] else "FAIL"
            print(f"  [{flag}] {r['name']:14s} expect={r['expect_ok']} got={r['got_ok']}")
        print("patch-points:")
        for pp in PATCH_POINTS:
            print(f"  - {pp.name}: {pp.where} :: {pp.original} -> {pp.patched}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
