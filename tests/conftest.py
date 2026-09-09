import pytest
from execution_finality import *

@pytest.fixture
def stack():
    ped_key=b"test-ped-key"
    holder_key=b"test-holder-key"
    act=make_candidate()
    ctx=make_context(act)
    policy=PolicyProfile(
        allowed_tools=frozenset({"customer-payment-api"}),
        allowed_destinations=frozenset({"payments-prod"}),
        allowed_consequence_classes=frozenset({ConsequenceClass.MCP_CALL}),
        allowed_purposes=frozenset({"customer-refund"}),
        max_precision="EXACT", max_amount=500, cold_path_amount=250,
        require_attestation=True, require_provenance=True)
    authn=HMACAuthenticator(ped_key)
    ped=ProtectedEnforcementDomain(authn, policy)
    holder=ProtectedHolder("holder-1", holder_key)
    replay=InMemoryReplayStore()
    sink=FinalitySink("mcp-dispatcher", authn, HolderRegistry({"holder-1":holder_key}), replay)
    return act, ctx, policy, authn, ped, holder, replay, sink
