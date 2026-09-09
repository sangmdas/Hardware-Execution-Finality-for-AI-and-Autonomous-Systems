# Detailed Implementation Reference

## 1. Purpose

This file documents the runnable implementation corresponding to the execution-finality architecture in `draft-das-hardware-enforced-execution-finality-01`.

The security objective is narrow and testable:

> A consequence-bearing Candidate Act remains non-effective unless current, act-specific, scoped authority is validated and independently verified at the consequence boundary.

The implementation therefore separates **computation**, **PED validation**, and **effectuation**. A valid model output, tool selection, connector allowlist, session permission, valid signature, or PED allow result is not independently sufficient to execute the consequence.

---

## 2. Reference state machine

```text
GENERATED
   │
   ▼
CANDIDATE_ACT / NON_EFFECTIVE
   │
   ├── malformed / stale / policy failure ───────────────► DENIED
   │
   ▼
PED_VALIDATING
   │
   ├── predicate failure ────────────────────────────────► DENIED
   │
   ▼
VALIDATION_EVIDENCE_COMMITTED
   │
   ▼
SCOPED_NON_BEARER_AUTHORITY_ISSUED
   │
   ▼
FINALITY_SINK_VERIFYING
   │
   ├── signature / digest / epoch / scope / PoP failure ► DENIED
   │
   ├── replay / consumed authority ─────────────────────► DENIED
   │
   ▼
AUTHORITY_ATOMICALLY_CONSUMED
   │
   ▼
EFFECTUATED
```

No code path intentionally calls `effect_fn` before sink verification and single-use consumption.

---

## 3. System language and software environment

### Primary language

- Python **3.11 or later**.
- Creation/validation environment recorded in `benchmark_results.json`: Python 3.13.5 on x86_64 Linux.

### Libraries

- Python standard library: dataclasses, enum, hashlib, hmac, sqlite3, threading, time, uuid, json.
- `cryptography`: Ed25519 asymmetric signing variation.
- `pytest`: automated validation suite.

### Why this language was chosen

The reference objective is inspectability of state transitions, not production throughput. Python allows reviewers to see precisely where authority is issued, where it is checked, what fields are bound, and when the consequence callback becomes reachable.

Production implementations may reasonably use Rust, C/C++, Go, Java, protected OS services, enclave code, HSM integrations, SmartNIC/DPU services, firmware, or accelerator-runtime components.

---

## 4. Candidate Act parameters implemented

The reference object includes:

- version
- candidate_act_id
- act_type
- initiator_id
- application_id
- agent_id
- model_id
- model_or_runtime_state_ref
- tool_id
- mcp_server_id
- function_or_verb
- instruction_provenance
- purpose
- permitted_scope
- consequence_class
- arguments
- resource_or_data_class
- destination_id
- jurisdiction
- data_precision
- nonce
- creation_time
- expiration_time
- policy_epoch
- authority_epoch
- revocation_epoch
- protected_state_ref
- finality_sink_id
- effectuation_boundary_id

The complete Candidate Act is canonicalized and SHA-256 digested. Mutating a load-bearing field after issuance invalidates the binding.

---

## 5. First boundary: Protected Enforcement Domain

`ProtectedEnforcementDomain.validate_and_issue()` performs the reference PED sequence.

### Predicate set

The example policy can check:

- policy and revocation availability;
- Candidate Act freshness;
- policy epoch;
- revocation epoch;
- protected-state reference;
- attestation result;
- instruction-provenance result;
- tool identity;
- destination;
- purpose;
- consequence class;
- precision ceiling;
- amount ceiling;
- delegation depth;
- optional hot/cold classification.

### Evidence-before-authority order

The code constructs and authenticates `ValidationEvidence` before constructing the finality authority. The authority then cryptographically binds the evidence digest.

The Candidate Act remains non-effective after successful PED processing.

---

## 6. Scoped non-bearer authority

The reference `FinalityAuthority` binds:

