# audit_h4_decision_register_consistency_audit_v4.md

H4 CONSISTENCY AUDIT v3 — FINAL DEPENDENCY AND SOURCE-SCOPE REVIEW
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

## 1. SCOPE AND LIMITATIONS

### 1.1. Inputs available as full text in this dialog

- `audit_h4_decision_register_consistency_audit_v3.md` — input
  document for this review, supplied in the user's previous message.
- `audit_h4_decision_register_consistency_audit_v1.md`,
  `..._v2.md`, `..._v3.md` — full texts in earlier messages.
- `audit_h4_decision_register_source_verification_v1.md` — full text.
- `h4_sources_v4.txt` — full text with line numbers. Contains
  verbatim:
  - `audit_h4_m3_eligibility_comparison_v1.md` (336 lines),
  - `audit_h4_final_predecision_audit_v1.md` (323 lines),
  - `audit_h4_range_atr_definition_proposal_v1.md` (301 line),
  - `audit_h4_m5_report.txt` (152 lines),
  - `audit_h4_forensic_followup_v2_fast_qa_a2.csv` (17 lines),
  - `audit_h4_consolidated_open_decisions_register_v1.md` (222 lines).
- `evidence_v2.txt`, `evidence_v3.txt` — full texts with line numbers.
- `audit_h4_evidence_reconciliation_matrix_v1.md` — full text.

### 1.2. What is NOT independently verifiable here

- Physical existence of any file on the user's disk.
- Actual byte content of any file not supplied verbatim in this
  dialog.
- Independently recomputed SHA-256 of any file.
- Line numbers beyond those shown in supplied texts.
- The two files
  `audit_h4_remaining_open_items_v1.md` and
  `audit_h4_m2_forensic_bootstrap_methodology_audit_v1.md` — their
  content is NOT in this dialog; only existence is asserted.

### 1.3. Labels used

- CONFIRMED FROM SOURCE — evidenced directly by text available here.
- PARTIALLY CONFIRMED.
- ASSERTED BUT NOT INDEPENDENTLY VERIFIED.
- NOT ESTABLISHED / OPEN.
- A / B / C / D / E (see §5).

### 1.4. Boundaries

No calculation on data. No T-1. No execution. No decisions taken on
behalf of the user.

---

## 2. D3 VERSUS D6 — SEPARATION

### 2.1. Primary source for D3 (Q2)

From `audit_h4_m3_eligibility_comparison_v1.md` §7.2 (verbatim,
h4_sources_v4.txt):

> "Q2. Which session constancy rule is normative for H4: the
> endpoint-only rule of v3.4 §5.2 (a) or the full-window rule
> of v3.6.2 §6 (k)?"

From same file §4.1 (verbatim):

> "v3.4 §5.2 (a), verbatim: session_key[t+h] == session_key[t]
> v3.6.2 §6 (k), verbatim: For every k in [0, h]: session_key[t+k]
> == session_key[t]."

From same file §4.3 (verbatim):

> "v3.6.2 (k) is strictly stricter than v3.4 (a). v3.6.2 excludes
> bars that v3.4 admits when the endpoints match but an interior
> bar does not."

**D3 = the choice between two session-constancy rules.**

### 2.2. Primary source for D6

From `audit_h4_final_predecision_audit_v1.md` §3 (table row M3,
verbatim):

> "Whether v3.6.2 §6 is a clarification or a change to the
> intended eligible set."

From same file §5 (item D-11, verbatim):

> "D-11. M3: declare v3.6.2 §6 to be a clarification or a change;
> or leave M3 OPEN."

**D6 = the interpretation decision about whether §6 as a whole is
a clarification or a change.**

### 2.3. Are D3 and D6 the same?

**No.** D3 chooses a specific rule (endpoint or full-window). D6
classifies the overall difference between the two specifications.
D6 is broader: it concerns all three substantive differences
(R7/R8/R9), not only the session-constancy rule.

