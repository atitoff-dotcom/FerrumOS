# ==============================================================================
#  FerrumOS Fast Installer for Windows (PowerShell)
# ==============================================================================
# Usage:
#   irm https://raw.githubusercontent.com/atitoff-dotcom/FerrumOS/main/install.ps1 | iex
#   .\install.ps1 -Uninstall
# ==============================================================================

$ErrorActionPreference = "Stop"

# Default configuration
$Version = if ($env:FERRUM_VERSION) { $env:FERRUM_VERSION } else { "latest" }
$InstallDir = if ($env:FERRUM_INSTALL_DIR) { $env:FERRUM_INSTALL_DIR } else { "$env:LOCALAPPDATA\FerrumOS\bin" }
$Uninstall = $false
$DryRun = $false

# Parse args if passed directly
for ($i = 0; $i -lt $args.Count; $i++) {
    $arg = $args[$i]
    if ($arg -eq "-Uninstall" -or $arg -eq "--uninstall") {
        $Uninstall = $true
    } elseif ($arg -eq "-DryRun" -or $arg -eq "--dry-run") {
        $DryRun = $true
    } elseif ($arg -eq "-Version" -or $arg -eq "--version") {
        $Version = $args[++$i]
    } elseif ($arg -eq "-InstallDir" -or $arg -eq "--dir") {
        $InstallDir = $args[++$i]
    }
}

# Ensure modern TLS
try {
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 -bor [Net.SecurityProtocolType]::Tls13
} catch {
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
}

$REPO = "atitoff-dotcom/FerrumOS"

function Write-FerrumBanner {
    Write-Host ""
    Write-Host "  ================================================================" -ForegroundColor Cyan
    Write-Host "   [+] FerrumOS -- Reactive Embedded OS and Studio Suite for IoT" -ForegroundColor White
    Write-Host "  ================================================================" -ForegroundColor Cyan
    Write-Host ""
}

function Remove-Ferrum {
    param([string]$TargetDir)

    Write-Host "[-] Removing FerrumOS from '$TargetDir'..." -ForegroundColor Yellow

    if (Test-Path $TargetDir) {
        Remove-Item -Path $TargetDir -Recurse -Force
        Write-Host "   [OK] Deleted directory: $TargetDir" -ForegroundColor Green
    } else {
        Write-Host "   [INFO] Target directory not found." -ForegroundColor DarkGray
    }

    # Clean User PATH (Windows only)
    if (-not $IsLinux -and -not $IsMacOS) {
        $UserPath = [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::User)
        if ($UserPath) {
            $Parts = $UserPath -split ";" | Where-Object { $_ -ne "" -and $_ -ne $TargetDir }
            $NewPath = $Parts -join ";"
            [Environment]::SetEnvironmentVariable("Path", $NewPath, [EnvironmentVariableTarget]::User)
            Write-Host "   [OK] Removed '$TargetDir' from User PATH" -ForegroundColor Green
        }
    }

    Write-Host "`n[OK] FerrumOS has been successfully uninstalled.`n" -ForegroundColor Green
}

if ($Uninstall) {
    Remove-Ferrum -TargetDir $InstallDir
    return
}

Write-FerrumBanner

# 1. Architecture Check
$Arch = $env:PROCESSOR_ARCHITECTURE
if (-not $Arch) {
    if ([System.Environment]::Is64BitOperatingSystem) { $Arch = "AMD64" } else { $Arch = "x86" }
}
if ($Arch -ne "AMD64" -and $Arch -ne "ARM64") {
    Write-Error "Unsupported CPU architecture: $Arch. FerrumOS currently supports x86_64 (AMD64) and ARM64."
    return
}

$BinaryName = if ($Arch -eq "ARM64") { "ferrum-windows-arm64.exe" } else { "ferrum-windows-x86_64.exe" }
$OSName = if ($IsLinux) { "Linux" } elseif ($IsMacOS) { "macOS" } else { "Windows" }
Write-Host "Detected system: $OSName ($Arch)" -ForegroundColor Gray
if ($IsLinux -or $IsMacOS) {
    Write-Host "   [NOTE] For Linux/macOS, the native bash installer is recommended:" -ForegroundColor Yellow
    Write-Host "          curl -fsSL https://raw.githubusercontent.com/$REPO/main/tools/install.sh | bash" -ForegroundColor Yellow
}