- candidate digest;
- validation-evidence digest;
- sink ID;
- purpose;
- permitted scope;
- consequence class;
- destination;
- jurisdiction;
- data precision;
- nonce;
- policy epoch;
- authority epoch;
- revocation epoch;
- protected state;
- holder-key identity;
- issuance and expiration time.

### Why it is not modeled as a bearer token

The authority does not contain everything needed to use itself. The sink requires a separate `HolderProof` generated with a key not serialized in the authority.

A copied authority therefore fails without the holder key. In a production deployment, that holder key should be non-exportable and bound to the appropriate process, device, enclave, workload identity, session, or hardware root.

The HMAC holder is a simple reference mechanism. It is not proposed as the only production construction.

---

## 7. Second boundary: Finality Sink

`FinalitySink.verify_and_effectuate()` independently checks, immediately before the callback:

1. Candidate and authority sink identity.
2. Validation-evidence integrity.
3. Authority integrity.
4. Candidate digest match.
5. Evidence-to-authority binding.
6. Candidate/authority freshness.
7. Current policy epoch.
8. Current revocation epoch.
9. Current authority epoch.
10. Current protected state.
11. Destination binding.
12. Purpose binding.
13. Consequence-class binding.
14. Precision binding.
15. Nonce binding.
16. Holder identity binding.
17. Holder proof-of-possession.
18. Single-use replay state.

Only after those checks does the implementation call `effect_fn`.

---

## 8. Implementation variations

### V1 — HMAC reference mode

Purpose: deterministic, easy-to-review test mode.

- PED evidence and authority: HMAC-SHA-256.
- Holder proof: HMAC-SHA-256.
- Strength: deterministic vectors, no PKI required.
- Limitation: shared secret must exist at verifier; not a recommended internet-scale trust distribution model.

### V2 — Ed25519 PED authority

Purpose: demonstrate separation of issuer signing from sink verification.

- PED uses Ed25519 private key.
- Finality Sink uses only public verification key.
- Holder proof remains replaceable in the current sample.

Production extension: place the signing key in HSM/TEE/enclave and bind public key/certificate to attested PED identity.

### V3 — In-memory replay store

Purpose: lowest-overhead local tests and benchmark.

- lock-protected set;
- atomic single-process consume;
- no crash persistence.

### V4 — SQLite replay store

Purpose: local persistence and concurrency demonstration.

- WAL mode;
- `authority_id` primary key;
- atomic unique insertion;
- survives process restart on the same storage.

Not a replacement for hardware monotonic state or distributed consensus.

### V5 — Consequence-boundary variations

The automated suite instantiates:

- MCP call;
- data export;
- payment;
- accelerator egress;
- memory write;
- computer use;
- shell execution;
- actuator command.

The code does not assume that the Finality Sink must be in one physical location. What matters is that it controls the protected consequence and cannot be bypassed for that consequence.

### V6 — Hot and cold path

The example policy classifies high-value actions above a configured threshold as cold-path candidates. Hot-path classification does **not** bypass the sink.

A real implementation can add cold-path predicates such as:

- fresh remote attestation;
- human approval;
- sanctions/counterparty refresh;
- new-tool review;
- policy-bundle fetch;
- external ledger/audit commit;
- higher-assurance provenance analysis.

---

## 9. Testing parameters

### Automated suite

- Framework: pytest.
- Collected tests at package creation: **58**.
- Result: **58 passed**.
- Test categories are listed in `TEST_MATRIX.md`.

### Mutation parameters

The suite varies load-bearing Candidate Act attributes including:

- destination;
- purpose;
- precision;
- nonce;
- tool;
- verb;
- MCP server;
- model;
- agent;
- sink;
- jurisdiction;
- protected state;
- argument set / amount.

### Runtime-failure parameters

The suite also injects:

- expired Candidate Act;
- expired authority;
- changed policy epoch;
- changed revocation epoch;
- changed authority epoch;
- changed protected state;
- attestation failure;
- instruction-provenance failure;
- policy state unavailable;
- revocation state unavailable;
- validation timeout;
- wrong holder key;
- wrong holder identity;
- invalid evidence signature;
- invalid authority signature;
- replay;
- wrong Finality Sink.

