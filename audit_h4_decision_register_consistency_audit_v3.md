# audit_h4_decision_register_consistency_audit_v3.md

H4 CONSISTENCY AUDIT v2 — TARGETED LOGIC CORRECTION
Read-only documentary review only.

No data processing. No bootstrap. No CI. No T-1 execution.
No H4 execution. No OOS opening or analysis. No spec, code, data or
existing report modification. No overwriting.

STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY
NO THRESHOLD IS OPTIMIZED
NO FILTER IS INSTALLED
NO LIVE ORDERS
OOS: SEALED. H4 EXECUTION: NOT AUTHORIZED.

---

## 1. SCOPE AND LIMITS

### 1.1. Inputs available as full text in this dialog

- `audit_h4_decision_register_consistency_audit_v2.md` (input for
  this review) — full text in the user's previous message.
- `audit_h4_decision_register_consistency_audit_v1.md` — full text
  in an earlier user message.
- `audit_h4_decision_register_source_verification_v1.md` — full
  text in an earlier user message.
- `h4_sources_v4.txt` — full text with line numbers in an earlier
  user message. It contains verbatim: the six source files
  (`audit_h4_m3_eligibility_comparison_v1.md`,
  `audit_h4_final_predecision_audit_v1.md`,
  `audit_h4_range_atr_definition_proposal_v1.md`,
  `audit_h4_m5_report.txt`,
  `audit_h4_forensic_followup_v2_fast_qa_a2.csv`,
  `audit_h4_consolidated_open_decisions_register_v1.md`).
- `audit_h4_evidence_reconciliation_matrix_v1.md` — full text.
- `evidence_v2.txt`, `evidence_v3.txt` — full texts with line
  numbers.

### 1.2. What is NOT independently verified here

- Physical existence of any file on the user's disk.
- Actual byte content of any file not supplied verbatim in this
  dialog.
- Independently recomputed SHA-256 of any file.
- Line numbers beyond those shown in supplied texts.

### 1.3. Labels used

- CONFIRMED FROM SOURCE — directly evidenced by text available.
- PARTIALLY CONFIRMED — partially evidenced.
- ASSERTED BUT NOT INDEPENDENTLY VERIFIED — stated, not checkable.
- NOT ESTABLISHED / OPEN — no evidence available.
- A / B / C / D / E (see §5).

### 1.4. Boundaries

No calculation. No data. No source execution. No spec changes.
No decisions taken on behalf of the user.

---

## 2. CORRECTIONS TABLE FOR v2

| ID   | v2 statement (exact location) | Problem | Correction in v3 |
|------|-------------------------------|---------|------------------|
| W-1  | v2 §5.2: "M2-STAT-UNDEF depends on PC3. PC3-UNDEF depends on M2-STAT-UNDEF." + "No cycles" in §7. | Mutual pair shown without marking cycle. | Per primary register, both directions are present; this is a cycle. See §3. |
| W-2  | v2 §5.2: "M2-RNG depends on PC4. PC4 depends on M2-RNG." + "No cycles" in §7. | Same issue. | Cycle confirmed. See §3. |
| W-3  | v2 §7: "M1 ↔ M2-QUANTILE". | Only one direction is supported (§5.2: M2-QUANTILE depends on M1). | Downgrade to one-directional `M1 → M2-QUANTILE`. See §3. |
| W-4  | v2 §3 & §7: `D1 → T-1 → M3 closure` chain. | §3 already says D6 ↔ T-1 is OPEN, but §7 shows a linear chain including T-1 as prerequisite for M3 closure. | Replace with an OPEN / NOT ESTABLISHED graph. See §4. |
| W-5  | v2 §3.4: criterion "in-scope → change; out-of-scope → clarification". | Not supported by primary sources. | Reclassify D6 criterion as **OPEN** with listed missing grounds. See §5. |
| W-6  | v2 §6 D11/D12 three-status split. | Correct idea; must be re-expressed with explicit source phrases per field. | Rebuild as A/B/C fields with verbatim anchors. See §6. |
| W-7  | v2 §4 "EVIDENCE MATRIX": items 1–12 marked "yes" in column B. | Column B="readable in dialog" is correct only because the six files were transmitted verbatim in h4_sources_v4. This is B in a narrow sense. | Preserve B=yes only for those six, and only as "readable in this dialog". See §7. |
| W-8  | v2 §4 "104 .py files" claim. | Limited-scope inventory. | Preserve as limited-scope statement only. See §7. |

---

