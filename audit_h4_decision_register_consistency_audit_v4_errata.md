# audit_h4_decision_register_consistency_audit_v4_errata.md

H4 CONSISTENCY AUDIT v4 — TARGETED ERRATA
Read-only documentary review only.

No data processing. No bootstrap. No CI. No T-1 execution.
No H4 execution. No OOS opening or analysis. No live orders.
No spec, code, data or existing report modification. No overwriting.

STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY
NO THRESHOLD IS OPTIMIZED
NO FILTER IS INSTALLED
NO LIVE ORDERS
OOS: SEALED. H4 EXECUTION: NOT AUTHORIZED.

---

## 1. CORRECTION TO THE PC3 DEPENDENCY GRAPH

### 1.1. Exact primary-register rows (verbatim, h4_sources_v4.txt)

From `audit_h4_consolidated_open_decisions_register_v1.md` §1
(Register table):

**Row M2-STAT-UNDEF:**
> "| M2-STAT-UNDEF | Methodology decision | UNRESOLVED | v3.4 §5.8
> (only N_event>0 and N_control=0 covered); v3.4 §7.1 step 4 | The
> only explicit non-estimability rule is the empty-control-group
> rule. | What happens when a dataset-level statistic is undefined
> for a reason other than N_event>0 and N_control=0 (for example
> empty E_h^d). | Define fallback as UNRESOLVED replicate; skip
> replicate; define additional non-estimability rules. | Explicit
> user authorization required | M2-CALENDAR, M2-DUPLICATES, PC3 |
> must remain sealed | User to state whether to broaden §5.8 or
> leave other undefined-statistic cases as UNRESOLVED. |"

**Row PC3-TRIGGER:**
> "| PC3-TRIGGER | Methodology decision | PROPOSED — NOT AUTHORIZED
> | v3.4 §7.1 step 5 "N_event>0 and N_control=0 in the resampled
> data" | The trigger is exactly this condition. | Whether this rule
> is authorized; whether it should be broadened. | Authorize as
> proposed; broaden; reject. | Explicit user authorization required
> | none | must remain sealed | User to authorize or reject the
> invalid-replicate rule. |"

**Row PC3-UNDEF:**
> "| PC3-UNDEF | Methodology decision | UNRESOLVED | v3.4 §7.1
> step 5 (narrow trigger); v3.4 §7.1 step 4 (aggregate requires
> defined Δ_h^d) | Only the narrow trigger is stated. | Handling of
> undefined dataset-level statistics outside that trigger, and of
> undefined aggregates. | See M2-STAT-UNDEF. | Explicit user
> authorization required | M2-STAT-UNDEF | must remain sealed |
> User to state the fallback for undefined statistics. |"

### 1.2. Is `PC3` an aggregate, a separate decision, or an alias?

Three rows carry the prefix `PC3`:

- `PC3-TRIGGER`
- `PC3-UNDEF`
- no standalone row named `PC3`

In the row `M2-STAT-UNDEF`, the dependency column reads
"**M2-CALENDAR, M2-DUPLICATES, PC3**".

There is **no** register row that defines a vertex named `PC3`.
The register uses `PC3` in that one dependency cell, but the
register's own rows are named `PC3-TRIGGER` and `PC3-UNDEF`.

**No primary source explicitly equates `PC3` with `PC3-UNDEF`.**
No primary source explicitly equates `PC3` with `PC3-TRIGGER`.
No primary source states that `PC3` is an aggregate of both.

### 1.3. Finding — do not merge vertices

- The v4 graph treated `PC3 → M2-STAT-UNDEF` as an edge.
  That edge is valid only if the vertex named in the register's
  cell (`PC3`) is the same as one of the register's own vertices
  (`PC3-TRIGGER` or `PC3-UNDEF`). **This identity is not
  established.**
- The v4 graph also treated `M2-STAT-UNDEF → PC3-UNDEF` as an
  edge. This is directly supported: the PC3-UNDEF row's
  dependency column names "M2-STAT-UNDEF".
- Therefore the mutual pair `M2-STAT-UNDEF ↔ PC3-UNDEF` is **not**
  supported unless the register's `PC3` is the same vertex as
  `PC3-UNDEF`. No source establishes this.

**Status of the mutual pair: NOT ESTABLISHED.**

**Correct action:** keep the vertices `M2-STAT-UNDEF`,
`PC3-TRIGGER`, `PC3-UNDEF` distinct. The register's cell `PC3`
must be treated as **an unresolved reference** (could be
`PC3-TRIGGER`, `PC3-UNDEF`, both, or a distinct unnamed item) —
not merged.

### 1.4. Recalculated confirmed cycles

The only cycle candidate after this correction is the pair
`M2-RNG ↔ PC4`, which does not involve any `PC3` vertex.

Recheck of `M2-RNG ↔ PC4` edges:

- Register row `M2-RNG`: dependency column reads "**PC4**".
- Register row `PC4`: dependency column reads
  "**M2-CALENDAR, M2-DUPLICATES, M2-QUANTILE, M2-RNG**".

Both edges are directly supported by the register text.
**Status: CONFIRMED CYCLE (length 2).**

### 1.5. Vertex count, edge count, cycles ≥ 3

