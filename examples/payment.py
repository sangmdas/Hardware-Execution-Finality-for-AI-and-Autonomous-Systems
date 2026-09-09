from execution_finality import *

for amount in (50, 300):
    act = make_candidate(arguments={"amount":amount,"currency":"USD"})
    ctx = make_context(act)
    policy = PolicyProfile(frozenset({"customer-payment-api"}), frozenset({"payments-prod"}),
        frozenset({ConsequenceClass.MCP_CALL}), frozenset({"customer-refund"}), max_amount=500, cold_path_amount=250)
    ped = ProtectedEnforcementDomain(HMACAuthenticator(b"ped"), policy)
    _, _, cold = ped.validate_and_issue(act, ctx)
    print(amount, "cold-path" if cold else "hot-path")
