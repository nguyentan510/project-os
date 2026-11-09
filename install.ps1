# Cài skill project-os trên Windows (PowerShell thuần, không cần bash).
#   irm https://raw.githubusercontent.com/nguyentan510/project-os/main/install.ps1 | iex
#   .\install.ps1 [-All] [-DryRun] [-Uninstall] [-Dir <thư-mục-clone>]
param(
  [switch]$All, [switch]$DryRun, [switch]$Uninstall,
  [string]$Dir = $(if ($env:PROJECT_OS_DIR) { $env:PROJECT_OS_DIR } else { Join-Path $HOME 'project-os' })
)
$ErrorActionPreference = 'Stop'
$RepoUrl = if ($env:PROJECT_OS_REPO) { $env:PROJECT_OS_REPO } else { 'https://github.com/nguyentan510/project-os.git' }
$SrcRel  = '.agents\skills\project-os'

function Say($m) { Write-Host "  $m" }
function Have($c) { [bool](Get-Command $c -ErrorAction SilentlyContinue) }

Write-Host 'Project OS · cài skill (windows)'

# 1. Nguồn: chạy từ bản clone thì dùng luôn, không thì clone/cập nhật.
$self = if ($PSScriptRoot) { $PSScriptRoot } else { $null }
if ($self -and (Test-Path (Join-Path $self $SrcRel))) {
  $Root = $self; Say "dùng bản clone sẵn có: $Root"
} elseif ($Uninstall) {
  $Root = $Dir
} else {
  if (-not (Have git)) { throw 'Cần git.' }
  if (Test-Path (Join-Path $Dir '.git')) {
    Say "cập nhật $Dir"; if (-not $DryRun) { git -C $Dir pull --ff-only --quiet }
  } elseif (Test-Path $Dir) {
    throw "$Dir đã tồn tại nhưng không phải bản clone. Dùng -Dir để chọn chỗ khác."
  } else {
    Say "clone $RepoUrl → $Dir"; if (-not $DryRun) { git clone --quiet $RepoUrl $Dir }
  }
  $Root = $Dir
}
$Src = Join-Path $Root $SrcRel
if (-not $DryRun -and -not $Uninstall -and -not (Test-Path $Src)) { throw "Không thấy $Src" }

# 2. Phát hiện công cụ.
$targets = @(, @('Chung (Codex, Antigravity…)', (Join-Path $HOME '.agents\skills')))
if ($All -or (Test-Path (Join-Path $HOME '.claude')) -or (Have claude)) { $targets += , @('Claude Code', (Join-Path $HOME '.claude\skills')) }
if ($All -or (Test-Path (Join-Path $HOME '.gemini')) -or (Have gemini) -or (Have antigravity)) { $targets += , @('Antigravity', (Join-Path $HOME '.gemini\config\skills')) }
if ($All -or (Test-Path (Join-Path $HOME '.codex')) -or (Have codex)) { $targets += , @('Codex', (Join-Path $HOME '.codex\skills')) }

function Is-Ours($p) {
  $i = Get-Item $p -Force -ErrorAction SilentlyContinue
  if (-not $i) { return $false }
  if ($i.LinkType -and ($i.Target -contains $Src)) { return $true }
  return (Test-Path (Join-Path $p '.project-os-install'))
}

# 3. Cài hoặc gỡ (junction không cần quyền admin; lỗi thì chép thư mục).
foreach ($t in $targets) {
  $name, $dir = $t; $dst = Join-Path $dir 'project-os'
  Write-Host "• $name → $dst"
  $exists = Test-Path $dst
  if ($Uninstall) {
    if ($exists -and (Is-Ours $dst)) {
      if (-not $DryRun) { (Get-Item $dst -Force).Delete() 2>$null; if (Test-Path $dst) { Remove-Item $dst -Recurse -Force } }
      Say 'đã gỡ'
    } else { Say 'bỏ qua (không có, hoặc không phải do script này tạo)' }
    continue
  }
  if ($exists) {
    if (Is-Ours $dst) {
      if (Test-Path (Join-Path $dst '.project-os-install')) {
        if (-not $DryRun) { Remove-Item $dst -Recurse -Force; Copy-Item $Src $dst -Recurse; New-Item (Join-Path $dst '.project-os-install') -ItemType File | Out-Null }
        Say 'đã làm mới bản chép'
      } else { Say 'đã cài, giữ nguyên' }
    } else { Say 'BỎ QUA: đã có thứ khác ở đó, không ghi đè. Xoá hoặc đổi tên nó rồi chạy lại.' }
    continue
  }
  if ($DryRun) { Say "[dry-run] tạo junction $dst → $Src"; continue }
  New-Item -ItemType Directory -Force $dir | Out-Null
  try { New-Item -ItemType Junction -Path $dst -Target $Src | Out-Null; Say 'đã cài (junction)' }
  catch { Copy-Item $Src $dst -Recurse; New-Item (Join-Path $dst '.project-os-install') -ItemType File | Out-Null; Say 'đã cài (bản chép, chạy lại để cập nhật)' }
}

Write-Host ''
if ($Uninstall) { Write-Host "Xong gỡ. Thư mục clone ($Root) giữ nguyên."; return }
Write-Host 'Xong. Khởi động lại công cụ AI nếu nó không thấy skill.'
Write-Host 'Gọi: Claude Code /project-os · Codex $project-os · Antigravity tự nhận.'
