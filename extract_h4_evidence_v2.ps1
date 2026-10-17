# extract_h4_evidence_v2.ps1
# READ-ONLY. Извлекает фрагменты исходников и спецификаций H4 в один файл.
# Ничего не меняет. Не запускает Python. Не открывает OOS. Не читает cache*.

$ErrorActionPreference = "Continue"
$Out = Join-Path (Get-Location) "evidence_v2.txt"
if (Test-Path $Out) { Remove-Item $Out -Force }
$enc = New-Object System.Text.UTF8Encoding($false)

function Write-Line {
    param([string]$Text)
    Add-Content -LiteralPath $Out -Value $Text -Encoding UTF8
}

function Write-Section {
    param([string]$Title)
    Write-Line ""
    Write-Line ("=" * 78)
    Write-Line $Title
    Write-Line ("=" * 78)
}

function Write-Range {
    param([string]$Path, [int]$Start, [int]$Count)
    if (-not (Test-Path $Path)) {
        Write-Line ("MISSING FILE: " + $Path)
        return
    }
    $lines = Get-Content -LiteralPath $Path
    $end = [Math]::Min($Start + $Count - 1, $lines.Count)
    for ($i = $Start; $i -le $end; $i++) {
        $n = $i + 1
        Write-Line ("{0,5}: {1}" -f $n, $lines[$i])
    }
}

function Write-Grep {
    param([string]$Path, [string[]]$Patterns, [int]$Context = 0)
    if (-not (Test-Path $Path)) {
        Write-Line ("MISSING FILE: " + $Path)
        return
    }
    $hits = Select-String -LiteralPath $Path -Pattern $Patterns -Context $Context, $Context -ErrorAction SilentlyContinue
    if (-not $hits) {
        Write-Line "NO MATCHES"
        return
    }
    foreach ($h in $hits) {
        if ($h.Context.PreContext) {
            $ln = $h.LineNumber - $h.Context.PreContext.Count
            foreach ($c in $h.Context.PreContext) {
                Write-Line ("{0,5}: {1}" -f $ln, $c); $ln++
            }
        }
        Write-Line ("{0,5}: {1}" -f $h.LineNumber, $h.Line)
        if ($h.Context.PostContext) {
            $ln = $h.LineNumber + 1
            foreach ($c in $h.Context.PostContext) {
                Write-Line ("{0,5}: {1}" -f $ln, $c); $ln++
            }
        }
        Write-Line ""
    }
}

# ============================================================
# HEADER
# ============================================================
Write-Line "H4 SOURCE EVIDENCE COMPLETION v2 -- READ ONLY"
Write-Line ("Generated: " + (Get-Date).ToString("o"))
Write-Line ("CWD: " + (Get-Location).Path)
Write-Line "STRATEGY LOGIC: UNCHANGED. RESEARCH ONLY."
Write-Line "NO THRESHOLD IS OPTIMIZED. NO FILTER IS INSTALLED. NO LIVE ORDERS."
Write-Line "OOS: SEALED. H4 EXECUTION: NOT AUTHORIZED."

# ============================================================
# BLOCK 1: build_forward_labels
# ============================================================
Write-Section "BLOCK 1: v600_hypothesis_lab.py :: build_forward_labels (L340..L450)"
Write-Range ".\v600_hypothesis_lab.py" 340 120

Write-Section "BLOCK 1b: HORIZONS / REACH_LEVELS / PERIODS / max_available"
Write-Grep ".\v600_hypothesis_lab.py" @('^HORIZONS','^REACH_LEVELS','^PERIODS','^DISCOVERY','^VALIDATION','^OOS','max_available','any_partial') 0

# ============================================================
# BLOCK 2: assign_period
# ============================================================
Write-Section "BLOCK 2: v600_hypothesis_lab.py :: assign_period (L130..L180)"
Write-Range ".\v600_hypothesis_lab.py" 130 50

Write-Section "BLOCK 2b: assign_period call sites"
Write-Grep ".\v600_hypothesis_lab.py" @('assign_period\(') 0

# ============================================================
# BLOCK 3: calculate_indicators
# ============================================================
Write-Section "BLOCK 3: main :: calculate_indicators (L481..L740)"
Write-Range ".\main_v5.17_threshold_path_lab_v2.py" 481 260

# ============================================================
# BLOCK 4: EXCLUDE_WEEKEND_SESSIONS / filter_weekend_sessions
# ============================================================
Write-Section "BLOCK 4: EXCLUDE_WEEKEND_SESSIONS / filter_weekend_sessions / session_key defs and calls"
Write-Grep ".\main_v5.17_threshold_path_lab_v2.py" @('EXCLUDE_WEEKEND_SESSIONS','filter_weekend_sessions','def trading_session_key','def build_session_keys','def calculate_indicators') 0

Write-Section "BLOCK 4b: filter_weekend_sessions body (L276..L300)"
Write-Range ".\main_v5.17_threshold_path_lab_v2.py" 276 25

Write-Section "BLOCK 4c: trading_session_key + build_session_keys body (L4447..L4480)"
Write-Range ".\main_v5.17_threshold_path_lab_v2.py" 4447 35