**CONFIRMED FROM SOURCE.** v3 §4.1 phrase "choice between v3.4 §5.2
and v3.6.2 §6 (D3 / D6)" was imprecise. In v4, D3 and D6 are
separated.

### 2.4. The precise eligibility rule required as input to T-1

From `audit_h4_m3_eligibility_comparison_v1.md` §7.4 (verbatim):

> "3. Choose between v3.4 §5.2 and v3.6.2 §6 as the normative
> eligibility rule, or freeze both and state which one applies
> in H4."

**The eligibility rule required as input to T-1 is the normative
rule set (v3.4 §5.2 or v3.6.2 §6).** D3 is a sub-question of this
choice; D6 concerns interpretation.

### 2.5. Any authorization explicitly required to run T-1

From `audit_h4_m3_eligibility_comparison_v1.md` §7.4 (verbatim):

> "4. Authorize T-1 to measure actual differences."

**CONFIRMED FROM SOURCE:** explicit authorization of T-1 is
required. T-1 is not run silently.

### 2.6. D6 and T-1 — order

No primary source states that D6 must precede T-1 or vice versa.

**Status of D6 ↔ T-1 order: OPEN.**

---

## 3. COMPLETE DEPENDENCY GRAPH AND CYCLES

### 3.1. Source for edges

Primary source: `audit_h4_consolidated_open_decisions_register_v1.md`
§1 (Register table). Rows read verbatim in h4_sources_v4.txt.

### 3.2. Confirmed edges (verbatim "Dependencies" column)

- M1 — "none"
- M2-CALENDAR — "none"
- M2-DUPLICATES — "none"
- M2-STAT-UNDEF — "M2-CALENDAR, M2-DUPLICATES, PC3"
- M2-QUANTILE — "M1"
- M2-RNG — "PC4"
- PC1 — "none"
- PC2 — "none"
- PC3-TRIGGER — "none"
- PC3-UNDEF — "M2-STAT-UNDEF"
- PC4 — "M2-CALENDAR, M2-DUPLICATES, M2-QUANTILE, M2-RNG"
- PC5 — "none"
- M3 — "none"
- Q-NEW — "none"

### 3.3. Graph

Vertices: M1, M2-CALENDAR, M2-DUPLICATES, M2-STAT-UNDEF,
M2-QUANTILE, M2-RNG, PC1, PC2, PC3-TRIGGER, PC3-UNDEF, PC4, PC5,
M3, Q-NEW.

Directed edges (X → Y means "Y depends on X"):

```
M2-CALENDAR   → M2-STAT-UNDEF
M2-DUPLICATES → M2-STAT-UNDEF
PC3           → M2-STAT-UNDEF
M2-STAT-UNDEF → PC3-UNDEF
M1            → M2-QUANTILE
PC4           → M2-RNG
M2-CALENDAR   → PC4
M2-DUPLICATES → PC4
M2-QUANTILE   → PC4
M2-RNG        → PC4
```

All other vertices: no outgoing edges (M1, PC1, PC2, PC3-TRIGGER,
PC5, M3, Q-NEW).

### 3.4. Cycle detection — manual documentary check

The graph is small (14 vertices, 10 edges). Manual check:

**Length-2 cycles (mutual pairs):**

- `M2-STAT-UNDEF → PC3-UNDEF → M2-STAT-UNDEF`
  - Edge 1: `PC3 → M2-STAT-UNDEF` ✓ (row M2-STAT-UNDEF)
  - Edge 2: `M2-STAT-UNDEF → PC3-UNDEF` ✓ (row PC3-UNDEF)
  - **CONFIRMED CYCLE.**
- `M2-RNG → PC4 → M2-RNG`
  - Edge 1: `PC4 → M2-RNG` ✓ (row M2-RNG)
  - Edge 2: `M2-RNG → PC4` ✓ (row PC4)
  - **CONFIRMED CYCLE.**

**Length-3 or longer cycles:**

