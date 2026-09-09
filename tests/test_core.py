from dataclasses import replace
import pytest
from execution_finality import *


def issue(stack):
    act,ctx,policy,authn,ped,holder,replay,sink=stack
    ev,au,cold=ped.validate_and_issue(act,ctx)
    proof=holder.prove(au,sink.challenge())
    return act,ctx,ev,au,proof,cold,sink

def test_happy_path_effects_once(stack):
    act,ctx,ev,au,proof,cold,sink=issue(stack)
    effects=[]
    r=sink.verify_and_effectuate(act,ev,au,proof,ctx,lambda a: effects.append(a.candidate_act_id))
    assert r.authority_id==au.authority_id and effects==[act.candidate_act_id] and cold is False

def test_replay_denied(stack):
    act,ctx,ev,au,proof,_,sink=issue(stack)
    sink.verify_and_effectuate(act,ev,au,proof,ctx)
    with pytest.raises(FinalityDenied) as x: sink.verify_and_effectuate(act,ev,au,proof,ctx)
    assert x.value.code==EFCode.AUTHORITY_ALREADY_USED

def test_wrong_holder_key_denied(stack):
    act,ctx,ev,au,_,_,sink=issue(stack)
    bad=ProtectedHolder("holder-1",b"wrong").prove(au,sink.challenge())
    with pytest.raises(FinalityDenied) as x: sink.verify_and_effectuate(act,ev,au,bad,ctx)
    assert x.value.code==EFCode.INVALID_AUTHORITY

def test_wrong_holder_id_denied(stack):
    act,ctx,ev,au,_,_,sink=issue(stack)
    bad=ProtectedHolder("holder-x",b"x").prove(au,sink.challenge())
    with pytest.raises(FinalityDenied) as x: sink.verify_and_effectuate(act,ev,au,bad,ctx)
    assert x.value.code==EFCode.INVALID_AUTHORITY

def test_expired_at_sink_denied(stack):
    act,ctx,ev,au,proof,_,sink=issue(stack)
    later=replace(ctx,now=au.expires_at+0.001)
    with pytest.raises(FinalityDenied) as x: sink.verify_and_effectuate(act,ev,au,proof,later)
    assert x.value.code==EFCode.STALE_AUTHORITY

def test_policy_epoch_change_denied(stack):
    act,ctx,ev,au,proof,_,sink=issue(stack)
    with pytest.raises(FinalityDenied) as x: sink.verify_and_effectuate(act,ev,au,proof,replace(ctx,policy_epoch=ctx.policy_epoch+1))
    assert x.value.code==EFCode.POLICY_EPOCH_MISMATCH

def test_revocation_epoch_change_denied(stack):
    act,ctx,ev,au,proof,_,sink=issue(stack)
    with pytest.raises(FinalityDenied) as x: sink.verify_and_effectuate(act,ev,au,proof,replace(ctx,revocation_epoch=ctx.revocation_epoch+1))
    assert x.value.code==EFCode.REVOCATION_STATE_MISMATCH

def test_protected_state_change_denied(stack):
    act,ctx,ev,au,proof,_,sink=issue(stack)
    with pytest.raises(FinalityDenied) as x: sink.verify_and_effectuate(act,ev,au,proof,replace(ctx,protected_state_ref="rollback"))
    assert x.value.code==EFCode.PROTECTED_STATE_MISMATCH

def test_authority_epoch_change_denied(stack):
    act,ctx,ev,au,proof,_,sink=issue(stack)
    with pytest.raises(FinalityDenied) as x: sink.verify_and_effectuate(act,ev,au,proof,replace(ctx,authority_epoch=ctx.authority_epoch+1))
    assert x.value.code==EFCode.INVALID_AUTHORITY

@pytest.mark.parametrize("field,value",[
    ("destination_id","attacker"),("purpose","other-purpose"),("data_precision","REGION"),
    ("nonce","changed"),("tool_id","other-tool"),("function_or_verb","delete_all"),
    ("mcp_server_id","evil-mcp"),("model_id","new-model"),("agent_id","other-agent"),
    ("finality_sink_id","other-sink"),("jurisdiction","ZZ"),("protected_state_ref","other-state")])
def test_load_bearing_candidate_mutations_fail_digest(stack,field,value):
    act,ctx,ev,au,proof,_,sink=issue(stack)
    mutated=replace(act,**{field:value})
    with pytest.raises(FinalityDenied): sink.verify_and_effectuate(mutated,ev,au,proof,ctx)

def test_argument_substitution_fails(stack):
    act,ctx,ev,au,proof,_,sink=issue(stack)
    mutated=replace(act,arguments={"amount":5000,"currency":"USD","customer_id":"18422"})
    with pytest.raises(FinalityDenied) as x: sink.verify_and_effectuate(mutated,ev,au,proof,ctx)
    assert x.value.code==EFCode.ACT_MISMATCH

def test_tampered_authority_signature_denied(stack):
    act,ctx,ev,au,proof,_,sink=issue(stack)
    bad=replace(au,signature="00"+au.signature[2:])
    with pytest.raises(FinalityDenied) as x: sink.verify_and_effectuate(act,ev,bad,proof,ctx)
    assert x.value.code==EFCode.INVALID_AUTHORITY

def test_tampered_evidence_signature_denied(stack):
    act,ctx,ev,au,proof,_,sink=issue(stack)
    bad=replace(ev,signature="00"+ev.signature[2:])
    with pytest.raises(FinalityDenied) as x: sink.verify_and_effectuate(act,bad,au,proof,ctx)
    assert x.value.code==EFCode.INVALID_AUTHORITY

def test_sink_substitution_denied(stack):
    act,ctx,ev,au,proof,_,_=issue(stack)
    _,_,_,authn,_,holder,_,_=stack
    wrong=FinalitySink("shell-bridge",authn,HolderRegistry({"holder-1":holder.key}),InMemoryReplayStore())
    with pytest.raises(FinalityDenied) as x: wrong.verify_and_effectuate(act,ev,au,holder.prove(au,wrong.challenge()),ctx)
    assert x.value.code==EFCode.SINK_MISMATCH
