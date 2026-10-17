# audit_h4_decision_register_consistency_audit_v2.md

H4 CONSISTENCY AUDIT v1 — TARGETED CORRECTION REVIEW
Read-only documentary review only.

No data processing. No bootstrap. No CI. No T-1 execution.
No H4 execution. No spec, code, data or existing report modification.
No overwriting.

STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY
NO THRESHOLD IS OPTIMIZED
NO FILTER IS INSTALLED
NO LIVE ORDERS
OOS: SEALED. H4 EXECUTION: NOT AUTHORIZED.

---

## 1. SCOPE AND LIMITS

### 1.1. Inputs available in this dialog

- `audit_h4_decision_register_consistency_audit_v1.md` — the input
  document for this review, supplied in the user's previous message
  in full.
- `audit_h4_decision_register_source_verification_v1.md` — full
  text in an earlier user message.
- `h4_sources_v4.txt` — full text with line numbers in an earlier
  user message. Contains verbatim: six source files (register,
  m3-eligibility-comparison, final-predecision, range-atr-proposal,
  m5-report, qa_a2.csv).
- `audit_h4_evidence_reconciliation_matrix_v1.md` — full text in an
  earlier assistant message.
- `evidence_v2.txt`, `evidence_v3.txt` — full texts in earlier user
  messages, with line numbers.

### 1.2. What cannot be independently verified here

- Physical existence of any file on the user's disk.
- Actual byte content of any file not supplied verbatim in this
  dialog.
- Independently recomputed SHA-256 of any file.
- Line numbers beyond those shown in supplied texts.

Labels used:

- A — value recorded in a supplied report.
- B — content of the file is readable in the dialog.
- C — file physically exists on disk.
- D — SHA-256 independently recomputed from raw bytes.
- E — conclusion independently reproduced.

### 1.3. Boundaries

No calculation. No data. No source execution. No spec changes.
No decisions taken on behalf of the user.

---

## 2. CORRECTIONS TABLE FOR v1

| ID  | v1 statement (exact location) | Problem | Correction in v2 |
|-----|-------------------------------|---------|------------------|
| V2-1 | v1 §4 list B, step B4: "Решение D6 (статус v3.6.2 §6: clarification vs change vs leave open)" placed **before** B5 "авторизация T-1". | Order between D6 and T-1 is not established by primary sources. | Reclassified: D6 order relative to T-1 is **OPEN**. See §3. |
| V2-2 | v1 §3 "EVIDENCE STATUS TABLE": "SHA-256 and sizes of the six sources — CONFIRMED FROM SOURCE". | CONFIRMED FROM SOURCE is too strong. The SHA-256 values were **copied from a report** (`h4_sources_v4.txt`), not recomputed. | Reclassified as **A (recorded in supplied report)**. See §4. |
| V2-3 | v1 §3 "Six source files were read fully — CONFIRMED FROM SOURCE". | Only the file **contents as transmitted** are readable. Physical disk existence is not verified. | Split into B (readable content) and C (physical existence — NOT VERIFIED). See §4. |
| V2-4 | v1 §3 "File existence on disk — CONFIRMED FROM SOURCE (by user)". | Existence is asserted by user, not independently verified. | Reclassified as **C — ASSERTED BY USER, NOT INDEPENDENTLY VERIFIED**. See §4. |
| V2-5 | v1 §6 decision packet Q-A1: "DEFERRED. M1 ... Что должно произойти раньше: решения D1–D6 (закрытие M3)." | No primary source establishes that M1 must wait for M3 closure. | Reclassified as **OPTIONAL ORDER**, not required. See §5. |
| V2-6 | v1 §6 decision packet Q-A2: "DEFERRED. M2 ... Что должно произойти раньше: D1–D6 и авторизация T-1." | Same issue as V2-5. | Reclassified as **OPTIONAL ORDER**. See §5. |
| V2-7 | v1 §6 decision packet Q-A3: "DEFERRED. PC1–PC5 ... Что должно произойти раньше: D1–D6." | Same issue as V2-5. | Reclassified as **OPTIONAL ORDER**. See §5. |
| V2-8 | v1 §6 decision packet Q-A4: "DEFERRED. Q-NEW ... Что должно произойти раньше: D1–D6." | Same issue as V2-5. | Reclassified as **OPTIONAL ORDER**. See §5. |
| V2-9 | v1 §6 Q-C2 and Q-C3: "Авторизация H4 execution" and "Авторизация открытия OOS" are stated as a single cascade. | Three separate notions are mixed: not-authorized, not-methodologically-ready, forbidden-until-specific-decision. | Split into three columns. See §6. |
| V2-10 | v1 §3 "No missing sources for D1–D12 classification — ASSERTED BUT NOT INDEPENDENTLY VERIFIED". | Already correctly classified in v1. No change. | Keep as is. |
| V2-11 | v1 §5 dependency map: "D1 → T-1" and "D2 → D3, D4, D5" — this part is consistent with primary sources. | Correct in v1. | Keep. See §7. |
| V2-12 | v1 §5 dependency map did not state where D6 sits relative to T-1. | Missing. | Add explicitly: D6 vs T-1 order **OPEN**. See §7. |

