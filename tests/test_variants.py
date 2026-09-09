from dataclasses import replace
from concurrent.futures import ThreadPoolExecutor
import tempfile
import pytest
from execution_finality import *


def test_ed25519_variant_end_to_end():
    signer=Ed25519Signer(); verifier=signer.public_verifier(); holder_key=b"holder"
    act=make_candidate(); ctx=make_context(act)
    policy=PolicyProfile(frozenset({act.tool_id}),frozenset({act.destination_id}),frozenset({act.consequence_class}),frozenset({act.purpose}))
    ped=ProtectedEnforcementDomain(signer,policy)
    holder=ProtectedHolder("holder-1",holder_key)
    sink=FinalitySink(act.finality_sink_id,verifier,HolderRegistry({"holder-1":holder_key}),InMemoryReplayStore())
    ev,au,_=ped.validate_and_issue(act,ctx)
    r=sink.verify_and_effectuate(act,ev,au,holder.prove(au,sink.challenge()),ctx)
    assert r.destination_id==act.destination_id

def test_sqlite_replay_store_persists():
    with tempfile.TemporaryDirectory() as d:
        path=f"{d}/replay.db"
        a=SQLiteReplayStore(path); assert a.consume_once("x") is True
        b=SQLiteReplayStore(path); assert b.consume_once("x") is False and b.is_used("x")

def test_in_memory_atomic_consume():
    store=InMemoryReplayStore()
    with ThreadPoolExecutor(max_workers=16) as ex:
        results=list(ex.map(lambda _:store.consume_once("same"),range(100)))
    assert sum(results)==1

def test_sqlite_atomic_consume():
    with tempfile.TemporaryDirectory() as d:
        store=SQLiteReplayStore(f"{d}/r.db")
        with ThreadPoolExecutor(max_workers=8) as ex:
            results=list(ex.map(lambda _:store.consume_once("same"),range(32)))
        assert sum(results)==1

@pytest.mark.parametrize("consequence,tool,dest,purpose,sinkid",[
    (ConsequenceClass.MCP_CALL,"tool","api","p","mcp-sink"),
    (ConsequenceClass.DATA_EXPORT,"egress","partner","p","egress-sink"),
    (ConsequenceClass.PAYMENT,"pay","bank","p","payment-sink"),
    (ConsequenceClass.ACCELERATOR_EGRESS,"gpu","host-buffer","p","dpu-sink"),
    (ConsequenceClass.MEMORY_WRITE,"memory","vector-db","p","db-commit"),
    (ConsequenceClass.COMPUTER_USE,"computer","desktop","p","ui-bridge"),
    (ConsequenceClass.SHELL_EXEC,"shell","host","p","shell-bridge"),
    (ConsequenceClass.ACTUATOR,"plc","line-7","p","plc-gate"),
])
def test_consequence_variations(consequence,tool,dest,purpose,sinkid):
    act=make_candidate(consequence_class=consequence,tool_id=tool,destination_id=dest,purpose=purpose,finality_sink_id=sinkid)
    ctx=make_context(act); key=b"k"; hk=b"h"
    policy=PolicyProfile(frozenset({tool}),frozenset({dest}),frozenset({consequence}),frozenset({purpose}))
    auth=HMACAuthenticator(key); ped=ProtectedEnforcementDomain(auth,policy); holder=ProtectedHolder("holder-1",hk)
    sink=FinalitySink(sinkid,auth,HolderRegistry({"holder-1":hk}),InMemoryReplayStore())
    ev,au,_=ped.validate_and_issue(act,ctx)
    assert sink.verify_and_effectuate(act,ev,au,holder.prove(au,sink.challenge()),ctx).consequence_class==consequence
