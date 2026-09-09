# System / Language / Reproducibility

## Implementation language

- Primary language: **Python 3.11+**
- Reference build tested in this package: Python version is recorded in `benchmark_results.json`.
- Cryptography backend: `cryptography` package for the Ed25519 variant; Python `hmac`/`hashlib` for deterministic HMAC-SHA-256 vectors.
- Tests: `pytest`.
- Persistent replay variation: standard-library SQLite 3.

## Why Python

Python is used to make the protocol state transitions readable and independently testable. It is not presented as the production language or the protected execution boundary. The same state machine can be implemented in Rust, C/C++, Go, Java, eBPF-adjacent host services, enclave code, HSM firmware integrations, SmartNIC/DPU services, or accelerator runtime components.

## Reproduction

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[test]'
pytest
PYTHONPATH=src python run_reference.py
PYTHONPATH=src python benchmarks/benchmark_hot_path.py
```

For Linux CI, recommended matrix: Python 3.11, 3.12, 3.13. For deployment validation, add the actual TEE/HSM/DPU/GPU/OS target and record firmware, kernel, CPU, security mode, attestation profile, clock source, and persistent-state backend.
