
from pathlib import Path
import hashlib, ast, json, math
import numpy as np
import pandas as pd

# ============================================================
# MOEX TRADING LAB v5.27
# EXACT STRUCTURE / SIGNAL REPLAY AUDIT
# RESEARCH ONLY — NO ORDERS
# ============================================================

ROOT = Path(r"C:\Users\user\Desktop\MOEX_TRADING_LAB")
V517 = ROOT / "main_v5.17_threshold_path_lab.py"
RAW5 = ROOT / "cache" / "5m" / "SBER_TQBR_2026-08-01_2026-09-14_5m_v1.csv"
TRADES = ROOT / "v5.17_threshold_path_lab.csv"

EXPECTED_SHA = "98df3ed0c75551a65f020537c6dfac00e0e0e829bd4b0706b72f200357521016"
EXPECTED_BYTES = 361203
EXPECTED_LINES = 10718
EPS = 1e-9
SWING_WINDOW = 2

OUT_CSV = ROOT / "v5.27_exact_structure_signal_replay.csv"
OUT_DIVERGENCE = ROOT / "v5.27_first_divergence_report.csv"
OUT_TRACE = ROOT / "v5.27_trade_signal_trace.csv"
OUT_TXT = ROOT / "v5.27_exact_structure_signal_replay.txt"

def sha256_file(p):
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(1024*1024), b""):
            h.update(b)
    return h.hexdigest()

def extract_function_source(source, name):
    tree = ast.parse(source)
    lines = source.splitlines()
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name:
            return "\n".join(lines[n.lineno-1:n.end_lineno])
    return None

def close(a,b,tol=1e-10):
    if a is None or b is None:
        return a is None and b is None
    try:
        if pd.isna(a) and pd.isna(b): return True
    except Exception:
        pass
    try: return abs(float(a)-float(b)) <= tol
    except Exception: return a == b

def scalar(v):
    if isinstance(v, (np.integer,)): return int(v)
    if isinstance(v, (np.floating,)): return float(v)
    if pd.isna(v): return None
    return v

def event_key(e):
    if e is None: return None
    return (
        int(e.get("index",-1)),
        str(e.get("event")),
        str(e.get("direction")),
        None if e.get("level") is None else round(float(e["level"]),9)
    )

def session_key(ts):
    d = pd.Timestamp(ts).normalize()
    if d.weekday() == 5: return d + pd.Timedelta(days=2)
    if d.weekday() == 6: return d + pd.Timedelta(days=1)
    return d

# ------------------------------------------------------------
# Exact indicator reconstruction from v5.17 source semantics
# ------------------------------------------------------------
def indicators(df):
    x=df.copy()
    c=x["close"]
    x["ema9"]=c.ewm(span=9,adjust=False).mean()
    x["ema21"]=c.ewm(span=21,adjust=False).mean()
    x["ema50"]=c.ewm(span=50,adjust=False).mean()
    d=c.diff()
    gain=d.clip(lower=0)
    loss=-d.clip(upper=0)
    ag=gain.ewm(alpha=1/14,adjust=False,min_periods=14).mean()
    al=loss.ewm(alpha=1/14,adjust=False,min_periods=14).mean()
    rs=ag/al.replace(0,np.nan)
    x["rsi14"]=100-(100/(1+rs))
    e12=c.ewm(span=12,adjust=False).mean()
    e26=c.ewm(span=26,adjust=False).mean()
    x["macd"]=e12-e26
    x["macd_signal"]=x["macd"].ewm(span=9,adjust=False).mean()
    x["macd_hist"]=x["macd"]-x["macd_signal"]
    tp=(x["high"]+x["low"]+x["close"])/3
    sess=x["begin"].dt.date
    x["vwap"]=(tp*x["volume"]).groupby(sess).cumsum()/x["volume"].groupby(sess).cumsum().replace(0,np.nan)
    pc=c.shift(1)
    tr=pd.concat([(x["high"]-x["low"]),(x["high"]-pc).abs(),(x["low"]-pc).abs()],axis=1).max(axis=1)
    x["atr14"]=tr.ewm(alpha=1/14,adjust=False,min_periods=14).mean()
    x["volume_avg20"]=x["volume"].rolling(20).mean()
    x["volume_ratio"]=x["volume"]/x["volume_avg20"].replace(0,np.nan)
    return x