### Boundary parameters

Hot/cold threshold tests include values below, exactly at, and above the configured threshold.

Replay tests include concurrent attempts to consume the same authority using both in-memory and SQLite stores. Exactly one consume is expected to succeed.

---

## 10. Benchmark parameters

`benchmarks/benchmark_hot_path.py` measures:

- PED validation + evidence + authority issuance;
- holder proof-of-possession generation;
- Finality Sink verification + atomic in-memory consume;
- complete local path.

Default parameters:

```text
warm-up iterations: 500
measured iterations: 5000
reference CI p95 target: 5.0 ms
GC: disabled during timed loop after explicit collection
network calls: none
external database: none
external ledger: none
real consequence I/O: none
crypto mode: HMAC-SHA-256 reference mode
replay mode: in-memory lock
```

The benchmark records p50, p95, p99, mean, minimum, and maximum latency for each stage.

---

## 11. Measured creation-time result

The machine-readable result is in `benchmark_results.json`.

At repository creation, the complete software-only local path measured approximately:

```text
PED issue                 p50 0.194 ms   p95 0.234 ms
Holder proof              p50 0.019 ms   p95 0.021 ms
Sink verify + consume     p50 0.170 ms   p95 0.210 ms
Total hot path            p50 0.394 ms   p95 0.458 ms
```

Environment:

```text
Python 3.13.5
Linux x86_64
Intel Xeon Platinum 8370C @ 2.80 GHz
500 warm-up + 5000 measured iterations
```

These are **not hardware-enforcement measurements**. They quantify only this local software reference implementation.

---

## 12. Latency targets and interpretation

### Target A — Reference-code regression target

For the included HMAC + in-memory replay configuration:

```text
p95 complete local path <= 5 ms
```

This is a repository regression threshold, not a protocol requirement.

### Target B — Protected hot-path deployment evaluation

The accompanying draft cites **1–20 ms** as representative industrial hot-path budgets in related implementations and explicitly says those numbers are examples, not protocol requirements.

A real deployment should therefore record:

- p50/p95/p99 PED latency;
- p50/p95/p99 sink latency;
- attestation cache hit/miss latency;
- HSM/enclave transition latency;
- secure persistent replay-state latency;
- policy cache hit/miss latency;
- revocation refresh latency;
- network hop latency if the sink is remote;
- end-to-end consequence latency.

No latency target is allowed to change fail-closed behavior. A timeout, cache miss, policy miss, network failure, or revocation uncertainty is an escalation/denial condition, not permission.

### Cold path

There is deliberately no universal cold-path number. A cold path may include external systems whose latency varies by deployment. It should have an explicit service-level objective and timeout policy, but timeout must fail closed or escalate.

---

## 13. Failure codes implemented

The reference catalog includes:

```text
EF-001 MALFORMED_ACT
EF-002 NO_FINALITY_AUTHORITY
EF-003 INVALID_AUTHORITY
EF-004 STALE_AUTHORITY
EF-005 AUTHORITY_ALREADY_USED
EF-006 REPLAY_DETECTED
EF-007 NONCE_FAILURE
EF-010 ACT_MISMATCH
EF-012 SCOPE_MISMATCH
EF-013 PURPOSE_MISMATCH
EF-014 CONSEQUENCE_CLASS_MISMATCH
EF-020 DESTINATION_MISMATCH
EF-021 JURISDICTION_MISMATCH
EF-023 PRECISION_MISMATCH
EF-030 POLICY_EPOCH_MISMATCH
EF-031 REVOCATION_STATE_MISMATCH
EF-032 PROTECTED_STATE_MISMATCH
EF-040 SINK_MISMATCH
EF-050 ATTESTATION_FAILURE
EF-053 INSTRUCTION_PROVENANCE_FAILURE
EF-060 VALIDATION_TIMEOUT
EF-061 AUTHORITY_UNCERTAIN
EF-070 ESCALATION_REQUIRED
EF-071 HUMAN_REVIEW_REQUIRED
EF-080 FAIL_CLOSED
```