---

## 3. D6 AND T-1: ORDER VERIFICATION

### 3.1. What T-1 is, per primary sources

From `audit_h4_m3_eligibility_comparison_v1.md` §7.3 and §7.4
(readable in `h4_sources_v4.txt`):

> "By source/data (T-1, read-only): Actual affected-bar counts for
> S1, S2, S3."

> "T-1 is run read-only and reports actual affected-bar counts."

**Definition established:** T-1 = read-only **computation on the
datasets** of the actual affected-bar counts for the three
substantive differences (R7, R8, R9).

T-1 is **not** "any comparison of specifications". It is a data-side
operation. The documentary comparison of v3.4 §5.2 and v3.6.2 §6 is
a separate activity already performed in
`audit_h4_m3_eligibility_comparison_v1.md` §4.

### 3.2. What D6 asks, per primary sources

From `audit_h4_final_predecision_audit_v1.md` table row "M3":

> "Whether v3.6.2 §6 is a clarification or a change to the intended
> eligible set."

From `audit_research_roadmap_v1_h4_spec_v3_6_2_PROPOSED.md` §14:

> "M3. Consistency of §6 (this document) with D1-D7 from v3.4 §11.
> A targeted source audit is required to compare v3.4 and v3.6.2
> word-for-word. Until that audit is performed on the actual files,
> M3 remains OPEN."

**Definition established:** D6 is a **textual interpretation
decision** about whether the differences between v3.4 §5.2 and
v3.6.2 §6 alter the intended eligible set or only clarify it.

### 3.3. Does T-1 need to be executed before D6 can be decided?

**Answer: not established by the primary sources.**

Reason:

