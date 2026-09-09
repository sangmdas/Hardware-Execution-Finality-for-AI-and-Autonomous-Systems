import gc, json, os, platform, statistics, sys, time
from execution_finality import *

N = int(os.getenv("EF_BENCH_N", "5000"))
WARMUP = int(os.getenv("EF_BENCH_WARMUP", "500"))
TARGET_P95_MS = float(os.getenv("EF_REFERENCE_P95_TARGET_MS", "5.0"))
PED_KEY=b"benchmark-ped-key"; HOLDER_KEY=b"benchmark-holder-key"
policy = PolicyProfile(frozenset({"customer-payment-api"}), frozenset({"payments-prod"}),
    frozenset({ConsequenceClass.MCP_CALL}), frozenset({"customer-refund"}), max_amount=500)
authn = HMACAuthenticator(PED_KEY)
ped = ProtectedEnforcementDomain(authn, policy)
holder = ProtectedHolder("holder-1", HOLDER_KEY)

def percentile(xs, p):
    xs=sorted(xs); return xs[min(len(xs)-1, int((len(xs)-1)*p))]

def stats(xs):
    return {"p50_ms":round(percentile(xs,.50),4),"p95_ms":round(percentile(xs,.95),4),
            "p99_ms":round(percentile(xs,.99),4),"mean_ms":round(statistics.mean(xs),4),
            "min_ms":round(min(xs),4),"max_ms":round(max(xs),4)}

def one(measure=True):
    act=make_candidate(); ctx=make_context(act)
    sink=FinalitySink("mcp-dispatcher", authn, HolderRegistry({"holder-1":HOLDER_KEY}), InMemoryReplayStore())
    t0=time.perf_counter_ns()
    ev, au, _=ped.validate_and_issue(act, ctx)
    t1=time.perf_counter_ns()
    proof=holder.prove(au, sink.challenge())
    t2=time.perf_counter_ns()
    sink.verify_and_effectuate(act, ev, au, proof, ctx)
    t3=time.perf_counter_ns()
    return ((t1-t0)/1e6,(t2-t1)/1e6,(t3-t2)/1e6,(t3-t0)/1e6)

for _ in range(WARMUP): one(False)
ped_s=[]; pop_s=[]; sink_s=[]; total_s=[]
gc.collect(); gc.disable()
try:
    for _ in range(N):
        a,b,c,d=one(); ped_s.append(a); pop_s.append(b); sink_s.append(c); total_s.append(d)
finally:
    gc.enable()

cpu="unknown"
try:
    for line in open('/proc/cpuinfo'):
        if line.lower().startswith('model name'):
            cpu=line.split(':',1)[1].strip(); break
except Exception: pass

result={
    "warning":"Software-only reference benchmark. Not a TEE/HSM/GPU/SmartNIC hardware result.",
    "scope":"PED issue + holder proof-of-possession + independent sink verification + atomic in-memory consume; no network or external effect I/O",
    "iterations":N,"warmup_iterations":WARMUP,
    "python":sys.version.split()[0],"platform":platform.platform(),"machine":platform.machine(),"cpu":cpu,
    "authenticator":"HMAC-SHA-256 reference variant","replay_store":"in-memory atomic lock",
    "ped_issue":stats(ped_s),"holder_proof":stats(pop_s),"sink_verify_and_consume":stats(sink_s),"total_hot_path":stats(total_s),
    "reference_ci_target_p95_ms":TARGET_P95_MS,
    "reference_ci_target_pass":percentile(total_s,.95) <= TARGET_P95_MS,
    "draft_context":"The Internet-Draft describes 1-20 ms as representative industrial hot-path budgets in related implementations, not as a protocol requirement."
}
print(json.dumps(result,indent=2))
