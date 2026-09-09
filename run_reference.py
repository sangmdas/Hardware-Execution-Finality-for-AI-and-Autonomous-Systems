from dataclasses import replace
from execution_finality import *

PED_KEY = b"reference-ped-key-change-me"
HOLDER_KEY = b"reference-holder-key-change-me"

act = make_candidate()
ctx = make_context(act)
policy = PolicyProfile(
    allowed_tools=frozenset({"customer-payment-api"}),
    allowed_destinations=frozenset({"payments-prod"}),
    allowed_consequence_classes=frozenset({ConsequenceClass.MCP_CALL}),
    allowed_purposes=frozenset({"customer-refund"}),
    max_precision="EXACT", max_amount=500, cold_path_amount=250,
    require_attestation=True)

authn = HMACAuthenticator(PED_KEY)
ped = ProtectedEnforcementDomain(authn, policy)
holder = ProtectedHolder("holder-1", HOLDER_KEY)
sink = FinalitySink("mcp-dispatcher", authn, HolderRegistry({"holder-1": HOLDER_KEY}), InMemoryReplayStore())

evidence, authority, cold = ped.validate_and_issue(act, ctx)
challenge = sink.challenge()
proof = holder.prove(authority, challenge)
receipt = sink.verify_and_effectuate(act, evidence, authority, proof, ctx, lambda a: print("EFFECT:", a.function_or_verb, a.arguments))
print("PATH:", "cold" if cold else "hot")
print("RECEIPT:", receipt)

# Demonstrate mutation denial.
mutated = replace(act, destination_id="attacker-endpoint")
try:
    sink2 = FinalitySink("mcp-dispatcher", authn, HolderRegistry({"holder-1": HOLDER_KEY}), InMemoryReplayStore())
    proof2 = holder.prove(authority, sink2.challenge())
    sink2.verify_and_effectuate(mutated, evidence, authority, proof2, ctx)
except FinalityDenied as e:
    print("EXPECTED DENIAL:", e)