- D6 is defined in terms of **wording** ("clarification or change
  to the intended eligible set"). Wording comparison is a documentary
  activity, done in `audit_h4_m3_eligibility_comparison_v1.md`.
- T-1 is defined as **data-side counting of affected bars**.
- No primary source states that the decision "clarification vs
  change" requires the count of affected bars.

- `audit_h4_m3_eligibility_comparison_v1.md` §7.4 lists
  "T-1 to measure actual differences" as a **separate step**,
  not as a prerequisite for the interpretation decision.

**Label: OPEN ORDER.** D6 and T-1 are not causally ordered by the
primary sources.

### 3.4. Can D6 be decided before T-1 without assumptions?

**Answer: not established by the primary sources.**

The question is whether a reader can decide "clarification vs
change" from wording alone. This depends on whether the reader
considers the three substantive differences (R7, R8, R9) to be
in-scope for the confirmatory estimand, or out-of-scope.

- If in-scope → the differences are "a change" unless the reader
  asserts they were always intended.
- If out-of-scope → the differences are "clarification".

**Label: OPEN ORDER.** The decision rule for D6 is not fixed by
the primary sources.

### 3.5. Is the proposed order B1–B6 in v1 circular?

**Answer: not circular, but not proven either.** v1 §4 list B
placed D6 (B4) before T-1 (B5). This is **one possible order**.
Nothing in the primary sources states that D6 must come before T-1.
**Label: POSSIBLE ORDER, NOT REQUIRED ORDER.**

### 3.6. Can a purely documentary comparison happen first?

**Answer: yes, and it already happened.**
`audit_h4_m3_eligibility_comparison_v1.md` §4 is exactly this
comparison: eleven rules, eight identical, three substantive.
This is **not T-1** under the source's own definition (§3.1 above).

**Label: CONFIRMED FROM SOURCE** — the documentary comparison
exists and is not T-1.

### 3.7. Conclusion of §3

- **D6 / T-1 order: OPEN.** Not established by primary sources.
- **Documentary comparison of specifications: already performed**
  (m3-eligibility-comparison). Not T-1.
- v1's placement of D6 before T-1 is **a possible order**, not
  a required one. This is a POSSIBLE ISSUE in v1, now corrected.

---

## 4. EVIDENCE MATRIX FOR FILES AND HASHES

Classification used:

- A — value recorded in a supplied report.
- B — content of the file is readable in the dialog.
- C — file physically exists on disk.
- D — SHA-256 independently recomputed from raw bytes.
- E — conclusion independently reproduced.

| # | Statement                                                       | A | B | C | D | E | Status                            |
|---|-----------------------------------------------------------------|---|---|---|---|---|-----------------------------------|
| 1 | audit_h4_m3_eligibility_comparison_v1.md, SHA 0d2dfacd…, 12532 B | yes | yes | user-asserted | no | no | A + B; C asserted; D not done   |
| 2 | audit_h4_final_predecision_audit_v1.md, SHA e9abf675…, 15103 B   | yes | yes | user-asserted | no | no | A + B; C asserted; D not done   |
| 3 | audit_h4_range_atr_definition_proposal_v1.md, SHA de1854ad…      | yes | yes | user-asserted | no | no | A + B; C asserted; D not done   |
| 4 | audit_h4_m5_report.txt, SHA 5d34c2e8…                            | yes | yes | user-asserted | no | no | A + B; C asserted; D not done   |
| 5 | audit_h4_forensic_followup_v2_fast_qa_a2.csv, SHA 225ce133…      | yes | yes | user-asserted | no | no | A + B; C asserted; D not done   |
| 6 | audit_h4_consolidated_open_decisions_register_v1.md, SHA 9705f5b2… | yes | yes | user-asserted | no | no | A + B; C asserted; D not done   |
| 7 | h4_sources_v4.txt, SHA DBDE6458…, 74658 B                        | yes | yes | user-asserted | no | no | A + B; C asserted; D not done   |
| 8 | evidence_v3.txt, SHA D10462EF…, 63685 B                          | yes | yes | user-asserted | no | no | A + B; C asserted; D not done   |
| 9 | evidence_v2.txt, SHA 7E9EAC67…, 462321 B                         | yes | yes | user-asserted | no | no | A + B; C asserted; D not done   |
| 10 | audit_h4_decision_register_source_verification_v1.md, SHA A351DA97… | yes | yes | user-asserted | no | no | A + B; C asserted; D not done |
| 11 | audit_h4_decision_register_consistency_audit_v1.md, SHA 68843A1B… | yes | yes | user-asserted | no | no | A + B; C asserted; D not done |
| 12 | Six sources read fully (content)                                 | yes | yes | user-asserted | no | no | B: content readable; C/D/E not  |
| 13 | Two previously flagged files exist                               | yes | no | user-asserted | no | no | A + C asserted; B not in dialog |
| 14 | Absence of H4 eligibility implementation in main tree            | yes | yes | — | no | partial | E: partially reproduced on 104 .py files, cache* excluded |

Legend for "Status":

- B: readable in this dialog.
- C user-asserted: file existence stated by user, not checked here.
- D not done: no independent byte recomputation.
- E partial: reproduced on evidence_v3's 104-file inventory, not on the whole filesystem.

### 4.1. Correction to v1 wording

v1 §3 used "CONFIRMED FROM SOURCE" for items #1, #2, #3, #11, #12.
v2 reclassifies those as **A + B** (recorded + readable), with C
(user-asserted) and D (not done) explicitly separated.

**No claim is made in v2 that the assistant independently verified
any file's physical existence or recomputed any SHA-256.**

### 4.2. Conclusion of §4

- **Content of six sources: readable in dialog (B).**
- **SHA-256 values: recorded in reports (A). Not recomputed (D).**
- **Physical file existence: user-asserted (C). Not independently
  checked.**
- **Absence of H4 eligibility in the main tree: partially reproduced
  on 104 .py files (E partial).**

---

## 5. DEPENDENCIES M1 / M2 / PC1–PC5 / Q-NEW

Task: verify whether primary sources actually require M3 closure
before deciding M1 and M2.

### 5.1. Types of relation

- Logical dependency — deciding X presupposes knowing Y.
- Organisational order — chosen by the user, not imposed by sources.
- Mandatory prerequisite — explicitly required by a source.

### 5.2. What primary sources state about M1, M2, PC1–PC5, Q-NEW

From `audit_h4_consolidated_open_decisions_register_v1.md`:

- M1 row: "Explicit user authorization required. Dependencies: none."
- M2-CALENDAR row: "Dependencies: none."
- M2-DUPLICATES row: "Dependencies: none."
- M2-STAT-UNDEF row: "Dependencies: M2-CALENDAR, M2-DUPLICATES, PC3."
- M2-QUANTILE row: "Dependencies: M1."
- M2-RNG row: "Dependencies: PC4."
- PC1 row: "Dependencies: none."
- PC2 row: "Dependencies: none."
- PC3-TRIGGER row: "Dependencies: none."
- PC3-UNDEF row: "Dependencies: M2-STAT-UNDEF."
- PC4 row: "Dependencies: M2-CALENDAR, M2-DUPLICATES, M2-QUANTILE, M2-RNG."
- PC5 row: "Dependencies: none."
- Q-NEW row: "Dependencies: none."

From `audit_h4_final_predecision_audit_v1.md` §5:
list of items D-1 … D-13 that "require explicit user authorization"
— none of these rows cites M3 closure as a prerequisite.

### 5.3. Findings

- **No primary source states that M1 requires M3 closure.**
  Label: **NOT ESTABLISHED**.
- **No primary source states that M2 requires M3 closure.**
  Label: **NOT ESTABLISHED**.
- **No primary source states that PC1–PC5 require M3 closure.**
  Label: **NOT ESTABLISHED**.
- **No primary source states that Q-NEW requires M3 closure.**
  Label: **NOT ESTABLISHED**.

The only internal dependencies stated by the sources are the ones
listed in §5.2 — none of which points to M3.

### 5.4. Correction to v1 decision packet

v1 §6 Q-A1–Q-A4 marked M1, M2, PC1–PC5 and Q-NEW as DEFERRED
"until D1–D6". No source supports this.

Corrected labels:

- M1: **OPTIONAL ORDER**. User may decide before or after M3.
- M2: **OPTIONAL ORDER**.
- PC1–PC5: **OPTIONAL ORDER**.
- Q-NEW: **OPTIONAL ORDER**.

The user is not required to close M3 first.

### 5.5. What remains mandatory

From the sources: none of these are mandatory prerequisites for
each other, except the internal ones already listed (M2-QUANTILE ↔
M1, M2-STAT-UNDEF ↔ PC3-UNDEF, M2-* → PC4). No cross-dependency to
M3 is established.

**Label: OPTIONAL ORDER for cross-M3 relations.**

---

## 6. D11 / D12 STATUS SPLIT

Three distinct statuses must be separated:

1. **Not authorized** — no user permission given.
2. **Not methodologically ready** — required methodological
   decisions not yet made.
3. **Forbidden until specific decision or verification** — the
   source explicitly prohibits execution before some condition.

### 6.1. H4 execution (D11)

From `audit_research_roadmap_v1_h4_spec_v3_6_2_PROPOSED.md` §17:

> "NOT AUTHORIZED FOR EXECUTION.
> NOT READY: U1, U1b, U3-U5, M1-M3, QA-A1, PC1-PC5 open."

From `audit_h4_final_predecision_audit_v1.md` §9 final status:

> "H4 EXECUTION: NOT AUTHORIZED."

Therefore:

- Status 1 (not authorized): **CONFIRMED FROM SOURCE**.
- Status 2 (not ready): **CONFIRMED FROM SOURCE** — the same §17
  lists open items.
- Status 3 (forbidden until specific decision): **NOT ESTABLISHED**.
  No source states "H4 execution is forbidden until decision X".

### 6.2. OOS opening (D12)

From `audit_research_roadmap_v1_h4_spec_v3_6_2_PROPOSED.md` §12:

> "OOS remains SEALED."

From `audit_h4_final_predecision_audit_v1.md` §9:

> "OOS: SEALED."

Therefore:

- Status 1 (not authorized): **CONFIRMED FROM SOURCE**.
- Status 2 (not ready): applies — OOS opening depends on H4
  execution being authorized and on all prior methodological
  decisions.
- Status 3 (forbidden until specific decision): **CONFIRMED FROM
  SOURCE**, because §12 explicitly says "remains SEALED" without
  naming a release condition.

### 6.3. Correction to v1

v1 §6 Q-C2/Q-C3 mixed "not authorized" and "forbidden until
decision" into a single cascade. v2 separates them:

- D11 = (1) + (2), not (3).
- D12 = (1) + (2) + (3).

**H4 EXECUTION: NOT AUTHORIZED. OOS: SEALED.** — unchanged.

---

## 7. UPDATED DEPENDENCY MAP

```
D1 (range_atr) --------------------\
                                    \
                                     --> T-1 --> M3 closure
                                    /
D2 (session_key) ------------------/
     |
     +--> D3 (endpoint vs full-window)
     +--> D4 (bounds check)
     +--> D5 (session_key[t] defined)

D3, D4, D5 are independent of each other.

D6 (interpretation of §6: clarification vs change)
   D6 order relative to T-1: OPEN.

D7 (M1) <--> D8-QUANTILE
D8-CALENDAR   --> PC4
D8-DUPLICATES --> PC4
D8-STAT-UNDEF <--> PC3-UNDEF
D8-RNG        --> PC4
D9 (PC1-PC5) — internal dependencies as in §5.2
D10 (Q-NEW) — independent
D11 (H4 execution) — NOT AUTHORIZED + NOT READY
D12 (OOS opening)  — NOT AUTHORIZED + NOT READY + FORBIDDEN until release
```

Checks:

- No cycles.
- All arrows are directly supported by primary sources, except the
  D6 ↔ T-1 relation, which is **OPEN**.

---

## 8. MINIMAL NEXT STEP

The minimal next step **that does not require any methodological
decision from the user**:

1. **No new operations are required to continue the read-only
   documentary audit.** All currently supplied sources are readable
   in this dialog.
2. If the user wants a **further documentary** step with no
   methodological decisions, the following is available:
   - Compare v3.4 §11 (D1-D7) and v3.6.2 §6 (a)-(k) in wording
     only, extending the existing
     `audit_h4_m3_eligibility_comparison_v1.md` to any remaining
     pair of rules not already covered.
   - Re-read `audit_h4_remaining_open_items_v1.md` and
     `audit_h4_m2_forensic_bootstrap_methodology_audit_v1.md` if
     they are supplied in the dialog — they are not yet supplied
     here.
3. **T-1, H4 execution, and OOS opening are not part of the minimal
   next step.** None is authorized.

**No new files, no data, no calculation.**

---

## 9. FINAL STATUS AND OPEN ITEMS

Project statuses — unchanged:

M3: PARTIALLY RESOLVED.
R-1: NOT DECIDED.
M1: OPEN.
M2: UNRESOLVED.
PC1–PC5: PROPOSED / NOT AUTHORIZED.
Q-NEW: OPEN / NOT DECIDED.
H4 EXECUTION: NOT AUTHORIZED.
OOS: SEALED.

Open items from this review:

- O-1. D6 order relative to T-1 — **OPEN** (not established by
  primary sources).
- O-2. Physical existence and SHA-256 of six sources — not
  independently verified in this dialog; only user-asserted.
- O-3. M1/M2/PC1–PC5/Q-NEW — organisational order relative to M3
  — **OPTIONAL**, not required.
- O-4. `audit_h4_remaining_open_items_v1.md` and
  `audit_h4_m2_forensic_bootstrap_methodology_audit_v1.md` —
  content not supplied in this dialog; existence asserted by user.

No decision was taken on behalf of the user. No calculation was
performed. No file was modified.

---

## 10. DECISIONS REQUIRED FROM HUMAN

The following decision is required **only if** the user wishes to
proceed toward closing M3 and running T-1. It is not required to
continue the current read-only documentary audit.

- **Q-B1 (D1 — R-1).** Which formula for `range_atr` is normative
  for H4? Options are listed in
  `audit_h4_range_atr_definition_proposal_v1.md` §7 (R-1a/b/c/d).
- **Q-B2 (D2 — Q1).** Which definition of `session_key` is
  normative for H4?
- **Q-B3 (D3 — Q2).** Endpoint-only (v3.4 §5.2(a)) or full-window
  (v3.6.2 §6(k))?
- **Q-B4 (D4 — Q3).** Explicit bounds check or implicit?
- **Q-B5 (D5 — Q4).** Is explicit `session_key[t]`-defined check
  required?
- **Q-B6 (D6).** Status of v3.6.2 §6 relative to v3.4 §5.2
  (clarification / change / leave M3 OPEN)? The order of D6
  relative to T-1 remains **OPEN** until the user states it.

Not requested now:

- R-1a/b/c/d choice is not requested here as an immediate action;
  it is listed only as an open item for future consideration.
- Endpoint-only vs full-window choice is not requested here.
- q025 vs q05 choice is not requested here.
- Authorization of H4 execution and OOS opening are not requested
  here.

**H4 EXECUTION: NOT AUTHORIZED. OOS: SEALED.** — unchanged by this
review.

---

## 11. CONFIRMATION

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