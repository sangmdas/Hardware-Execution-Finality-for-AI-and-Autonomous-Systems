from dataclasses import replace
import pytest
from execution_finality import *

@pytest.mark.parametrize("mutation,code",[
    ({"tool_id":"unknown"},EFCode.SCOPE_MISMATCH),
    ({"destination_id":"unknown"},EFCode.DESTINATION_MISMATCH),
    ({"purpose":"fraud"},EFCode.PURPOSE_MISMATCH),
    ({"data_precision":"IMPOSSIBLY_HIGH"},EFCode.PRECISION_MISMATCH),
])
def test_policy_basic_denials(stack,mutation,code):
    act,ctx,_,_,ped,_,_,_=stack
    with pytest.raises(FinalityDenied) as x: ped.validate_and_issue(replace(act,**mutation),ctx)
    assert x.value.code==code

def test_consequence_class_denied(stack):
    act,ctx,_,_,ped,_,_,_=stack
    with pytest.raises(FinalityDenied) as x: ped.validate_and_issue(replace(act,consequence_class=ConsequenceClass.PAYMENT),ctx)
    assert x.value.code==EFCode.CONSEQUENCE_CLASS_MISMATCH

def test_amount_limit_denied(stack):
    act,ctx,_,_,ped,_,_,_=stack
    with pytest.raises(FinalityDenied) as x: ped.validate_and_issue(replace(act,arguments={"amount":501}),ctx)
    assert x.value.code==EFCode.SCOPE_MISMATCH

def test_delegation_depth_denied(stack):
    act,ctx,_,_,ped,_,_,_=stack
    with pytest.raises(FinalityDenied) as x: ped.validate_and_issue(replace(act,arguments={"amount":50,"delegation_depth":4}),ctx)
    assert x.value.code==EFCode.SCOPE_MISMATCH

def test_attestation_denied(stack):
    act,ctx,_,_,ped,_,_,_=stack
    with pytest.raises(FinalityDenied) as x: ped.validate_and_issue(act,replace(ctx,attestation_ok=False))
    assert x.value.code==EFCode.ATTESTATION_FAILURE

def test_provenance_denied(stack):
    act,ctx,_,_,ped,_,_,_=stack
    with pytest.raises(FinalityDenied) as x: ped.validate_and_issue(act,replace(ctx,provenance_ok=False))
    assert x.value.code==EFCode.INSTRUCTION_PROVENANCE_FAILURE

@pytest.mark.parametrize("field",["policy_available","revocation_available"])
def test_uncertain_state_fails_closed(stack,field):
    act,ctx,_,_,ped,_,_,_=stack
    with pytest.raises(FinalityDenied) as x: ped.validate_and_issue(act,replace(ctx,**{field:False}))
    assert x.value.code==EFCode.AUTHORITY_UNCERTAIN

def test_timeout_fails_closed(stack):
    act,ctx,_,_,ped,_,_,_=stack
    with pytest.raises(FinalityDenied) as x: ped.validate_and_issue(act,replace(ctx,force_timeout=True))
    assert x.value.code==EFCode.VALIDATION_TIMEOUT

def test_stale_candidate_denied(stack):
    act,ctx,_,_,ped,_,_,_=stack
    with pytest.raises(FinalityDenied) as x: ped.validate_and_issue(act,replace(ctx,now=act.expiration_time+1))
    assert x.value.code==EFCode.STALE_AUTHORITY

def test_candidate_policy_epoch_stale(stack):
    act,ctx,_,_,ped,_,_,_=stack
    with pytest.raises(FinalityDenied) as x: ped.validate_and_issue(replace(act,policy_epoch=480),ctx)
    assert x.value.code==EFCode.POLICY_EPOCH_MISMATCH

def test_candidate_revocation_epoch_stale(stack):
    act,ctx,_,_,ped,_,_,_=stack
    with pytest.raises(FinalityDenied) as x: ped.validate_and_issue(replace(act,revocation_epoch=11),ctx)
    assert x.value.code==EFCode.REVOCATION_STATE_MISMATCH

def test_candidate_protected_state_stale(stack):
    act,ctx,_,_,ped,_,_,_=stack
    with pytest.raises(FinalityDenied) as x: ped.validate_and_issue(replace(act,protected_state_ref="stale"),ctx)
    assert x.value.code==EFCode.PROTECTED_STATE_MISMATCH

@pytest.mark.parametrize("amount,expected",[(1,False),(249.99,False),(250,True),(500,True)])
def test_hot_cold_path_threshold(stack,amount,expected):
    act,ctx,_,_,ped,_,_,_=stack
    _,_,cold=ped.validate_and_issue(replace(act,arguments={"amount":amount}),ctx)
    assert cold is expected
