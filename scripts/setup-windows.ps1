# Unumdorlik — Windows bir martalik sozlash (Antigravity /start workflow shu skriptni chaqiradi)
# Ishga tushirish: PowerShell'da loyiha papkasida:  powershell -ExecutionPolicy Bypass -File scripts\setup-windows.ps1
$ErrorActionPreference = "Continue"
function Step($t) { Write-Host "`n=== $t ===" -ForegroundColor Cyan }
function Has($cmd) { return [bool](Get-Command $cmd -ErrorAction SilentlyContinue) }

Step "1/6 uv (Python paket menejeri)"
if (-not (Has "uv")) { winget install --id astral-sh.uv -e --accept-source-agreements --accept-package-agreements }
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

Step "2/6 ffmpeg"
if (-not (Has "ffmpeg")) { winget install --id Gyan.FFmpeg -e --accept-source-agreements --accept-package-agreements }
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

Step "3/6 Claude Code CLI"
if (-not (Has "claude")) {
  if (-not (Has "npm")) { winget install --id OpenJS.NodeJS.LTS -e --accept-source-agreements --accept-package-agreements }
  $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
  npm install -g --allow-scripts=@anthropic-ai/claude-code @anthropic-ai/claude-code
}

Step "4/6 Python muhiti"
uv sync --extra llm --extra audio --extra pdf --extra images

Step "5/6 Konfiguratsiya fayllari"
if (-not (Test-Path "config\pipeline.yaml")) { Copy-Item "config\profiles\stack-b.yaml" "config\pipeline.yaml"; Write-Host "config\pipeline.yaml yaratildi (stack-b)" }
if (-not (Test-Path ".env")) { Copy-Item ".env.example" ".env"; Write-Host ".env yaratildi — GEMINI_API_KEY ni to'ldiring" -ForegroundColor Yellow }
New-Item -ItemType Directory -Force -Path "assets\characters","secrets","topics\inbox","episodes" | Out-Null

Step "6/6 Tekshiruv"
uv run unumdorlik doctor
Write-Host "`nKeyingi: (1) .env ga GEMINI_API_KEY yozing; (2) 'claude' deb kirib /login qiling; (3) Antigravity'da /start" -ForegroundColor Green