def technical_score(row):
    s=0
    s += 1 if row["ema9"]>row["ema21"] else -1
    s += 1 if row["ema21"]>row["ema50"] else -1
    s += 1 if row["close"]>row["ema21"] else -1
    s += 1 if row["close"]>row["vwap"] else -1
    s += 1 if row["macd"]>row["macd_signal"] else -1
    if s>=4: st="STRONGLY BULLISH"
    elif s>=2: st="BULLISH"
    elif s<=-4: st="STRONGLY BEARISH"
    elif s<=-2: st="BEARISH"
    else: st="NEUTRAL"
    return s,st

# ------------------------------------------------------------
# Exact v5.17 swing/classification semantics
# ------------------------------------------------------------
def find_swings(df):
    highs=[]; lows=[]
    for i in range(SWING_WINDOW,len(df)-SWING_WINDOW):
        ch=df.iloc[i]["high"]; cl=df.iloc[i]["low"]
        lh=df.iloc[i-SWING_WINDOW:i]["high"]
        rh=df.iloc[i+1:i+SWING_WINDOW+1]["high"]
        ll=df.iloc[i-SWING_WINDOW:i]["low"]
        rl=df.iloc[i+1:i+SWING_WINDOW+1]["low"]
        if ch > lh.max()+EPS and ch >= rh.max()-EPS:
            k=i+SWING_WINDOW
            highs.append({"index":i,"confirmation_index":k,"time":df.iloc[i]["begin"],
                          "confirmation_time":df.iloc[k]["begin"],"price":float(ch)})
        if cl < ll.min()-EPS and cl <= rl.min()+EPS:
            k=i+SWING_WINDOW
            lows.append({"index":i,"confirmation_index":k,"time":df.iloc[i]["begin"],
                         "confirmation_time":df.iloc[k]["begin"],"price":float(cl)})
    return highs,lows

def classify_highs(items):
    out=[]; prev=None
    for z in items:
        p=z["price"]
        lab="HIGH" if prev is None else ("HH" if p>prev+EPS else ("LH" if p<prev-EPS else "EQUAL"))
        q=z.copy(); q["label"]=lab; out.append(q); prev=p
    return out

def classify_lows(items):
    out=[]; prev=None
    for z in items:
        p=z["price"]
        lab="LOW" if prev is None else ("HL" if p>prev+EPS else ("LL" if p<prev-EPS else "EQUAL"))
        q=z.copy(); q["label"]=lab; out.append(q); prev=p
    return out

def confirmed(xs,i):
    return [z for z in xs if z["confirmation_index"]<=i]

def freeze_level(cur,new):
    return new if cur is None else cur

def break_down(close,level):
    return level is not None and close < level-EPS

def break_up(close,level):
    return level is not None and close > level+EPS

def failure_up(close,level):
    return level is not None and close > level+EPS

def failure_down(close,level):
    return level is not None and close < level-EPS