The identifiers are implementation/reference labels, not IANA assignments.

---

## 14. Deterministic vectors

`vectors/deterministic_vectors.json` contains:

- a fixed Candidate Act;
- canonical serialized object;
- expected SHA-256 digest;
- expected HMAC-SHA-256 tag using a public test key.

The vector key is test material and must never be reused in deployment.

This vector allows another language implementation to confirm canonicalization and digest compatibility before attempting full interoperability.

---

## 15. Limitations that must be disclosed with results

### Hardware boundary

Python process isolation is not a TEE, secure enclave, HSM, protected controller, or accelerator security domain.

### Key protection

Reference HMAC and holder keys live in process memory. Production keys require hardware/protected-runtime lifecycle controls.

### Attestation

The implementation consumes an `attestation_ok` result but does not implement a RATS verifier, EAT parser, vendor endorsement validation, certificate path, or attestation freshness protocol.

### Atomicity

Authority consumption is atomic with respect to the replay store, but a generic Python callback cannot guarantee atomicity with an arbitrary external system. Payment/database/device deployments need transactional coupling, idempotency, or hardware commit semantics.

### Alternate-path closure

The library cannot prove that a deployment has no bypass. Direct API calls, shell, browser, computer-use, IPC, alternate plugins, memory writes, DMA, device paths, or privileged administrators may provide alternate routes unless the system architecture closes them.

### Distributed state

The sample does not solve distributed replay consensus, multi-region revocation races, cross-HSM state synchronization, clock trust, or quorum availability.

### Policy completeness

The included policy profile is intentionally small and reviewable. It is not a general authorization language or regulatory rules engine.

### Formal verification

Passing 58 tests is evidence of exercised behavior, not a mathematical proof of security.

### Legal status

The implementation does not certify GDPR, EU AI Act, CRA, financial, safety, or other legal compliance.

---

## 16. Suggested production test expansion

Before production use, add at least:

1. real TEE/HSM/secure-controller key tests;
2. attestation freshness and endorsement-chain tests;
3. reboot/rollback tests;
4. power-loss tests between consume and effect;
5. clock rollback and skew tests;
6. multi-node replay races;
7. network partition tests;
8. stale policy-cache tests;
9. stale revocation-cache tests;
10. holder-key rotation and compromise tests;
11. sink-key rotation tests;
12. policy epoch rollover tests;
13. candidate canonicalization interoperability vectors across languages;
14. fuzzing of serializers and malformed acts;
15. high-concurrency soak testing;
16. side-channel analysis appropriate to the selected hardware root;
17. alternate-path red-team testing;
18. MCP verb/schema mutation tests;
19. computer-use bypass tests;
20. DPU/GPU DMA and egress bypass tests where applicable.

---

## 17. Interoperability profile candidates for future work

This repository intentionally leaves wire standardization open. A future interoperability profile could standardize:

- Candidate Act canonical encoding;
- evidence envelope;
- finality-authority envelope;
- holder proof format;
- sink challenge format;
- consequence-class registry;
- EF failure identifiers;
- epoch semantics;
- authority consumption semantics;
- attestation-binding claims;
- replay-state requirements;
- hot/cold escalation signaling.

Those items should be standardized only after implementation experience establishes which fields must be mandatory across domains.

---

## 18. Reproduction commands

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[test]'

pytest
PYTHONPATH=src python run_reference.py
PYTHONPATH=src python examples/precision_egress.py
PYTHONPATH=src python examples/gpu_egress.py
PYTHONPATH=src python examples/payment.py
PYTHONPATH=src python vectors/generate_vectors.py
PYTHONPATH=src python benchmarks/benchmark_hot_path.py
```

For reproducible benchmark comparison, record the raw JSON result with OS/kernel, CPU, Python version, crypto mode, replay store, warm-up count, sample count, and whether real protected hardware was used.
