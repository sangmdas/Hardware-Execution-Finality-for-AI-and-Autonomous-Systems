# Alignment with the Internet-Draft

Source: `draft-das-hardware-enforced-execution-finality-01.xml` (9 September 2026).

| Draft concept | Reference code |
|---|---|
| Candidate Act / stable digest | `models.py`, `canonical.py` |
| Non-Effective State | control flow: no `effect_fn` before sink success |
| Protected Enforcement Domain | `ped.py` |
| Protected validation evidence | `ValidationEvidence` + PED signature |
| Scoped non-bearer finality authority | `FinalityAuthority` + `ProtectedHolder` proof-of-possession |
| Independent Finality Sink | `sink.py` |
| Single-use / replay | `replay.py` |
| Policy + revocation epochs | `policy.py`, `sink.py` |
| Hot/cold path | `PolicyProfile.cold_path_amount` and tests |
| Failure behavior | `errors.py` |
| Alternate-path closure | documented deployment requirement in `LIMITATIONS.md` |
| MCP/tool dispatch | default runnable example |
| Sensitive egress | `examples/precision_egress.py` |
| Accelerator egress | `examples/gpu_egress.py` |
| Payment/settlement | `examples/payment.py` |

The implementation deliberately does **not** convert PED approval into effectuation. The sink independently re-verifies signed state, candidate digest, epochs, destination, purpose, consequence class, precision, nonce, protected state, sink identity, holder proof, and replay state before invoking the effect callback.
