from dataclasses import replace
from execution_finality import *

act = make_candidate(
    act_type="DATA_EXPORT", tool_id="field-search", mcp_server_id="search-mcp",
    function_or_verb="find_technicians", purpose="dispatch-discovery",
    consequence_class=ConsequenceClass.DATA_EXPORT,
    destination_id="search-provider-X", data_precision="REGION",
    arguments={"region":"zone-7"}, finality_sink_id="egress-controller")
ctx = make_context(act)
policy = PolicyProfile(frozenset({"field-search"}), frozenset({"search-provider-X"}),
                       frozenset({ConsequenceClass.DATA_EXPORT}), frozenset({"dispatch-discovery"}),
                       max_precision="REGION")
a = HMACAuthenticator(b"ped")
h = ProtectedHolder("holder-1", b"holder")
ped = ProtectedEnforcementDomain(a, policy)
sink = FinalitySink("egress-controller", a, HolderRegistry({"holder-1":b"holder"}), InMemoryReplayStore())
ev, auth, _ = ped.validate_and_issue(act, ctx)
proof = h.prove(auth, sink.challenge())
print(sink.verify_and_effectuate(act, ev, auth, proof, ctx))

# Exact-location substitution is denied because the act digest changes.
try:
    exact = replace(act, data_precision="EXACT", arguments={"lat":20.1,"lon":86.7})
    sink2 = FinalitySink("egress-controller", a, HolderRegistry({"holder-1":b"holder"}), InMemoryReplayStore())
    sink2.verify_and_effectuate(exact, ev, auth, h.prove(auth, sink2.challenge()), ctx)
except FinalityDenied as e:
    print("EXPECTED:", e)
