# Test Matrix

The automated suite covers the positive path plus adversarial mutations and deployment variations.

| Area | Representative checks |
|---|---|
| Candidate binding | tool, verb, MCP server, model, agent, destination, purpose, jurisdiction, nonce, precision, sink, protected state, arguments |
| Evidence | evidence signature, evidence-to-authority binding |
| Non-bearer property | wrong holder key, wrong holder identity, proof binding |
| Replay | in-memory single-use, SQLite persistence, concurrent atomic consume |
| Freshness | candidate expiry, authority expiry |
| Epochs | policy, revocation, authority, protected state |
| Policy | tool/destination/purpose/class/precision/amount/delegation |
| External predicates | attestation, provenance, policy availability, revocation availability, injected timeout |
| Path selection | hot/cold threshold boundaries |
| Crypto variations | HMAC-SHA-256, Ed25519 |
| Consequence variations | MCP, data export, payment, accelerator egress, memory write, computer use, shell, actuator |
| Failure catalog | uniqueness and coverage of EF identifiers implemented in the reference |

The suite intentionally tests that uncertainty is a denial condition, not a default-allow condition.