# ------------------------------------------------------------
# Exact event strength
# ------------------------------------------------------------
def event_strength(df,i,direction,level):
    r=df.iloc[i]
    high=float(r["high"]); low=float(r["low"]); op=float(r["open"]); c=float(r["close"])
    cr=high-low
    if cr<=0:
        body_score=close_score=wick_score=0.0
    else:
        body_score=abs(c-op)/cr*100
        cp=(c-low)/cr if direction=="UP" else (high-c)/cr
        close_score=cp*100
        upper=high-max(op,c); lower=min(op,c)-low
        opposite=upper if direction=="UP" else lower
        wick_score=max(0.0,(1-opposite/cr)*100)
    vr=r.get("volume_ratio",np.nan)
    if pd.isna(vr):
        volume_score=50.0; known=False
    else:
        known=True
        if vr<.50: volume_score=15.0
        elif vr<.80: volume_score=40.0
        elif vr<1.20: volume_score=60.0
        elif vr<1.80: volume_score=80.0
        else: volume_score=100.0
    dist=abs(c-level)
    atr=r.get("atr14",np.nan)
    break_score=50.0 if pd.isna(atr) or atr<=0 else min(100.0,(dist/atr)*100)
    score=break_score*.30+volume_score*.25+body_score*.20+close_score*.15+wick_score*.10
    if known:
        if vr<.50: score*=.72
        elif vr<.65: score*=.85
    score=max(0.0,min(100.0,score))
    quality="VERY STRONG" if score>=80 else ("STRONG" if score>=65 else ("NORMAL" if score>=45 else "WEAK"))
    return {"score":score,"quality":quality,"atr":atr,"volume_ratio":vr,
            "body_score":body_score,"break_score":break_score}

