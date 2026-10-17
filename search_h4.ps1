# search_h4.ps1 -- READ-ONLY search of the project for H4-related code and specs.
# Does NOT run Python, does NOT touch market data, does NOT modify files.

$Root = "C:\Users\user\Desktop\MOEX_TRADING_LAB_V2"
$Out  = Join-Path $Root "search_results.txt"

# Patterns to search for (case-insensitive, literal, not regex)
$Patterns = @(
    "H4",
    "eligibility",
    "eligible",
    "build_forward_labels",
    "range_atr",
    "session_key",
    "v3.4",
    "v3.6.2",
    "assign_period",
    "calculate_indicators",
    "0.54835695",
    "T-1"
)

# File extensions to include
$Exts = @("*.py", "*.md", "*.txt", "*.json", "*.yaml", "*.yml")

# Directories to exclude (regex on the full path)
$ExcludeDirs = @(
    "\\\.git\\",
    "\\__pycache__\\",
    "\\\.venv\\",
    "\\venv\\",
    "\\env\\",
    "\\cache\\",
    "\\cache_2024_2025\\",
    "\\cache_other_tickers\\"
)

# File-name patterns to exclude (market data, big CSVs, OOS artefacts)
$ExcludeFileRegex = "(?i)(OOS|\.csv$|\.parquet$|\.feather$|\.h5$|\.hdf5$)"

$lines = New-Object System.Collections.Generic.List[string]
$lines.Add("H4 PROJECT-WIDE DISCOVERY -- READ-ONLY SEARCH")
$lines.Add("Generated: " + (Get-Date).ToString("o"))
$lines.Add("Root: $Root")
$lines.Add("Patterns: " + ($Patterns -join ", "))
$lines.Add("Excluded dirs: " + ($ExcludeDirs -join " | "))
$lines.Add("Excluded files: " + $ExcludeFileRegex)
$lines.Add("")

$files = Get-ChildItem -Path $Root -Recurse -File -Include $Exts -ErrorAction SilentlyContinue | Where-Object {
    $p = $_.FullName
    $skip = $false
    foreach ($d in $ExcludeDirs) { if ($p -match $d) { $skip = $true; break } }
    if (-not $skip -and ($p -match $ExcludeFileRegex)) { $skip = $true }
    -not $skip
}

$lines.Add("Files scanned: " + $files.Count)
$lines.Add("")

$total = 0
foreach ($f in $files) {
    $rel = $f.FullName.Substring($Root.Length).TrimStart('\')
    $content = Get-Content -LiteralPath $f.FullName -ErrorAction SilentlyContinue
    if ($null -eq $content) { continue }

    $hits = New-Object System.Collections.Generic.List[string]
    for ($i = 0; $i -lt $content.Count; $i++) {
        $line = $content[$i]
        foreach ($pat in $Patterns) {
            if ($line -match [regex]::Escape($pat)) {
                $hits.Add(("L{0}: {1}" -f ($i + 1), $line))
                break
            }
        }
    }

    if ($hits.Count -gt 0) {
        $total += $hits.Count
        $lines.Add("=" * 78)
        $lines.Add("FILE: $rel")
        $lines.Add("SIZE: " + $f.Length + "   MTIME: " + $f.LastWriteTime.ToString("o"))
        $lines.Add("HITS: " + $hits.Count)
        foreach ($h in $hits) { $lines.Add($h) }
        $lines.Add("")
    }
}

$lines.Add("=" * 78)
$lines.Add("TOTAL HITS: $total")
$lines.Add("STRATEGY LOGIC: UNCHANGED. RESEARCH ONLY.")
$lines.Add("NO THRESHOLD IS OPTIMIZED. NO FILTER IS INSTALLED. NO LIVE ORDERS.")
$lines.Add("OOS: SEALED. H4 EXECUTION: NOT AUTHORIZED.")

$lines | Out-File -FilePath $Out -Encoding utf8
Write-Host "WROTE: $Out"
Write-Host ("BYTES: " + (Get-Item $Out).Length)
Write-Host ("LINES: " + $lines.Count)