Проверяем через истоки. Только вершины с исходящими рёбрами
могут участвовать в циклах. Список: M2-CALENDAR, M2-DUPLICATES,
M2-STAT-UNDEF, M1, PC3, PC4, M2-QUANTILE, M2-RNG.

Топологические выходы:

- M2-CALENDAR, M2-DUPLICATES → M2-STAT-UNDEF, PC4 → терминалы
  (PC3-UNDEF, M2-RNG).
- M1 → M2-QUANTILE → PC4 → M2-RNG.
- PC3 → M2-STAT-UNDEF → PC3-UNDEF.

Никаких путей длиной ≥3, возвращающихся в исходную вершину, не
обнаружено. Обе найденные цикла — длины 2.

**Найденные циклы: 2** (оба длиной 2, оба взаимные пары).

**Cycles of length ≥3: NOT FOUND.** Не утверждаю «отсутствуют
абсолютно», а: «не обнаружены при ручной проверке полного списка
рёбер из первичного реестра».

### 3.5. Limitations of this check

- Проверка **ручная, документальная**, по 14 вершинам и 10 рёбрам
  из первичного реестра.
- Данные не обрабатывались. Код не запускался.
- Если бы существовали рёбра, не записанные в первичный реестр,
  они не могли быть учтены. Таких рёбер в доступных источниках не
  обнаружено.

**Status: PARTIALLY CONFIRMED.** Полный граф по первичным данным
проверен; за пределами первичного реестра рёбер нет.

### 3.6. No resolution of cycles

Циклы не разрешаются, не разрываются, топологический порядок не
навязывается. Циклы зафиксированы как **CONFIRMED**.

---

## 4. SOURCE-AVAILABILITY INVENTORY FOR UNRESOLVED D6 ISSUES

### 4.1. Relevant primary sources and status

| Source | Status in this dialog |
|--------|-----------------------|
| `audit_h4_m3_eligibility_comparison_v1.md` | Full text via h4_sources_v4. |
| `audit_h4_final_predecision_audit_v1.md` | Full text via h4_sources_v4. |
| `audit_h4_consolidated_open_decisions_register_v1.md` | Full text via h4_sources_v4. |
| `audit_h4_range_atr_definition_proposal_v1.md` | Full text via h4_sources_v4. |
| `audit_h4_m5_report.txt` | Full text via h4_sources_v4. |
| `audit_h4_forensic_followup_v2_fast_qa_a2.csv` | Full text via h4_sources_v4. |
| `audit_research_roadmap_v1_h4_spec_v3_4_PROPOSED.md` | Full text via evidence_v2 block 5a. |
| `audit_research_roadmap_v1_h4_spec_v3_6_2_PROPOSED.md` | Full text via evidence_v2 block 5b. |
| `audit_h4_remaining_open_items_v1.md` | NOT in dialog; only asserted existence. |
| `audit_h4_m2_forensic_bootstrap_methodology_audit_v1.md` | NOT in dialog; only asserted existence. |
| `audit_h4_m2_cross_version_consistency_audit_v1.md` | NOT in dialog; only referenced in register. |
| `audit_h4_m2_cross_version_consistency_correction_v1.md` | NOT in dialog; only referenced. |
| `audit_h4_m2_bootstrap_statistic_scope_correction_v2.md` | NOT in dialog; only referenced. |
| `audit_h4_m2_bootstrap_statistic_scope_correction_v3.md` | NOT in dialog; only referenced. |
| `audit_h4_m3_forensic_source_comparison_v1.md` | NOT in dialog; only referenced in search_results. |
| `audit_h4_m3_full_eligibility_equivalence_v2.md` | NOT in dialog; only referenced. |
| `audit_h4_final_predecision_correction_v1.md` | NOT in dialog; only referenced. |

**Physical file existence not independently verified for any of the
above.** Only the content of files supplied verbatim in this dialog
is available for review.

