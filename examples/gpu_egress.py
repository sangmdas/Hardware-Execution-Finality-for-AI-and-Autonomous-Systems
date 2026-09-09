from execution_finality import *

act = make_candidate(
    act_type="ACCELERATOR_EGRESS", tool_id="gpu-egress", mcp_server_id="",
    function_or_verb="release_output", purpose="approved-inference-egress",
    consequence_class=ConsequenceClass.ACCELERATOR_EGRESS,
    resource_or_data_class="model-output", destination_id="host-bounce-buffer",
    finality_sink_id="dpu-egress-controller", arguments={"buffer_digest":"abc123"})
ctx = make_context(act)
policy = PolicyProfile(frozenset({"gpu-egress"}), frozenset({"host-bounce-buffer"}),
    frozenset({ConsequenceClass.ACCELERATOR_EGRESS}), frozenset({"approved-inference-egress"}), require_attestation=True)
a = HMACAuthenticator(b"ped")
h = ProtectedHolder("holder-1", b"holder")
ped = ProtectedEnforcementDomain(a, policy)
sink = FinalitySink("dpu-egress-controller", a, HolderRegistry({"holder-1":b"holder"}), InMemoryReplayStore())
ev, auth, _ = ped.validate_and_issue(act, ctx)
print(sink.verify_and_effectuate(act, ev, auth, h.prove(auth, sink.challenge()), ctx,
      lambda _: print("SIMULATED: transmit-enable released")))