# 2. Determine Download URLs (Releases primary, Raw Git fallback)
$UrlCandidates = @()
if ($Version -eq "latest") {
    $UrlCandidates += "https://github.com/$REPO/releases/latest/download/$BinaryName"
    $UrlCandidates += "https://raw.githubusercontent.com/$REPO/main/releases/v0.6.0/$BinaryName"
} else {
    $UrlCandidates += "https://github.com/$REPO/releases/download/$Version/$BinaryName"
    $UrlCandidates += "https://raw.githubusercontent.com/$REPO/main/releases/$Version/$BinaryName"
}

Write-Host "Target binary:   $BinaryName" -ForegroundColor Gray
Write-Host "Install folder:  $InstallDir" -ForegroundColor Gray

if ($DryRun) {
    Write-Host "`n[DryRun] Would download '$BinaryName' to '$InstallDir\ferrum.exe' and add to PATH.`n" -ForegroundColor Yellow
    return
}

# 3. Create Target Directory
if (-not (Test-Path $InstallDir)) {
    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
}

$TargetExe = Join-Path $InstallDir "ferrum.exe"
$TempExe = Join-Path $InstallDir "ferrum_temp.exe"

# 4. Download Binary
Write-Host "Downloading FerrumOS executable..." -ForegroundColor Cyan

$DownloadSuccess = $false
foreach ($Url in $UrlCandidates) {
    try {
        if (Test-Path $TempExe) { Remove-Item $TempExe -Force -ErrorAction SilentlyContinue }
        Invoke-WebRequest -Uri $Url -OutFile $TempExe -UseBasicParsing -Headers @{"User-Agent" = "FerrumOS-Installer"}
        if ((Test-Path $TempExe) -and (Get-Item $TempExe).Length -gt 100000) {
            $DownloadSuccess = $true
            break
        }
    } catch {
        # Try next candidate
    }
}

if ($DownloadSuccess) {
    if (Test-Path $TargetExe) {
        Remove-Item $TargetExe -Force
    }
    Move-Item -Path $TempExe -Destination $TargetExe -Force
    Write-Host "   [OK] Downloaded and installed: $TargetExe" -ForegroundColor Green
} else {
    if (Test-Path $TempExe) { Remove-Item $TempExe -Force -ErrorAction SilentlyContinue }
    Write-Host "Checking if local built binary exists in dist_release/..." -ForegroundColor Gray
    
    # Fallback for local build/testing environment
    $LocalCandidates = @(
        "$PSScriptRoot\..\dist_release\ferrum-windows-x86_64.exe",
        "$PSScriptRoot\..\dist_release\ferrum.exe",
        "$PSScriptRoot\..\dist_release\FerrumOS-Studio.exe"
    )
    $FoundLocal = $false
    foreach ($Candidate in $LocalCandidates) {
        if (Test-Path $Candidate) {
            Copy-Item -Path $Candidate -Destination $TargetExe -Force
            Write-Host "   [OK] Installed from local build: $Candidate" -ForegroundColor Green
            $FoundLocal = $true
            break
        }
    }
    if (-not $FoundLocal) {
        Write-Error "Could not retrieve FerrumOS binary from any distribution source. Please check your internet connection."
        return
    }
}

# 5. Configure User PATH (Windows only)
if (-not $IsLinux -and -not $IsMacOS) {
    $UserPath = [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::User)
    $PathEntries = if ($UserPath) { $UserPath -split ";" | Where-Object { $_ -ne "" } } else { @() }

    if ($PathEntries -notcontains $InstallDir) {
        $NewUserPath = ($PathEntries + $InstallDir) -join ";"
        [Environment]::SetEnvironmentVariable("Path", $NewUserPath, [EnvironmentVariableTarget]::User)
        Write-Host "   [OK] Added '$InstallDir' to User PATH" -ForegroundColor Green
    } else {
        Write-Host "   [INFO] PATH already includes target directory." -ForegroundColor DarkGray
    }
}

# Update current session PATH so user can type `ferrum` immediately
if ($env:PATH -split ";" -notcontains $InstallDir) {
    $env:PATH = "$InstallDir;$env:PATH"
}

# 6. Completion and Quickstart
Write-Host ""
Write-Host "Installation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "  To get started, try:" -ForegroundColor White
Write-Host "    ferrum --help        " -ForegroundColor Yellow -NoNewline
Write-Host "- View all CLI commands" -ForegroundColor Gray
Write-Host "    ferrum studio        " -ForegroundColor Yellow -NoNewline
Write-Host "- Launch Web Control Center in your browser" -ForegroundColor Gray
Write-Host "    ferrum scan          " -ForegroundColor Yellow -NoNewline
Write-Host "- Scan local network for active ESP32 nodes" -ForegroundColor Gray
Write-Host ""