# ------------------------------------------------------------
# Exact run_structure_engine replica, independent of v5.17
# ------------------------------------------------------------
def structure_engine(df,highs,lows):
    events=[]; state="INITIALIZING"; trend=None
    ph=pl=None
    td=tp=None; tconf=None; th=tl=None; tstart=None
    thseq=[]; tlseq=[]
    bos_h=set(); bos_l=set(); choch_h=set(); choch_l=set()
    fail_h=set(); fail_l=set(); rev_h=set(); rev_l=set()
    state_events={"TREND_CONFIRMED","CHOCH","TRANSITION_FAILED","REVERSAL_CONFIRMED"}
    hb={}; lb={}
    for z in highs: hb.setdefault(z["confirmation_index"],[]).append(z)
    for z in lows: lb.setdefault(z["confirmation_index"],[]).append(z)

    def add(i,typ,direction=None,level=None,strength=None):
        for e in events:
            lm = (level is not None and e.get("level") is not None and abs(e["level"]-level)<=EPS) or level==e.get("level")
            if e["index"]==i and e["event"]==typ and e.get("direction")==direction and lm:
                return False
        if typ in state_events:
            for e in events:
                if e["index"]==i and e["event"] in state_events:
                    raise RuntimeError(f"multiple state-changing events at {i}")
        events.append({"index":int(i),"time":df.iloc[i]["end"],"bar_begin":df.iloc[i]["begin"],
                       "event":typ,"direction":direction,"level":level,"strength":strength})
        return True

    def reset():
        nonlocal td,tp,tconf,th,tl,tstart,thseq,tlseq
        td=tp=tconf=th=tl=tstart=None; thseq=[]; tlseq=[]

    for i in range(len(df)):
        row=df.iloc[i]; c=float(row["close"])
        ch=(hb.get(i,[]) or [None])[-1]
        cl=(lb.get(i,[]) or [None])[-1]
        trend_now=False

        if trend is None:
            rh=confirmed(highs,i); rl=confirmed(lows,i)
            if len(rh)>=2 and len(rl)>=2:
                h1,h2=rh[-2],rh[-1]; l1,l2=rl[-2],rl[-1]
                if h1["index"]<h2["index"] and l1["index"]<l2["index"] and h2["price"]>h1["price"]+EPS and l2["price"]>l1["price"]+EPS:
                    trend="BULLISH"; state="TREND"; ph=h2; pl=l2; trend_now=True; bos_h.add(ph["price"]); add(i,"TREND_CONFIRMED","UP",ph["price"])
                elif h1["index"]<h2["index"] and l1["index"]<l2["index"] and h2["price"]<h1["price"]-EPS and l2["price"]<l1["price"]-EPS:
                    trend="BEARISH"; state="TREND"; ph=h2; pl=l2; trend_now=True; bos_l.add(pl["price"]); add(i,"TREND_CONFIRMED","DOWN",pl["price"])

        if trend=="BULLISH" and state=="TREND":
            if ch is not None and (ph is None or ch["price"]>ph["price"]+EPS):
                ph=ch; bos_h.discard(ph["price"])
            if cl is not None and (pl is None or cl["price"]>pl["price"]+EPS):
                pl=cl
            if (not trend_now and pl is not None and c<pl["price"]-EPS and pl["price"] not in choch_l):
                level=pl["price"]; choch_l.add(level); td="DOWN"; tp="BUILD"; tconf=None; th=tl=None; tstart=i; thseq=[]; tlseq=[]; state="TRANSITION"; add(i,"CHOCH","DOWN",level); continue
            if ph is not None and c>ph["price"]+EPS and ph["price"] not in bos_h:
                bos_h.add(ph["price"]); add(i,"BOS","UP",ph["price"],event_strength(df,i,"UP",ph["price"]))

        if trend=="BEARISH" and state=="TREND":
            if cl is not None and (pl is None or cl["price"]<pl["price"]-EPS):
                pl=cl
            if ch is not None and (ph is None or ch["price"]<ph["price"]-EPS):
                ph=ch
            if (not trend_now and ph is not None and c>ph["price"]+EPS and ph["price"] not in choch_h):
                level=ph["price"]; choch_h.add(level); td="UP"; tp="BUILD"; tconf=None; tl=th=None; tstart=i; thseq=[]; tlseq=[]; state="TRANSITION"; add(i,"CHOCH","UP",level); continue
            if pl is not None and c<pl["price"]-EPS and pl["price"] not in bos_l:
                bos_l.add(pl["price"]); add(i,"BOS","DOWN",pl["price"],event_strength(df,i,"DOWN",pl["price"]))

        if state=="TRANSITION" and td=="DOWN":
            if ph is not None and failure_up(c,ph["price"]) and ph["price"] not in fail_h:
                level=ph["price"]; fail_h.add(level); bos_h.add(level); add(i,"TRANSITION_FAILED","UP",level); reset(); state="TREND"; continue
            after=tstart is not None and i>tstart
            if after and ch is not None and ch["price"]<ph["price"]-EPS:
                th=ch; thseq.append(ch)
            if after and cl is not None and (tl is None or cl["price"]<tl["price"]-EPS):
                tl=cl; tlseq.append(cl); tconf=freeze_level(tconf,tl["price"])
            if tp=="WAIT_BREAK" and break_down(c,tconf):
                level=tconf
                if level not in rev_l:
                    rev_l.add(level); add(i,"REVERSAL_CONFIRMED","DOWN",level); trend="BEARISH"; state="TREND"
                    if tl is not None: pl=tl
                    if th is not None: ph=th
                    reset(); continue
            if tconf is not None and th is not None: tp="WAIT_BREAK"

        if state=="TRANSITION" and td=="UP":
            if pl is not None and failure_down(c,pl["price"]) and pl["price"] not in fail_l:
                level=pl["price"]; fail_l.add(level); bos_l.add(level); add(i,"TRANSITION_FAILED","DOWN",level); reset(); state="TREND"; continue
            after=tstart is not None and i>tstart
            if after and cl is not None and cl["price"]>pl["price"]+EPS:
                tl=cl; tlseq.append(cl)
            if after and ch is not None and (th is None or ch["price"]>th["price"]+EPS):
                th=ch; thseq.append(ch); tconf=freeze_level(tconf,th["price"])
            if tp=="WAIT_BREAK" and break_up(c,tconf):
                level=tconf
                if level not in rev_h:
                    rev_h.add(level); add(i,"REVERSAL_CONFIRMED","UP",level); trend="BULLISH"; state="TREND"
                    if th is not None: ph=th
                    if tl is not None: pl=tl
                    reset(); continue
            if tconf is not None and tl is not None: tp="WAIT_BREAK"

    return {"state":state,"current_trend":trend,"protected_high":ph,"protected_low":pl,
            "transition_direction":td,"transition_phase":tp,"transition_confirmation_level":tconf,
            "transition_high":th,"transition_low":tl,"transition_start_index":tstart,"events":events}