# ============================================================
# BLOCK 5: spec v3.4 full text
# ============================================================
Write-Section "BLOCK 5a: FULL audit_research_roadmap_v1_h4_spec_v3_4_PROPOSED.md"
if (Test-Path ".\audit_research_roadmap_v1_h4_spec_v3_4_PROPOSED.md") {
    $lines = Get-Content ".\audit_research_roadmap_v1_h4_spec_v3_4_PROPOSED.md"
    for ($i = 0; $i -lt $lines.Count; $i++) {
        Write-Line ("{0,5}: {1}" -f ($i+1), $lines[$i])
    }
} else {
    Write-Line "MISSING FILE"
}

# ============================================================
# BLOCK 5b: spec v3.6.2 full text
# ============================================================
Write-Section "BLOCK 5b: FULL audit_research_roadmap_v1_h4_spec_v3_6_2_PROPOSED.md"
if (Test-Path ".\audit_research_roadmap_v1_h4_spec_v3_6_2_PROPOSED.md") {
    $lines = Get-Content ".\audit_research_roadmap_v1_h4_spec_v3_6_2_PROPOSED.md"
    for ($i = 0; $i -lt $lines.Count; $i++) {
        Write-Line ("{0,5}: {1}" -f ($i+1), $lines[$i])
    }
} else {
    Write-Line "MISSING FILE"
}

# ============================================================
# BLOCK 6: audit M3 functions
# ============================================================
Write-Section "BLOCK 6a: audit_h4_implementation_v1.py :: audit_bounds (L127..L172)"
Write-Range ".\audit_h4_implementation_v1.py" 127 46

Write-Section "BLOCK 6b: audit_h4_forensic_followup_v2_fast.py :: formal_classification (L147..L190)"
Write-Range ".\audit_h4_forensic_followup_v2_fast.py" 147 44

Write-Section "BLOCK 6c: audit_h4_forensic_followup_v2_fast.py :: v600_partial_flags_reconstructed (L98..L150)"
Write-Range ".\audit_h4_forensic_followup_v2_fast.py" 98 53

Write-Section "BLOCK 6d: audit_h4_forensic_followup_v1.py :: formal_classification (L108..L150)"
Write-Range ".\audit_h4_forensic_followup_v1.py" 108 43

# ============================================================
# BLOCK 7: real call sites
# ============================================================
Write-Section "BLOCK 7: REAL CALL SITES in *.py (not definitions)"
$patterns = @(
    '[^a-zA-Z_]build_forward_labels\(',
    '[^a-zA-Z_]assign_period\(',
    '[^a-zA-Z_]calculate_indicators\(',
    '[^a-zA-Z_]filter_weekend_sessions\(',
    '[^a-zA-Z_]trading_session_key\(',
    '[^a-zA-Z_]build_session_keys\('
)
$files = Get-ChildItem -Path . -Filter *.py -File -Recurse -ErrorAction SilentlyContinue | Where-Object { $_.FullName -notmatch '\\cache' }
foreach ($f in $files) {
    $hits = Select-String -LiteralPath $f.FullName -Pattern $patterns -ErrorAction SilentlyContinue
    foreach ($h in $hits) {
        $trim = $h.Line.Trim()
        if ($trim -match '^\s*def\s+') { continue }
        Write-Line ($f.Name + "  L" + $h.LineNumber + ": " + $trim)
    }
}

# ============================================================
# BLOCK 8: function definitions without H4 keywords
# ============================================================
Write-Section "BLOCK 8: def sites related to forward/session/mask/range/atr/period/window"
$defPattern = '^\s*def\s+\w+'
$keyword = 'forward|eligible|eligib|session|mask|range|atr|period|horizon|window'
foreach ($f in $files) {
    $hits = Select-String -LiteralPath $f.FullName -Pattern $defPattern -ErrorAction SilentlyContinue
    foreach ($h in $hits) {
        if ($h.Line -match $keyword) {
            Write-Line ($f.Name + "  L" + $h.LineNumber + ": " + $h.Line.Trim())
        }
    }
}

# ============================================================
# BLOCK 9: H4 spec inventory (fix 13 vs 15)
# ============================================================
Write-Section "BLOCK 9: H4 spec files inventory"
$specs = Get-ChildItem -Path . -Filter "audit_research_roadmap_v1_h4_spec_*.md" -File | Sort-Object Name
foreach ($s in $specs) {
    Write-Line ("{0}  {1} bytes  {2}" -f $s.Name, $s.Length, $s.LastWriteTime.ToString("o"))
}
Write-Line "----- COUNT -----"
Write-Line ([string]$specs.Count)

# ============================================================
# FOOTER
# ============================================================
Write-Section "FOOTER"
Write-Line ("BYTES: " + (Get-Item $Out).Length)
Write-Line ("LINES: " + ((Get-Content $Out).Count))
Write-Line "STRATEGY LOGIC: UNCHANGED. RESEARCH ONLY."
Write-Line "NO THRESHOLD IS OPTIMIZED. NO FILTER IS INSTALLED. NO LIVE ORDERS."
Write-Line "OOS: SEALED. H4 EXECUTION: NOT AUTHORIZED."

Write-Host ("WROTE: " + $Out)
Write-Host ("BYTES: " + (Get-Item $Out).Length)
