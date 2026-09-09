import hashlib
import json
from dataclasses import asdict, is_dataclass
from enum import Enum
from typing import Any


def _normalize(v: Any) -> Any:
    if is_dataclass(v):
        v = asdict(v)
    if isinstance(v, Enum):
        return v.value
    if isinstance(v, dict):
        return {k: _normalize(v[k]) for k in sorted(v) if v[k] is not None}
    if isinstance(v, (list, tuple)):
        return [_normalize(x) for x in v]
    return v


def canonical_bytes(v: Any) -> bytes:
    return json.dumps(_normalize(v), sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def sha256_hex(v: Any) -> str:
    return hashlib.sha256(canonical_bytes(v)).hexdigest()