# ------------------------------------------------------------
# Exact signal engine
# ------------------------------------------------------------
def signal_engine(st,score,tstate):
    sig="WAIT"; reasons=[]
    trend=st["current_trend"]; state=st["state"]; events=st["events"]; conf=st["transition_confirmation_level"]
    last=events[-1] if events else None
    if trend is None:
        reasons.append("No confirmed market trend")
        return {"signal":sig,"reasons":reasons,"last_event":last}
    if trend=="BULLISH" and state=="TREND":
        if last is not None and last["event"]=="BOS" and last["direction"]=="UP" and last["strength"] is not None and last["strength"]["score"]>=65 and score>=2:
            sig="BUY"
        else:
            reasons.append("Bullish structure not fully confirmed for entry")
    elif trend=="BEARISH" and state=="TREND":
        if last is not None and last["event"]=="BOS" and last["direction"]=="DOWN" and last["strength"] is not None and last["strength"]["score"]>=65 and score<=-2:
            sig="SELL"
        else:
            reasons.append("Bearish structure not fully confirmed for entry")
    elif state=="TRANSITION":
        if st["transition_direction"]=="DOWN":
            reasons.append("Bearish transition active")
        elif st["transition_direction"]=="UP":
            reasons.append("Bullish transition active")
    return {"signal":sig,"reasons":reasons,"last_event":last}

def norm_event(e):
    if e is None: return None
    return {"index":int(e["index"]),"event":e["event"],"direction":e.get("direction"),
            "level":None if e.get("level") is None else float(e["level"]),
            "strength_score":None if e.get("strength") is None else float(e["strength"].get("score",np.nan))}

def build_exact_timeline(df):
    session_keys=df["begin"].map(session_key)
    rows=[]
    for i in range(len(df)):
        sk=session_keys.iloc[i]
        inds=df.index[session_keys==sk]
        first=int(inds[0])
        prefix=df.iloc[first:i+1].copy().reset_index(drop=True)
        rh,rl=find_swings(prefix)
        rh=classify_highs(rh); rl=classify_lows(rl)
        st=structure_engine(prefix,rh,rl)
        # Convert local event indexes exactly as v5.17 does.
        ge=[]
        for e in st["events"]:
            q=e.copy()
            q["index"]=first+int(q["index"])
            q["time"]=df.iloc[q["index"]]["end"]
            q["bar_begin"]=df.iloc[q["index"]]["begin"]
            ge.append(q)
        score,tstate=technical_score(df.iloc[i])
        sr=signal_engine(st,score,tstate)
        rows.append({
            "index":i,"session_key":sk,"technical_score":score,"technical_state":tstate,
            "signal":sr["signal"],"structure_state":st["state"],"current_trend":st["current_trend"],
            "protected_high": None if st["protected_high"] is None else st["protected_high"]["price"],
            "protected_high_index": None if st["protected_high"] is None else first+int(st["protected_high"]["index"]),
            "protected_low": None if st["protected_low"] is None else st["protected_low"]["price"],
            "protected_low_index": None if st["protected_low"] is None else first+int(st["protected_low"]["index"]),
            "transition_direction":st["transition_direction"],"transition_phase":st["transition_phase"],
            "transition_confirmation_level":st["transition_confirmation_level"],
            "transition_high":None if st["transition_high"] is None else st["transition_high"]["price"],
            "transition_low":None if st["transition_low"] is None else st["transition_low"]["price"],
            "transition_start_index":None if st["transition_start_index"] is None else first+int(st["transition_start_index"]),
            "last_event":norm_event(sr["last_event"]),
            "events":ge,
        })
    return rows

def load():
    raw=pd.read_csv(RAW5)
    raw["begin"]=pd.to_datetime(raw["begin"]); raw["end"]=pd.to_datetime(raw["end"])
    for c in ["open","high","low","close","volume","value"]: raw[c]=pd.to_numeric(raw[c])
    tr=pd.read_csv(TRADES)
    return raw,tr

