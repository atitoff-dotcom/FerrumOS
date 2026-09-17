<#
.SYNOPSIS
    FerrumOS Fast Installer for Windows (PowerShell)
.DESCRIPTION
    Installs the FerrumOS CLI & Studio launcher into the user profile,
    configures environment variables, and enables instant terminal access.
.EXAMPLE
    irm https://raw.githubusercontent.com/atitoff-dotcom/FerrumOS/main/tools/install.ps1 | iex
.EXAMPLE
    .\install.ps1 -Uninstall
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$Version = "latest",

    [Parameter(Mandatory = $false)]
    [string]$InstallDir = "$env:LOCALAPPDATA\FerrumOS\bin",

    [Parameter(Mandatory = $false)]
    [switch]$Uninstall,

    [Parameter(Mandatory = $false)]
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

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
    Write-Host "   🛡️  FerrumOS — Reactive Embedded OS & Studio Suite for IoT" -ForegroundColor White
    Write-Host "  ================================================================" -ForegroundColor Cyan
    Write-Host ""
}

function Remove-Ferrum {
    param([string]$TargetDir)

    Write-Host "🗑️  Removing FerrumOS from '$TargetDir'..." -ForegroundColor Yellow

    if (Test-Path $TargetDir) {
        Remove-Item -Path $TargetDir -Recurse -Force
        Write-Host "   [OK] Deleted directory: $TargetDir" -ForegroundColor Green
    } else {
        Write-Host "   [INFO] Target directory not found." -ForegroundColor DarkGray
    }

    # Clean User PATH
    $UserPath = [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::User)
    if ($UserPath) {
        $Parts = $UserPath -split ";" | Where-Object { $_ -ne "" -and $_ -ne $TargetDir }
        $NewPath = $Parts -join ";"
        [Environment]::SetEnvironmentVariable("Path", $NewPath, [EnvironmentVariableTarget]::User)
        Write-Host "   [OK] Removed '$TargetDir' from User PATH" -ForegroundColor Green
    }

    Write-Host "`n✅ FerrumOS has been successfully uninstalled.`n" -ForegroundColor Green
}

if ($Uninstall) {
    Remove-Ferrum -TargetDir $InstallDir
    exit 0
}

Write-FerrumBanner

# 1. Architecture Check
$Arch = $env:PROCESSOR_ARCHITECTURE
if ($Arch -ne "AMD64" -and $Arch -ne "ARM64") {
    Write-Error "Unsupported CPU architecture: $Arch. FerrumOS currently supports x86_64 (AMD64) and ARM64 on Windows."
    exit 1
}

$BinaryName = if ($Arch -eq "ARM64") { "ferrum-windows-arm64.exe" } else { "ferrum-windows-x86_64.exe" }
Write-Host "🔍 Detected system: Windows ($Arch)" -ForegroundColor Gray

# 2. Determine Download URL
if ($Version -eq "latest") {
    $DownloadUrl = "https://github.com/$REPO/releases/latest/download/$BinaryName"
} else {
    $DownloadUrl = "https://github.com/$REPO/releases/download/$Version/$BinaryName"
}

Write-Host "📦 Target binary:   $BinaryName" -ForegroundColor Gray
Write-Host "📂 Install folder:  $InstallDir" -ForegroundColor Gray

if ($DryRun) {
    Write-Host "`n[DryRun] Would download '$DownloadUrl' to '$InstallDir\ferrum.exe' and add to PATH.`n" -ForegroundColor Yellow
    exit 0
}

# 3. Create Target Directory
if (-not (Test-Path $InstallDir)) {
    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
}

$TargetExe = Join-Path $InstallDir "ferrum.exe"
$TempExe = Join-Path $InstallDir "ferrum_temp.exe"

# 4. Download Binary
Write-Host "⬇️  Downloading FerrumOS executable..." -ForegroundColor Cyan

try {
    $WebClient = New-Object System.Net.WebClient
    $WebClient.Headers.Add("User-Agent", "FerrumOS-Installer")
    $WebClient.DownloadFile($DownloadUrl, $TempExe)

    # Atomic move
    if (Test-Path $TargetExe) {
        Remove-Item $TargetExe -Force
    }
    Move-Item -Path $TempExe -Destination $TargetExe -Force
    Write-Host "   [OK] Downloaded and installed: $TargetExe" -ForegroundColor Green
} catch {
    if (Test-Path $TempExe) { Remove-Item $TempExe -Force -ErrorAction SilentlyContinue }
    Write-Host "⚠️  Direct download failed: $($_.Exception.Message)" -ForegroundColor Yellow
    Write-Host "   Checking if local built binary exists in dist_release/..." -ForegroundColor Gray
    
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
        Write-Error "Could not retrieve FerrumOS binary from '$DownloadUrl'. Please check your internet connection or release tags."
        exit 1
    }
}

# 5. Configure User PATH
$UserPath = [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::User)
$PathEntries = if ($UserPath) { $UserPath -split ";" | Where-Object { $_ -ne "" } } else { @() }

if ($PathEntries -notcontains $InstallDir) {
    $NewUserPath = ($PathEntries + $InstallDir) -join ";"
    [Environment]::SetEnvironmentVariable("Path", $NewUserPath, [EnvironmentVariableTarget]::User)
    Write-Host "   [OK] Added '$InstallDir' to User PATH" -ForegroundColor Green
} else {
    Write-Host "   [INFO] PATH already includes target directory." -ForegroundColor DarkGray
}

# Update current session PATH so user can type `ferrum` immediately
if ($env:PATH -split ";" -notcontains $InstallDir) {
    $env:PATH = "$InstallDir;$env:PATH"
}

# 6. Completion & Quickstart
Write-Host ""
Write-Host "🎉 Installation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "  To get started, try:" -ForegroundColor White
Write-Host "    ferrum --help        " -ForegroundColor Yellow -NoNewline
Write-Host "- View all CLI commands" -ForegroundColor Gray
Write-Host "    ferrum studio        " -ForegroundColor Yellow -NoNewline
Write-Host "- Launch Web Control Center in your browser" -ForegroundColor Gray
Write-Host "    ferrum scan          " -ForegroundColor Yellow -NoNewline
Write-Host "- Scan local network for active ESP32 nodes" -ForegroundColor Gray
Write-Host ""
