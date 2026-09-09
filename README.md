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

# LICENSE

## Copyright License — CC BY-NC 4.0

Copyright © 2026 Sangam Das. All rights reserved except as expressly licensed below.

Unless otherwise expressly stated, the documentation, explanatory material, diagrams, test vectors, reference implementation material, and other copyrightable content in this repository are made available under the:

**Creative Commons Attribution-NonCommercial 4.0 International License (CC BY-NC 4.0).**

This permits copying, redistribution, adaptation, research, testing, evaluation, citation, and other uses permitted by CC BY-NC 4.0, provided that:

1. appropriate attribution is provided;
2. the use is non-commercial; and
3. the applicable CC BY-NC 4.0 terms are complied with.

License text:

https://creativecommons.org/licenses/by-nc/4.0/

---

# Patent Rights

The CC BY-NC 4.0 copyright license does **not** grant any license, covenant, waiver, exhaustion, or other right under any patent or patent application.

Certain architectures, mechanisms, methods, protocol elements, terminology, implementations, or combinations described or demonstrated in this repository may be associated with pending patent applications or other patent rights of Sangam Das, including applications within the DAS Protocols family.

Except for the express standards-related commitment stated below, **all patent rights are reserved**.

Publication of source code, documentation, test vectors, examples, benchmarks, protocol descriptions, Internet-Drafts, research materials, or other material in this repository does not constitute an unrestricted patent license.

---

# IETF Standardization and FRAND Commitment

If a patent claim owned or controlled by Sangam Das becomes **essential to implementation of a specification formally adopted or standardized through the IETF**, such essential patent claim will be made available to implementers of that IETF standard on **Fair, Reasonable and Non-Discriminatory (FRAND) terms**, subject to a separate applicable patent license.

This commitment applies only to patent claims that are actually essential to implementation of the relevant standardized specification.

It does not automatically extend to:

* optional implementations that are not required by the standard;
* proprietary extensions;
* non-standardized embodiments;
* alternative applications of the technology;
* implementations outside the scope of the standardized specification;
* claims that can be avoided while still conforming to the standard; or
* other patent claims that are not essential to implementation of the adopted IETF specification.

Any FRAND patent license may include reasonable terms concerning scope, field of use, reciprocity, defensive suspension, royalties, reporting, sublicensing, assignment, compliance, and other customary licensing provisions, provided that the resulting terms remain fair, reasonable, and non-discriminatory for similarly situated implementers.

---

# No Royalty-Free Commitment Unless Expressly Stated

Nothing in this repository constitutes a commitment to provide patent rights on a royalty-free basis.

**FRAND does not mean royalty-free unless expressly agreed in writing.**

No royalty-free patent license, covenant not to sue, patent non-assertion commitment, or patent waiver arises merely because material is:

* published on GitHub;
* submitted to the IETF;
* discussed on an IETF mailing list;
* included in an Internet-Draft;
* referenced by an RFC;
* used in a reference implementation;
* published through Zenodo or another research repository; or
* made available under CC BY-NC 4.0.

---

# No Waiver

Nothing in this repository, its publication, distribution, discussion, testing, contribution, standardization activity, or public availability shall be interpreted as:

* a waiver of patent rights;
* a waiver of pending or future patent claims;
* an abandonment of intellectual-property rights;
* an implied patent license;
* an implied covenant not to sue;
* a dedication of patent rights to the public;
* consent to commercial implementation;
* patent exhaustion beyond that required by applicable law;
* a waiver of the right to seek royalties or other consideration; or
* a waiver of any right to enforce patents that are not subject to an applicable standards commitment.

All rights not expressly granted are reserved.

---

# Reference Implementation Does Not Expand the Patent License

The reference implementation is provided to facilitate:

* technical evaluation;
* interoperability research;
* protocol experimentation;
* security analysis;
* reproducibility;
* academic and standards-related review; and
* non-commercial testing.

The availability of executable source code does not enlarge the copyright license or create any patent license beyond the express commitments contained in this notice.

A technically equivalent implementation, reimplementation in another programming language, hardware implementation, firmware implementation, protocol-compatible implementation, clean-room implementation, or independently written implementation may still require a patent license if it practices an applicable patent claim.

---

# Commercial Use

Commercial use of copyrightable material covered by CC BY-NC 4.0 is not authorized by that license.

Organizations seeking:

* commercial implementation rights;
* production deployment rights;
* commercial redistribution rights;
* commercial integration rights; or
* patent licenses outside an applicable IETF FRAND standards commitment

should obtain a separate written license from the rights holder.

---

# IETF Intellectual Property Procedures

Any disclosure or licensing statement submitted in connection with IETF standardization should be interpreted together with the applicable IETF intellectual-property policies and the specific IETF IPR disclosure made for the relevant contribution.

This repository notice does not replace any disclosure that may be required under applicable IETF procedures.

Where a specific IETF IPR disclosure contains a more specific licensing commitment for a particular patent, application, contribution, or specification, that specific commitment governs to the extent applicable.

---

# No Endorsement or Certification

Publication of this implementation does not imply endorsement, approval, certification, or adoption by the IETF, IESG, IAB, any standards organization, regulator, governmental institution, technology company, or other third party.

---

## Summary

**Copyright:** CC BY-NC 4.0
**Commercial copyright use:** Separate permission required
**General patent license:** Not granted
**IETF-essential patent claims:** Available on FRAND terms if and when applicable
**Royalty-free commitment:** None unless separately stated in writing
**Non-essential patent claims:** All rights reserved
**Implied patent licenses:** None
**Patent waiver:** None