## 3. CYCLES IN THE DEPENDENCY MAP — VERIFICATION

For each pair, the primary source is
`audit_h4_consolidated_open_decisions_register_v1.md` §1 (the
"Register table"), which is readable verbatim in
`h4_sources_v4.txt` with line numbers.

### 3.1. M2-STAT-UNDEF ↔ PC3-UNDEF

**Primary rows (verbatim excerpts):**

- Register row `M2-STAT-UNDEF`:
  "Dependencies: M2-CALENDAR, M2-DUPLICATES, PC3".

- Register row `PC3-UNDEF`:
  "Dependencies: M2-STAT-UNDEF".

**Finding:** both directions are stated. **CONFIRMED FROM SOURCE**
for the mutual pair.

**Cycle:** yes, mutual.

**Correction:** v2 §7 asserted "No cycles". This is wrong for this
pair. v3 marks it as a **CONFIRMED CYCLE**.

### 3.2. M2-RNG ↔ PC4

**Primary rows (verbatim excerpts):**

- Register row `M2-RNG`:
  "Dependencies: PC4".

- Register row `PC4`:
  "Dependencies: M2-CALENDAR, M2-DUPLICATES, M2-QUANTILE, M2-RNG".

**Finding:** both directions are stated. **CONFIRMED FROM SOURCE**
for the mutual pair.

**Cycle:** yes, mutual.

**Correction:** v2 §7 asserted "No cycles". This is wrong for this
pair. v3 marks it as a **CONFIRMED CYCLE**.

### 3.3. M1 ↔ M2-QUANTILE

**Primary rows (verbatim excerpts):**

- Register row `M2-QUANTILE`:
  "Dependencies: M1".

- Register row `M1`:
  "Dependencies: none".

**Finding:** only one direction is supported. Reverse direction is
**NOT ESTABLISHED**.

**Correction to v2:** remove `↔`. Use `M1 → M2-QUANTILE` only.

### 3.4. Cycles elsewhere

No other mutual pair is stated in the register. The three pairs
above are the only cycles identified. **CONFIRMED FROM SOURCE** for
absence of further cycles in the primary register.

**v3 does not claim "No cycles" as a global fact.** It states: two
confirmed cycles (M2-STAT-UNDEF ↔ PC3-UNDEF, M2-RNG ↔ PC4), and no
further cycles in the primary register.

---

## 4. D1 → T-1 → M3 CLOSURE — RE-VERIFICATION

The v2 §7 chain must be verified piece-by-piece against primary
sources.

### 4.1. What are the mandatory prerequisites for T-1?

From `audit_h4_m3_eligibility_comparison_v1.md` §7.4 (verbatim,
in h4_sources_v4.txt):

> "1. Resolve R-1 (definition of range_atr) to fix the input for
> eligibility.
> 2. Answer Q1 (session_key definition).
> 3. Choose between v3.4 §5.2 and v3.6.2 §6 as the normative
> eligibility rule, or freeze both and state which one applies
> in H4.
> 4. Authorize T-1 to measure actual differences."

**Primary evidence supports:**

- R-1 (D1) — prerequisite for T-1.
- Q1 (D2) — prerequisite for T-1.
- choice between v3.4 §5.2 / v3.6.2 §6 (D3 / D6) — prerequisite.
- explicit authorization of T-1 itself.

### 4.2. What is needed to interpret T-1 results?

Primary source does not state a separate list for this. **NOT
ESTABLISHED** by primary sources.

### 4.3. Is T-1 a mandatory prerequisite for M3 closure?

From `audit_h4_m3_eligibility_comparison_v1.md` §7.4:

> "Until steps 1-3 are done, T-1 has no defined input. Without T-1,
> M3 cannot be closed."

**Primary evidence supports:** T-1 is a mandatory prerequisite for
M3 closure as stated by the source.

### 4.4. Can M3 be closed documentarily without T-1?

Primary source explicitly says **no**:
"Without T-1, M3 cannot be closed."

So the documentary-only closure of M3 is **NOT ESTABLISHED** /
prohibited by the source.

### 4.5. Does D6 require T-1?

The primary source defines D6 (in
`audit_h4_final_predecision_audit_v1.md`) as a decision about
whether §6 is a clarification or a change. It does not state that
T-1 is required before D6, nor that D6 must precede T-1.

**Status: OPEN.**

### 4.6. Conclusion of §4