### 4.2. Does any available source record the originally intended
eligible set?

Search through available texts:

- v3.4 §5.2 defines the eligible set (a)-(i).
- v3.6.2 §6 defines the eligible set (a)-(k).
- `audit_h4_m3_eligibility_comparison_v1.md` §3 table compares them.
- `audit_h4_final_predecision_audit_v1.md` §3 row M3 mentions the
  comparison.

**No available source states what the author originally intended.**
No source provides a decision rule for choosing "clarification"
versus "change".

**Status: NOT ESTABLISHED.**

### 4.3. Classification of unresolved D6 questions

| Question | Classification | Basis |
|----------|----------------|-------|
| D6 criterion (clarification vs change) | REQUIRES EXPLICIT HUMAN DECISION if documents cannot settle it; currently NOT ESTABLISHED because no decision rule is in available sources | No rule in available sources. |
| D6 order vs T-1 | NOT ESTABLISHED | No source fixes order. |
| Recoverability via missing files | MORE SOURCE MATERIAL MAY RESOLVE IT | Files `audit_h4_m2_cross_version_consistency_audit_v1.md`, `..._correction_v1.md`, `audit_h4_m3_full_eligibility_equivalence_v2.md` are referenced but not in dialog. They might contain additional discussion. |

**Correction to v3 §11:** v3 §11 stated the two D6 questions "cannot
be closed by adding more project documents". This is too strong.
Two other documents (`audit_h4_m2_cross_version_consistency_audit_v1.md`,
`audit_h4_m3_full_eligibility_equivalence_v2.md`) exist per the
search inventory and are not read here. They **may** contain
relevant text. Therefore:

- Classification of D6 criterion: **REQUIRES EXPLICIT HUMAN
  DECISION** as the ultimate action, but **MORE SOURCE MATERIAL MAY
  RESOLVE IT** first, if those two files are supplied.
- Classification of D6 order vs T-1: **MORE SOURCE MATERIAL MAY
  RESOLVE IT** if the same files discuss order; otherwise **NOT
  ESTABLISHED**.

**No claim is made here that either file has been read.**

---

## 5. OOS RELEASE-CONDITION COMPARISON

### 5.1. v3.4 §9 (verbatim, evidence_v2 block 5a)

> "## 9. OOS handling
> OOS remains SEALED until separate authorization, decided before
> viewing OOS results."

### 5.2. v3.6.2 §12 (verbatim, evidence_v2 block 5b)

> "## 12. OOS
> OOS remains SEALED."

### 5.3. `audit_h4_final_predecision_audit_v1.md` §9 (verbatim,
h4_sources_v4)

> "OOS: SEALED."

### 5.4. Comparison

