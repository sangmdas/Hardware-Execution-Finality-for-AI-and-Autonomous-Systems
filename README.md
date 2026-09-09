# Hardware-Enforced Execution-Finality — Runnable Reference Implementation

**Computation is not authority.**

This repository is a vendor-neutral, runnable reference implementation accompanying:

> **Computation Is Not Authority: Hardware-Enforced Execution-Finality for Agentic AI, MCP Tool Calls, and Industrial Agents**  
> Internet-Draft: `draft-das-hardware-enforced-execution-finality-01`

The implementation demonstrates the load-bearing chain:

```text
Candidate Act
   ↓
NON-EFFECTIVE STATE
   ↓
Protected Enforcement Domain (PED)
   ├─ validates act-specific predicates
   ├─ commits protected validation evidence
   └─ releases scoped non-bearer finality authority
   ↓
Protected Holder proof-of-possession
   ↓
Independent Finality Sink
   ├─ re-verifies act + evidence + authority + epochs + sink + PoP
   ├─ atomically consumes single-use authority
   └─ only then permits effectuation
   ↓
External Consequence
```

A PED `ALLOW` is **not** effectuation. The effect callback is unreachable until the independent Finality Sink succeeds.

## What is implemented

- Machine-verifiable Candidate Act descriptor and deterministic canonical digest.
- PED policy evaluation over tool, MCP server context, purpose, destination, consequence class, precision, amount, delegation depth, epochs, attestation status, provenance status, and protected state.
- Signed protected validation evidence.
- Act-/evidence-/scope-/nonce-/epoch-/state-/sink-bound finality authority.
- Proof-of-possession so copied authority alone is insufficient.
- Independent Finality Sink verification immediately before consequence.
- Single-use replay protection with in-memory and SQLite implementations.
- Fail-closed behavior for timeout, policy uncertainty, revocation uncertainty, stale epochs, invalid signatures, replay, substitution, and sink mismatch.
- HMAC-SHA-256 deterministic reference mode and Ed25519 asymmetric variation.
- MCP/tool, data egress, payment, GPU/accelerator egress, memory-write, computer-use, shell, and actuator test variations.
- 58 automated tests.
- Deterministic cryptographic vector generation.
- Reproducible microbenchmark with warm-up and p50/p95/p99 reporting.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[test]'
pytest
PYTHONPATH=src python run_reference.py
PYTHONPATH=src python benchmarks/benchmark_hot_path.py
```

## Current validation result

Reference package validation at creation time:

```text
58 tests collected
58 passed
```

See `benchmark_results.json` for the machine-readable benchmark output. The included benchmark is **software-only** and must not be represented as a TEE, HSM, DPU, SmartNIC, GPU, confidential-computing, network, or production-agent measurement.

## Implementation variations

| Dimension | Baseline | Variation | Production direction |
|---|---|---|---|
| PED authority authentication | HMAC-SHA-256 | Ed25519 | HSM/TEE-backed asymmetric signing |
| Non-bearer binding | HMAC proof-of-possession holder | replaceable holder registry | device/enclave key, mTLS/DPoP-like proof, hardware key |
| Replay state | in-memory lock | SQLite WAL | secure monotonic state / distributed transactional store |
| Policy | local `PolicyProfile` | hot/cold threshold | enterprise PDP, GNAP/OAuth inputs, RATS predicates |
| Finality Sink | Python boundary | consequence-specific sink IDs | MCP dispatcher, API gateway, payment switch, DB commit gate, DPU/GPU egress controller |
| Evidence | signed local structure | deterministic vector | sealed state, secure counter, Merkle commitment, LAVR-style record |
| Attestation | Boolean verifier result input | fail/allow tests | real RATS/EAT/vendor evidence verification |

## Latency

The Internet-Draft describes **1–20 ms** as representative industrial hot-path budgets in related implementations, explicitly as examples rather than protocol requirements.

This repository uses two separate notions:

1. **Reference CI target:** complete in-process software path p95 ≤ **5 ms** on a warmed local benchmark. This is only a regression target for this codebase.
2. **Deployment evaluation goal:** measure the actual protected local hot path against the deployment's latency envelope; 1–20 ms is a useful comparison band from the draft, not a conformance threshold.

Cold-path actions may involve remote policy, attestation, human approval, ledger/audit persistence, or higher-assurance checks. They are intentionally not assigned a false universal latency number. If required state is unavailable, the implementation escalates or denies; it never converts latency pressure into default permission.

## Important limitation

This repository demonstrates the **protocol state machine**. Running Python on a normal host does not create a hardware-rooted security boundary. See `LIMITATIONS.md`, `SECURITY.md`, and `IMPLEMENTATION_REFERENCE.md` before making deployment claims.

## Repository map

```text
src/execution_finality/
  models.py       Candidate Act, evidence, authority, proof, receipt
  canonical.py    deterministic serialization and SHA-256 digest
  crypto.py       HMAC + Ed25519 variants
  policy.py       PED predicates and hot/cold classification
  ped.py          first boundary: validate → evidence → authority
  holder.py       proof-of-possession non-bearer binding
  replay.py       in-memory + SQLite single-use stores
  sink.py         second boundary: independent verify → consume → effect
  errors.py       EF-xxx reference failure identifiers
  factory.py      reproducible test/example builders

tests/            58 automated tests
examples/         egress, accelerator, payment examples
benchmarks/       warm-up + latency distribution benchmark
vectors/          deterministic vector generator/output
configs/          example policy
IMPLEMENTATION_REFERENCE.md
SYSTEM_ENVIRONMENT.md
TEST_MATRIX.md
LIMITATIONS.md
SECURITY.md
NOTICE.md
docs/             source Internet-Draft + alignment map
```

## Status

Reference implementation for engineering discussion, interoperability testing, adversarial review, and standards-oriented experimentation. It is not an IETF standard or implementation certification.
