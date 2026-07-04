#Requires -RunAsAdministrator
<#
.SYNOPSIS
    CVE/EoL 突合バッチを Windows タスクスケジューラに登録する。

.DESCRIPTION
    毎日 AM 2:00 に実行するタスクを登録する。
    初回実行前に以下の環境変数を設定してください:
      $env:ZABBIX_URL      = "https://your-zabbix/zabbix/api_jsonrpc.php"
      $env:ZABBIX_USER     = "api_user"
      $env:ZABBIX_PASSWORD = "password"
      $env:NVD_API_KEY     = "your-nvd-api-key"  # 任意

.EXAMPLE
    .\setup_scheduler.ps1
    .\setup_scheduler.ps1 -Hour 3 -Minute 30   # AM 3:30 に変更
    .\setup_scheduler.ps1 -Unregister           # タスク削除
#>

param(
    [int]    $Hour       = 2,
    [int]    $Minute     = 0,
    [switch] $Unregister
)

$TaskName   = "ZabbixSecurityBatch"
$TaskPath   = "\AtLib\"
$BatchDir   = $PSScriptRoot
$PythonExe  = (Get-Command python -ErrorAction SilentlyContinue).Source
$ScriptPath = Join-Path $BatchDir "main.py"
$LogDir     = Join-Path $BatchDir "logs"
$LogPath    = Join-Path $LogDir   "batch.log"

# ---- タスク削除 ----
if ($Unregister) {
    Unregister-ScheduledTask -TaskName $TaskName -TaskPath $TaskPath -Confirm:$false -ErrorAction SilentlyContinue
    Write-Host "タスク '$TaskPath$TaskName' を削除しました。"
    exit 0
}

# ---- 事前確認 ----
if (-not $PythonExe) {
    Write-Error "Python が見つかりません。PATH に Python を追加してください。"
    exit 1
}
if (-not (Test-Path $ScriptPath)) {
    Write-Error "main.py が見つかりません: $ScriptPath"
    exit 1
}
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir | Out-Null
}

Write-Host "Python: $PythonExe"
Write-Host "スクリプト: $ScriptPath"
Write-Host "ログ: $LogPath"
Write-Host "実行時刻: 毎日 $($Hour):$($Minute.ToString('D2'))"
Write-Host ""

# ---- 環境変数チェック ----
$missingVars = @()
foreach ($var in @("ZABBIX_URL", "ZABBIX_USER", "ZABBIX_PASSWORD")) {
    if (-not [System.Environment]::GetEnvironmentVariable($var, "Machine")) {
        $missingVars += $var
    }
}
if ($missingVars.Count -gt 0) {
    Write-Warning "以下のシステム環境変数が未設定です（タスク実行前に設定してください）:"
    $missingVars | ForEach-Object { Write-Warning "  $_" }
    Write-Warning "設定例: [System.Environment]::SetEnvironmentVariable('ZABBIX_URL', 'https://...', 'Machine')"
    Write-Host ""
}

# ---- タスク定義 ----
# ラッパースクリプト: ログに日時ヘッダーを追記してからバッチ実行
$wrapperScript = Join-Path $BatchDir "run_batch.ps1"
@"
`$LogPath = "$LogPath"
`$BatchDir = "$BatchDir"
`$PythonExe = "$PythonExe"
Add-Content -Path `$LogPath -Value "`n=== `$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ===" -Encoding UTF8
Set-Location `$BatchDir
& `$PythonExe main.py 2>&1 | Tee-Object -FilePath `$LogPath -Append
"@ | Out-File -FilePath $wrapperScript -Encoding utf8

$action  = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NonInteractive -ExecutionPolicy Bypass -File `"$wrapperScript`"" `
    -WorkingDirectory $BatchDir

$trigger = New-ScheduledTaskTrigger -Daily -At "$($Hour):$($Minute.ToString('D2'))"

$settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Hours 2) `
    -MultipleInstances IgnoreNew

$principal = New-ScheduledTaskPrincipal `
    -UserId "SYSTEM" `
    -LogonType ServiceAccount `
    -RunLevel Highest

# ---- 登録 ----
$existing = Get-ScheduledTask -TaskName $TaskName -TaskPath $TaskPath -ErrorAction SilentlyContinue
if ($existing) {
    Set-ScheduledTask -TaskName $TaskName -TaskPath $TaskPath `
        -Action $action -Trigger $trigger -Settings $settings -Principal $principal | Out-Null
    Write-Host "タスクを更新しました: $TaskPath$TaskName"
} else {
    Register-ScheduledTask -TaskName $TaskName -TaskPath $TaskPath `
        -Action $action -Trigger $trigger -Settings $settings -Principal $principal | Out-Null
    Write-Host "タスクを登録しました: $TaskPath$TaskName"
}

Write-Host ""
Write-Host "手動テスト実行:"
Write-Host "  Start-ScheduledTask -TaskName '$TaskName' -TaskPath '$TaskPath'"
Write-Host "ログ確認:"
Write-Host "  Get-Content '$LogPath' -Tail 50"
