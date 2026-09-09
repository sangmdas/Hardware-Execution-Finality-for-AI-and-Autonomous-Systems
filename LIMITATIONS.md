# Limitations

1. **Not a hardware security boundary.** The default PED, holder, and sink are Python objects in one process. This demonstrates protocol mechanics only. A production implementation must place the relevant keys/state/checks in a TEE, HSM, secure enclave, protected OS service, secure controller, DPU/SmartNIC, accelerator security domain, or equivalent protected mechanism.
2. **HMAC baseline is pedagogical.** It is deterministic and convenient for vectors, but it implies shared-secret verification. The repository also contains an Ed25519 variation. Production key lifecycle, rotation, hardware isolation, certificate chains, and remote attestation are out of scope.
3. **Proof-of-possession is simulated.** The holder key is process memory. In production it should be non-exportable or hardware/protected-runtime bound.
4. **Attestation is a predicate input, not a verifier implementation.** `attestation_ok` models the result of an external verifier (e.g., RATS/EAT/vendor attestation). This repository does not parse or validate real evidence formats.
5. **Effectuation atomicity has a boundary.** Replay-state consumption occurs before `effect_fn`. A real payment/database/device boundary needs a transaction, idempotency key, commit protocol, or hardware atomicity so a crash cannot produce ambiguous consume/effect state.
6. **Alternate-path closure cannot be proven by a library.** Every path capable of the protected consequence must be routed through an enforcing sink. Direct API, shell, browser, IPC, alternate plugin, memory-write, DMA, and other bypass paths are deployment properties.
7. **Policy is intentionally small.** The example policy engine covers tool, destination, purpose, consequence class, precision, amount, delegation depth, attestation, provenance, epochs, and availability. It is not a complete enterprise policy language.
8. **No network or distributed consensus model.** Cluster-wide replay, cross-region revocation consistency, clock synchronization, HSM quorum, and consensus are not implemented.
9. **No formal verification.** The implementation is executable and tested but not mechanically proven.
10. **Failure-code precedence is implementation-specific.** A mutation may fail first as `EF-010 ACT_MISMATCH` even when a more specific mismatch (destination/precision/etc.) is also true.
11. **Benchmark results are local software measurements only.** They are not TEE, HSM, SmartNIC, DPU, GPU, network, ledger, or production-agent benchmarks.
12. **No legal/compliance determination.** Passing the technical reference checks does not itself establish legal compliance, safety certification, or regulatory conformity.