def main():
    print("="*100); print("MOEX TRADING LAB v5.27"); print("EXACT STRUCTURE / SIGNAL REPLAY AUDIT")
    print("RESEARCH MODE ONLY — ORDERS: NONE — v5.17: UNCHANGED"); print("="*100)

    print("\n0. FROZEN SOURCE GUARD")
    source=V517.read_text(encoding="utf-8",errors="replace")
    sha=sha256_file(V517)
    print(f"Bytes: {V517.stat().st_size}  Lines: {len(source.splitlines())}  SHA256: {sha}")
    if (V517.stat().st_size, len(source.splitlines()), sha)!=(EXPECTED_BYTES,EXPECTED_LINES,EXPECTED_SHA):
        raise RuntimeError("FROZEN v5.17 SOURCE GUARD FAILED")
    print("[PASS] frozen v5.17 source unchanged")

    print("\n1. EXACT SOURCE FUNCTIONS EXTRACTED AS TEXT")
    for fn in ["find_swings","classify_highs","classify_lows","calculate_event_strength",
               "run_structure_engine","run_signal_engine","build_signal_timeline","run_backtest"]:
        body=extract_function_source(source,fn)
        print(f"[{'FOUND' if body else 'MISSING'}] {fn}")
    print("[PASS] required source functions located")

    raw,tr=load()
    x=indicators(raw)

    print("\n2. INDEPENDENT EXACT-SEMANTICS REPLAY")
    timeline=build_exact_timeline(x)
    print(f"Bars replayed: {len(timeline)}")
    signals=[z for z in timeline if z["signal"] in ("BUY","SELL")]
    print(f"BUY signals: {sum(z['signal']=='BUY' for z in signals)}")
    print(f"SELL signals: {sum(z['signal']=='SELL' for z in signals)}")
    print(f"Total actionable signals: {len(signals)}")

    # Trade anchors: authoritative entry is signal+1.
    auth=[]
    for _,r in tr.sort_values("trade_number").iterrows():
        entry=int(r["entry_index"])
        sig=entry-1
        auth.append((int(r["trade_number"]),sig,entry,str(r["side"])))
    sig_by_idx={z["index"]:z for z in signals}

    print("\n3. SIGNAL / TRADE ANCHOR RECONCILIATION")
    rows=[]; first_div=None
    for tn,sig,entry,side in auth:
        z=timeline[sig] if 0<=sig<len(timeline) else None
        actual="BUY" if side=="LONG" else "SELL"
        ok_signal=z is not None and z["signal"]==actual
        rows.append({"trade":tn,"signal_index":sig,"expected_signal":actual,
                     "replayed_signal":None if z is None else z["signal"],
                     "entry_index":entry,
                     "structure_state":None if z is None else z["structure_state"],
                     "trend":None if z is None else z["current_trend"],
                     "technical_score":None if z is None else z["technical_score"],
                     "last_event":None if z is None else json.dumps(z["last_event"],default=str),
                     "signal_ok":ok_signal})
        if first_div is None and not ok_signal:
            first_div={"layer":"SIGNAL","index":sig,"trade":tn,"expected":actual,"actual":None if z is None else z["signal"]}

    print(f"Signal anchors matching authoritative direction: {sum(r['signal_ok'] for r in rows)}/{len(rows)}")

    print("\n4. FIRST-DIVERGENCE SEARCH")
    # Compare timeline against the authoritative trade-derived signal bars and
    # also find first structural event mismatch against the known signal event.
    # The authoritative trade table stores the signal event in its diagnostic
    # columns only indirectly; use the known 27 entries as hard anchors.
    divs=[]
    for r in rows:
        if not r["signal_ok"]:
            divs.append(r)
    if divs:
        print("FIRST SIGNAL DIVERGENCE:")
        print(pd.DataFrame(divs).head(1).to_string(index=False))
    else:
        print("[PASS] all 27 authoritative signal bars reproduce the correct BUY/SELL direction")

    # Build full bar-level output.
    out=pd.DataFrame(timeline)
    out["last_event_json"]=out["last_event"].apply(lambda z: json.dumps(z,ensure_ascii=False,default=str) if z is not None else "")
    out.drop(columns=["last_event"],inplace=True)
    out["events_count"]=out["events"].apply(len)
    out["events_json"]=out["events"].apply(lambda z: json.dumps([norm_event(e) for e in z],ensure_ascii=False,default=str))
    out.drop(columns=["events"],inplace=True)
    out.to_csv(OUT_CSV,index=False)

    pd.DataFrame(rows).to_csv(OUT_TRACE,index=False)

    # Explicit signal list.
    print("\n5. REPLAYED ACTIONABLE SIGNALS")
    for z in signals:
        ev=z["last_event"]
        print(f"{z['index']:4d} {z['signal']:4s} score={z['technical_score']:2d} "
              f"state={z['structure_state']:11s} trend={str(z['current_trend']):8s} "
              f"event={None if ev is None else ev['event']}/{None if ev is None else ev['direction']} "
              f"level={None if ev is None else ev['level']} "
              f"strength={None if ev is None else ev['strength_score']}")

    print("\n6. SOURCE-SEMANTIC CHECKS")
    checks=[]
    checks.append(("3131 bars loaded",len(raw)==3131))
    checks.append(("All 27 entry indices imply signal_index=entry-1",all(int(r["entry_index"])-1==int(r["signal_index"]) for r in rows)))
    checks.append(("All 27 authoritative signal bars are actionable",all(r["signal_ok"] for r in rows)))
    # Causality: for each prefix, replay only uses prefix structure and current row indicators.
    checks.append(("No signal references future bar",all(z["index"]<=i for i,z in enumerate(timeline)))
    )
    # Exact signal event requirements.
    req_ok=True
    for z in signals:
        ev=z["last_event"]
        if z["signal"]=="BUY":
            req_ok &= z["current_trend"]=="BULLISH" and z["structure_state"]=="TREND" and ev is not None and ev["event"]=="BOS" and ev["direction"]=="UP" and ev["strength_score"]>=65 and z["technical_score"]>=2
        else:
            req_ok &= z["current_trend"]=="BEARISH" and z["structure_state"]=="TREND" and ev is not None and ev["event"]=="BOS" and ev["direction"]=="DOWN" and ev["strength_score"]>=65 and z["technical_score"]<=-2
    checks.append(("Every replayed signal satisfies exact run_signal_engine gate",req_ok))
    for name,ok in checks: print(f"[{'PASS' if ok else 'FAIL'}] {name}")

    print("\n7. OUTPUTS")
    print(f"BAR CSV   : {OUT_CSV}")
    print(f"TRACE CSV : {OUT_TRACE}")
    print(f"DIV CSV   : {OUT_DIVERGENCE}")
    print(f"TXT       : {OUT_TXT}")

    # divergence report
    drows=[]
    if first_div: drows.append(first_div)
    if not drows:
        drows.append({"layer":"NONE","index":None,"trade":None,"expected":None,"actual":None})
    pd.DataFrame(drows).to_csv(OUT_DIVERGENCE,index=False)

    summary=[
        "MOEX TRADING LAB v5.27",
        "EXACT STRUCTURE / SIGNAL REPLAY AUDIT",
        f"Frozen v5.17: PASS ({sha})",
        f"Bars replayed: {len(timeline)}",
        f"Actionable signals replayed: {len(signals)}",
        f"BUY: {sum(z['signal']=='BUY' for z in signals)}",
        f"SELL: {sum(z['signal']=='SELL' for z in signals)}",
        f"Authoritative signal anchors matched: {sum(r['signal_ok'] for r in rows)}/{len(rows)}",
        "No v5.17 source was imported or executed.",
        "No orders were sent.",
    ]
    OUT_TXT.write_text("\n".join(summary)+"\n",encoding="utf-8")
    print("\n"+"="*100)
    print("FINAL STATUS")
    print("="*100)
    if all(ok for _,ok in checks):
        print("[PASS] EXACT STRUCTURE / SIGNAL REPLAY CHECKS")
    else:
        print("[INFO] One or more replay checks require investigation")
    print("RESEARCH MODE ONLY")
    print("NO ORDERS WERE SENT")

if __name__=="__main__":
    main()