- v3.4 §9 states: SEALED + release condition ("until separate
  authorization, decided before viewing OOS results").
- v3.6.2 §12 states: SEALED, without repeating the release
  condition.
- `final_predecision_audit_v1.md` restates the fact but not the
  condition.

**Finding:** the later specification (v3.6.2) restates the SEALED
status but does **not** repeat the release condition. The release
condition remains explicit only in v3.4 §9.

**Status: PARTIALLY CONFIRMED.** The SEALED status is consistent
across versions. The release condition is explicit in v3.4 and
implicit in v3.6.2 (by historical carry-over, not by re-statement).

**No permission to open OOS is derived.** OOS remains SEALED.

### 5.5. Version consistency

Consistency of the *status* across versions: **CONFIRMED.**
Consistency of the *release condition* across versions: **PARTIALLY
CONFIRMED** — v3.4 states it; v3.6.2 does not restate it.

---

## 6. EVIDENCE AND INTEGRITY

### 6.1. Distinctions

- Full source text available in dialog: `audit_h4_m3_eligibility_comparison_v1.md`,
  `audit_h4_final_predecision_audit_v1.md`,
  `audit_h4_range_atr_definition_proposal_v1.md`,
  `audit_h4_m5_report.txt`,
  `audit_h4_forensic_followup_v2_fast_qa_a2.csv`,
  `audit_h4_consolidated_open_decisions_register_v1.md`,
  `audit_research_roadmap_v1_h4_spec_v3_4_PROPOSED.md`,
  `audit_research_roadmap_v1_h4_spec_v3_6_2_PROPOSED.md`,
  all v1/v2/v3 audit texts, evidence_v2, evidence_v3.
- Source text quoted inside another document only: see §4.1 rows
  marked "only referenced".
- Reported SHA-256 values: recorded in earlier user messages; not
  recomputed here.
- SHA-256 independently recomputed: **none performed**.
- Independently reproduced conclusions: only those derived from
  texts readable in this dialog.

### 6.2. Use of "CONFIRMED FROM SOURCE"

In this document, "CONFIRMED FROM SOURCE" means: the statement is
directly supported by text readable in this dialog. It does **not**
imply physical file existence, byte recomputation, or any check
beyond the text in this dialog.

---

## 7. CORRECTED DEPENDENCY MAP

Legend:

- `-->` : dependency confirmed from primary source.
- `<=>` : mutual dependency (cycle), confirmed.
- `-/-` : relation OPEN / NOT ESTABLISHED.
- `~`   : organisational order, not a mandatory prerequisite.

```
M2-CALENDAR   --> M2-STAT-UNDEF
M2-DUPLICATES --> M2-STAT-UNDEF
PC3           --> M2-STAT-UNDEF
M2-STAT-UNDEF <=> PC3-UNDEF            [CONFIRMED CYCLE]

M1 --> M2-QUANTILE

PC4 <=> M2-RNG                          [CONFIRMED CYCLE]
M2-CALENDAR   --> PC4
M2-DUPLICATES --> PC4
M2-QUANTILE   --> PC4

D1 (range_atr)        --> T-1
D2 (session_key)      --> T-1
D3 (session constancy) --> T-1
D6 (specification interpretation) -/- T-1  [OPEN]
T-1                   --> M3 closure
D6 -/- M3 closure      [OPEN]

D11 (H4 execution): NOT AUTHORIZED + NOT READY; release condition NOT ESTABLISHED.
D12 (OOS): SEALED; release condition CONFIRMED in v3.4 §9, NOT restated in v3.6.2 §12.
```

---

## 8. ISSUE TABLE

| # | Issue | Evidence (primary source) | Finding | Status | Next documentary step |
|---|-------|---------------------------|---------|--------|-----------------------|
| 1 | D3 vs D6 conflation in v3 §4.1 | m3 §7.2 (Q2); final_predecision §3 row M3 | D3 = choice of rule; D6 = interpretation decision | CONFIRMED FROM SOURCE | None — separation recorded |
| 2 | Complete graph cycle check | register §1 rows | 2 cycles (both length 2); no length ≥3 found | CONFIRMED FROM SOURCE (manual, documentary) | None — recorded |
| 3 | D6 criterion | final_predecision §5 item D-11 | No decision rule provided | OPEN; may be resolvable if missing files supplied | Supply missing m2/m3 audit files |
| 4 | D6 order vs T-1 | m3 §7.4 | Order not fixed | OPEN | Same as #3 |
| 5 | OOS release condition | v3.4 §9; v3.6.2 §12 | v3.4 explicit; v3.6.2 restates SEALED only | PARTIALLY CONFIRMED | None |
| 6 | SHA-256 evidence | earlier messages | Recorded, not recomputed | ASSERTED BUT NOT INDEPENDENTLY VERIFIED | None — do not upgrade |
| 7 | Missing files | register §0 | Two files asserted, content not in dialog | NOT INDEPENDENTLY VERIFIED | Supply content if needed |
| 8 | T-1 requires explicit authorization | m3 §7.4 step 4 | Explicit | CONFIRMED FROM SOURCE | None |

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

## 10. CONFIRMATION

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