Vertices (distinct register rows with dependency columns):
M1, M2-CALENDAR, M2-DUPLICATES, M2-STAT-UNDEF, M2-QUANTILE,
M2-RNG, PC1, PC2, PC3-TRIGGER, PC3-UNDEF, PC4, PC5, M3, Q-NEW.

Also referenced but not defined as rows: `PC3` (in
M2-STAT-UNDEF's cell).

Vertex count: **14 defined rows + 1 unresolved reference
(`PC3`) = 15 identifiers total, of which 14 are defined as
vertices.**

Edges with both endpoints defined:

```
M2-CALENDAR   → M2-STAT-UNDEF
M2-DUPLICATES → M2-STAT-UNDEF
M2-STAT-UNDEF → PC3-UNDEF
M1            → M2-QUANTILE
PC4           → M2-RNG
M2-CALENDAR   → PC4
M2-DUPLICATES → PC4
M2-QUANTILE   → PC4
M2-RNG        → PC4
```

Plus one unresolved edge:

```
PC3 → M2-STAT-UNDEF   [endpoint PC3 not defined as a vertex]
```

Confirmed edges among defined vertices: **9.**

Cycles of length ≥ 3 among these 9 edges:

- No closed walk of length ≥ 3 was found by manual traversal.
- **Status: NOT ESTABLISHED as present; not asserted absent beyond
  these 9 edges.**

**Confirmed cycles count after correction: 1** (only
`M2-RNG ↔ PC4`).

**All other reported cycles in v4 are retracted.**

### 1.6. What remains unresolved

- The reference `PC3` in M2-STAT-UNDEF's dependency cell: no
  primary source defines it. **NOT ESTABLISHED.**
- Whether `PC3` = `PC3-TRIGGER` or `PC3` = `PC3-UNDEF` or
  something else: **NOT ESTABLISHED.**

---

## 2. CORRECTION TO THE OOS RELEASE-CONDITION STATEMENT

### 2.1. What v3.4 explicitly says (verbatim, evidence_v2 block 5a)

From `audit_research_roadmap_v1_h4_spec_v3_4_PROPOSED.md` §9:

> "## 9. OOS handling
> OOS remains SEALED until separate authorization, decided before
> viewing OOS results."

### 2.2. What v3.6.2 explicitly says (verbatim, evidence_v2 block 5b)

From `audit_research_roadmap_v1_h4_spec_v3_6_2_PROPOSED.md` §12:

> "## 12. OOS
> OOS remains SEALED."

### 2.3. What `audit_h4_final_predecision_audit_v1.md` §9 says (verbatim, h4_sources_v4)

> "OOS: SEALED."

### 2.4. Normative relationship between v3.4 §9 and v3.6.2 §12

No available source states that v3.6.2 §12 inherits the release
condition from v3.4 §9. No available source states that v3.6.2 §12
supersedes v3.4 §9. No available source states that both texts
apply jointly.

**Status of the normative relationship: NOT ESTABLISHED.**

### 2.5. Corrected statement

- **v3.4 §9 explicitly requires:** SEALED until separate
  authorization, decided before viewing OOS results.
- **v3.6.2 §12 explicitly says:** OOS remains SEALED.
- **The normative relationship between these two statements is
  not established** by any available source.

**Removed from v4:** the assertion that the v3.4 release condition
is "implicitly carried over" into v3.6.2. No source supports that
assertion.

**Unchanged operational status:**

- `OOS: SEALED.`
- No authorization to open or analyze OOS.
- No permission to open OOS is derived by this document.

---

## 3. RECONCILIATION OF D3 AND T-1 PREREQUISITES

### 3.1. What the primary source says about T-1 input and authorization

From `audit_h4_m3_eligibility_comparison_v1.md` §7.4 (verbatim,
h4_sources_v4.txt):

> "1. Resolve R-1 (definition of range_atr) to fix the input for
> eligibility.
> 2. Answer Q1 (session_key definition).
> 3. Choose between v3.4 §5.2 and v3.6.2 §6 as the normative
> eligibility rule, or freeze both and state which one applies
> in H4.
> 4. Authorize T-1 to measure actual differences."

### 3.2. What the source does and does not establish

- **Documentary sequence:** the four items appear as a numbered
  list. A numbered list is a documentary sequence, not necessarily
  a mandatory order of execution.

- **Technical prerequisite:** the source says "Resolve R-1 ... to
  fix the input for eligibility" — this is a **conditional**
  statement ("to fix"), not "required before". It does not
  explicitly state that D3 must be decided before T-1.
  The source also does not state that T-1 may compare both
  eligibility variants before D3 is decided.

- **Authorization requirement:** the source explicitly states
  "Authorize T-1". **CONFIRMED FROM SOURCE.**

### 3.3. Does the source establish that D3 must precede T-1?

**NOT ESTABLISHED.**

The source lists a choice of normative rule and, separately,
authorization of T-1. It does not state an ordering constraint
between them.

### 3.4. Does the source establish that T-1 may compare both variants before D3?

**NOT ESTABLISHED.**

No available source discusses this possibility.

### 3.5. Corrected status of the D3 ↔ T-1 relation

**OPEN / NOT ESTABLISHED.**

- Documentary sequence exists in the source (numbered list).
- Technical prerequisite is not established.
- Authorization requirement for T-1 is explicitly established.

Do not infer that D3 must precede T-1. Do not execute T-1. Do not
silently authorize it.

---

## 4. FINAL STATUS

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

## 5. CONFIRMATION

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