- `D1 → T-1` — CONFIRMED.
- `D2 → T-1` — CONFIRMED.
- `D3` (choice between endpoint/full-window) `→ T-1` — CONFIRMED.
- `D6 → T-1` — NOT ESTABLISHED.
- `T-1 → M3 closure` — CONFIRMED (source says "Without T-1, M3
  cannot be closed").
- `D6 ↔ T-1` — OPEN.
- v2 §7 chain `D1 → T-1 → M3 closure` is partially correct: D1 is
  a prerequisite; the D6 position is not established.
- **v2's linear notation was incomplete, not wrong on D1 side.**

---

## 5. D6 CRITERION — RE-VERIFICATION

### 5.1. Literal differences between v3.4 §5.2 and v3.6.2 §6

From `audit_h4_m3_eligibility_comparison_v1.md` §3 (comparison
table, verbatim in h4_sources_v4.txt):

- R7: v3.4 §5.2(a) endpoint-only vs v3.6.2 §6(k) full-window —
  **SUBSTANTIVE DIFFERENCE**.
- R8: v3.4 does not state `session_key[t] defined`; v3.6.2 §6(b)
  states it — **MISSING IN v3.4**.
- R9: v3.4 does not state bounds; v3.6.2 §6(j) states it —
  **MISSING IN v3.4**.

### 5.2. Statements about the originally intended eligible set

The primary documents do **not** state what the author originally
intended for the eligible set. They state only wording.

**NOT ESTABLISHED.**

### 5.3. Interpretation of the differences as clarification or change

Not fixed by any primary source. Neither
`audit_h4_m3_eligibility_comparison_v1.md` nor
`audit_h4_final_predecision_audit_v1.md` prescribes a decision rule.

The v2 §3.4 "in-scope → change / out-of-scope → clarification" rule
is **not supported**.

### 5.4. Factual impact on eligibility

Two prior statements exist:

- From `audit_h4_final_predecision_audit_v1.md` table row M3:
  "on audited data no bars affected".
- From `audit_h4_forensic_followup_v2_fast_qa_a2.csv`: per-bar
  mismatch = 0 for tested combinations.

Both are **observations**, not decisions.

### 5.5. Correct status of D6 criterion

**D6 criterion (clarification vs change): OPEN.**

Missing grounds, listed explicitly:

- The intended eligible set is not stated in any primary document.
- No decision rule is provided for choosing clarification vs
  change.
- The relationship between the three substantive differences
  (R7, R8, R9) and the intended set is not stated.
- It is not stated whether the observed 0-mismatch on audited data
  is relevant to the intended-set interpretation.

**No choice of clarification vs change is asked of the user here.**

---

## 6. D11 AND D12 — THREE FIELDS

Three independent fields are used:

- A. CURRENT AUTHORIZATION STATUS
- B. METHODOLOGICAL READINESS
- C. EXPLICIT PROHIBITION / RELEASE CONDITION

### 6.1. H4 execution (D11)

**Field A — Authorization status.**
Primary source: `audit_research_roadmap_v1_h4_spec_v3_6_2_PROPOSED.md`
§17 (verbatim): "NOT AUTHORIZED FOR EXECUTION."
Also: `audit_h4_final_predecision_audit_v1.md` §9: "H4 EXECUTION:
NOT AUTHORIZED."

**Field A value: NOT AUTHORIZED. CONFIRMED FROM SOURCE.**

**Field B — Methodological readiness.**
Primary source: same §17: "NOT READY: U1, U1b, U3-U5, M1-M3,
QA-A1, PC1-PC5 open."
**Field B value: NOT READY. CONFIRMED FROM SOURCE.**

**Field C — Explicit prohibition / release condition.**
Primary sources do **not** state a specific condition, event or
decision after which H4 execution becomes permitted. The sources
state only "NOT AUTHORIZED" and list open items.

**Field C value: NOT ESTABLISHED.**

### 6.2. OOS opening (D12)

**Field A — Authorization status.**
Primary source: `audit_research_roadmap_v1_h4_spec_v3_6_2_PROPOSED.md`
§12 (verbatim): "OOS remains SEALED."
Also: `audit_h4_final_predecision_audit_v1.md` §9: "OOS: SEALED."

**Field A value: SEALED. CONFIRMED FROM SOURCE.**

**Field B — Methodological readiness.**
Primary source: not stated separately for OOS. B inherits from D11
in the sense that OOS is downstream of H4 execution, but the source
does not fix a specific condition.

**Field B value: NOT ESTABLISHED for OOS specifically.**

**Field C — Explicit prohibition / release condition.**
Primary source: `audit_research_roadmap_v1_h4_spec_v3_4_PROPOSED.md`
§9 (verbatim): "OOS remains SEALED until separate authorization,
decided before viewing OOS results."

**Field C value: FORBIDDEN UNTIL SEPARATE AUTHORIZATION.
CONFIRMED FROM SOURCE.**

### 6.3. Correction to v2

v2 §6 combined A, B, C partly. v3 separates them explicitly.
No change to:

- H4 EXECUTION: NOT AUTHORIZED.
- OOS: SEALED.

**No permission for H4 execution or OOS opening is derived from
this review.**

---

## 7. EVIDENCE MATRIX — FILE PRESENCE AND HASHES

Fields:

- A — value recorded in a supplied report.
- B — full text readable in this dialog.
- C — physical existence on disk.
- D — SHA-256 independently recomputed from raw bytes.
- E — conclusion independently reproduced.

| # | File / statement | A | B | C | D | E |
|---|------------------|---|---|---|---|---|
| 1 | audit_h4_m3_eligibility_comparison_v1.md | yes | yes (via h4_sources_v4) | user-asserted only | no | no |
| 2 | audit_h4_final_predecision_audit_v1.md | yes | yes (via h4_sources_v4) | user-asserted only | no | no |
| 3 | audit_h4_range_atr_definition_proposal_v1.md | yes | yes (via h4_sources_v4) | user-asserted only | no | no |
| 4 | audit_h4_m5_report.txt | yes | yes (via h4_sources_v4) | user-asserted only | no | no |
| 5 | audit_h4_forensic_followup_v2_fast_qa_a2.csv | yes | yes (via h4_sources_v4) | user-asserted only | no | no |
| 6 | audit_h4_consolidated_open_decisions_register_v1.md | yes | yes (via h4_sources_v4) | user-asserted only | no | no |
| 7 | h4_sources_v4.txt | yes | yes | user-asserted only | no | no |
| 8 | evidence_v3.txt | yes | yes | user-asserted only | no | no |
| 9 | evidence_v2.txt | yes | yes | user-asserted only | no | no |
| 10 | 104 .py inventory (evidence_v3, block G) | yes | yes | user-asserted only | no | partial |

**Interpretation:**

- B=yes only for files transmitted verbatim in this dialog.
- The six source files are B=yes **only** because
  `h4_sources_v4.txt` contains them verbatim. Their own physical
  existence on disk (C) is **user-asserted**, not verified here.
- SHA-256 values are **A** — recorded in a supplied report. They
  are **not** D — not recomputed here.
- The 104-file inventory is **limited-scope**: it covers the files
  reachable by the earlier `extract_h4_evidence_v3.py` run, excluding
  `cache*`, `cache_2024_2025*`, `cache_other_tickers*`, `.git`,
  `__pycache__`. **It is not a proof about the whole filesystem.**

**No claim is made here that the assistant independently verified
any file's physical existence or recomputed any SHA-256.**

---

## 8. UPDATED DEPENDENCY MAP

Legend:

- `-->` : dependency confirmed by primary source.
- `-/-` : dependency not established (OPEN).
- `<=>` : confirmed cycle.
- `~`   : organisational order, not a mandatory prerequisite.

```
D1 (range_atr) --------------------\
                                    \
                                     --> T-1 --> M3 closure
                                    /         (source: "Without T-1,
D2 (session_key) ------------------/           M3 cannot be closed")

D2 --> D3 (endpoint vs full-window)
D2 --> D4 (bounds check)
D2 --> D5 (session_key[t] defined)

D3, D4, D5 : independent of each other.

D6 (interpretation of §6) -/- T-1   [OPEN]
D6 -/- M3 closure                   [OPEN]

D7 (M1) --> D8-QUANTILE
D8-CALENDAR   --> PC4
D8-DUPLICATES --> PC4
D8-STAT-UNDEF <=> PC3-UNDEF         [CONFIRMED CYCLE]
D8-RNG        <=> PC4               [CONFIRMED CYCLE]
D9 (PC1-PC5)  : internal deps as in §9.2 below
D10 (Q-NEW)   : independent
D11 (H4 execution)  : NOT AUTHORIZED + NOT READY; no release condition
D12 (OOS opening)   : SEALED + FORBIDDEN until separate authorization
```

Internal dependencies in the register (verbatim rows in
`audit_h4_consolidated_open_decisions_register_v1.md`):

- M2-STAT-UNDEF depends on M2-CALENDAR, M2-DUPLICATES, PC3.
- PC3-UNDEF depends on M2-STAT-UNDEF.
- M2-QUANTILE depends on M1.
- M2-RNG depends on PC4.
- PC4 depends on M2-CALENDAR, M2-DUPLICATES, M2-QUANTILE, M2-RNG.
- PC3-TRIGGER: no dependencies.
- PC1, PC2, PC5: no dependencies.
- M1: no dependencies.
- M2-CALENDAR, M2-DUPLICATES: no dependencies.
- Q-NEW: no dependencies.

**No claim of "No cycles"** is made in v3.

---

## 9. FINAL STATUS

Unchanged:

- M3: PARTIALLY RESOLVED.
- R-1: NOT DECIDED.
- M1: OPEN.
- M2: UNRESOLVED.
- PC1–PC5: PROPOSED / NOT AUTHORIZED.
- Q-NEW: OPEN / NOT DECIDED.
- H4 EXECUTION: NOT AUTHORIZED.
- OOS: SEALED.

STRATEGY LOGIC: UNCHANGED.
RESEARCH ONLY.
NO THRESHOLD IS OPTIMIZED.
NO FILTER IS INSTALLED.
NO LIVE ORDERS.

---

## 10. ISSUE TABLE

| Issue | Primary evidence | Finding | Status | Minimal next documentary step |
|-------|------------------|---------|--------|-------------------------------|
| W-1: mutual M2-STAT-UNDEF ↔ PC3-UNDEF | register rows M2-STAT-UNDEF, PC3-UNDEF | Both directions stated | CONFIRMED CYCLE | None — record as cycle in map |
| W-2: mutual M2-RNG ↔ PC4 | register rows M2-RNG, PC4 | Both directions stated | CONFIRMED CYCLE | None — record as cycle in map |
| W-3: M1 ↔ M2-QUANTILE | register rows M1, M2-QUANTILE | One direction only | NOT ESTABLISHED (reverse) | Remove reverse arrow |
| W-4: D6 order vs T-1 | m3 §7.4; final_predecision table | Sources do not fix order | OPEN | None — keep as OPEN |
| W-5: D6 criterion (clarification vs change) | m3 §3; final_predecision table | No decision rule given | OPEN | None — keep as OPEN |
| W-6: D11/D12 three fields | v3.6.2 §17, §12; v3.4 §9 | A, B, C separable | CONFIRMED FROM SOURCE | None |
| W-7: file B column | h4_sources_v4 | B valid only for transmitted texts | CONFIRMED FROM SOURCE | None — preserve wording |
| W-8: 104 .py inventory scope | evidence_v3 block G | Limited scope | CONFIRMED FROM SOURCE | None — preserve wording |
| W-9: SHA-256 evidence | h4_sources_v4 | A, not D | ASSERTED / not recomputed | None — do not upgrade |

---

## 11. MINIMAL NEXT DOCUMENTARY STEP

The minimal next step that is read-only and does not require any
methodological choice from the user:

1. No new operation is required to continue the current
   documentary audit. All supplied texts are readable in this
   dialog.
2. The two OPEN issues (W-4 D6/T-1 order; W-5 D6 criterion) cannot
   be closed by adding more documentary material from the project:
   they are decisions, not facts. **They remain OPEN until the user
   decides.**
3. The two confirmed cycles (W-1, W-2) are facts, not decisions.
   No further action is required to close them; they are recorded
   in §8.
4. T-1, H4 execution, and OOS opening are **not** part of the
   minimal next step. None is authorized.

**No data, no T-1, no execution.**

---

## 12. DECISIONS REQUIRED FROM HUMAN

This review does not ask the user to choose R-1a/b/c/d,
endpoint-only/full-window, q025/q05, or to authorize execution.

Items that remain user-decisions in the future (not requested
here):

- D6 order relative to T-1 — **OPEN**.
- D6 criterion (clarification vs change) — **OPEN**.
- R-1 normative definition — **NOT DECIDED**.
- Q1 normative session_key — **NOT DECIDED**.
- Q2/Q3/Q4 — **OPEN**.
- M1/M2/PC1–PC5/Q-NEW — **OPEN / PROPOSED / NOT AUTHORIZED**.

No choice is requested here.

---

## 13. CONFIRMATION

- No H4 effect was computed.
- No bootstrap was executed.
- No CI was computed.
- No data processing was performed.
- No T-1 was executed.
- OOS was not opened or analyzed.
- No specification was modified.
- No source file, data file, or prior report was modified.
- No live order was sent.
- No decision was taken on behalf of the user.