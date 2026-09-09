# Security Notes

This repository is a runnable **reference model**, not a claim that Python process memory is a Protected Enforcement Domain.

Security properties demonstrated in code:

- Candidate Acts are canonicalized and cryptographically digested.
- PED validation and Finality Sink verification are separate operations.
- Protected validation evidence is created before finality authority.
- Finality authority is bound to candidate digest, evidence, purpose, consequence class, destination, precision, nonce, epochs, protected state, sink identity, and holder key identity.
- A copied authority is insufficient without holder proof-of-possession.
- Authority is single-use through an atomic replay store.
- Policy/revocation/protected-state changes after issuance cause denial.
- Timeouts and unavailable policy/revocation state fail closed.

Production replacements are required for software-held keys, protected monotonic state, attestation verification, transactional effectuation, and real hardware consequence boundaries.
