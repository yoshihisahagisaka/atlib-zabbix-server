$ErrorActionPreference = "Stop"

# リポジトリルート（このスクリプトの3階層上: zabbixserver/tools/ops-runbooks/build.ps1 -> repo root）
$toolsDir = $PSScriptRoot
$repo = Resolve-Path "$toolsDir\..\..\.." | Select-Object -ExpandProperty Path

$template = Get-Content -Raw -Encoding UTF8 "$toolsDir\template.html"
$fontB64 = (Get-Content -Raw -Encoding UTF8 "$toolsDir\jbm-latin.b64").Trim()

$docs = @{
  "__DOC_SENSOR_EDGE__" = "$repo\Sensor Edge\運用手順書_顧客追加フロー.md"
  "__DOC_ONBOARDING__"  = "$repo\msp-customer-portal\docs\運用手順書_顧客オンボーディング統合フロー.md"
  "__DOC_DEPLOY__"      = "$repo\zabbixserver\運用手順書_デプロイ.md"
  "__DOC_PW_ADMIN__"    = "$repo\msp-frontend-server\運用手順書_Zabbix管理者パスワードローテーション.md"
  "__DOC_PW_DB__"       = "$repo\msp-frontend-server\運用手順書_zabbix-server_DBパスワードローテーション.md"
  "__DOC_PSK_PROXY__"   = "$repo\msp-frontend-server\運用手順書_ZabbixProxy_PSKローテーション.md"
  "__DOC_BACKUP_DR__"   = "$repo\msp-frontend-server\運用手順書_バックアップDR方針.md"
  "__GUIDE_SENSOR_EDGE__" = "$repo\Sensor Edge\実施手順_顧客追加フロー.md"
  "__GUIDE_ONBOARDING__"  = "$repo\msp-customer-portal\docs\実施手順_顧客オンボーディング統合フロー.md"
  "__GUIDE_DEPLOY__"      = "$repo\zabbixserver\実施手順_デプロイ.md"
  "__GUIDE_PW_ADMIN__"    = "$repo\msp-frontend-server\実施手順_Zabbix管理者パスワードローテーション.md"
  "__GUIDE_PW_DB__"       = "$repo\msp-frontend-server\実施手順_zabbix-server_DBパスワードローテーション.md"
  "__GUIDE_PSK_PROXY__"   = "$repo\msp-frontend-server\実施手順_ZabbixProxy_PSKローテーション.md"
  "__GUIDE_BACKUP_DR__"   = "$repo\msp-frontend-server\実施手順_バックアップDR方針.md"
  "__DOC_DEVICE_MGMT__"   = "$repo\Sensor Edge\運用手順書_機器管理システム.md"
  "__GUIDE_DEVICE_MGMT__" = "$repo\Sensor Edge\実施手順_機器管理システム.md"
}

$out = $template.Replace("__FONT_B64__", $fontB64)
$out = $out.Replace("__GEN_DATE__", (Get-Date -Format "yyyy-MM-dd"))

foreach ($key in $docs.Keys) {
  $path = $docs[$key]
  if (-not (Test-Path $path)) { throw "Missing source file: $path" }
  $content = Get-Content -Raw -Encoding UTF8 $path
  # 先頭の "# タイトル" 行を除去（ページ側で見出しを別途描画するため）
  $content = $content -replace '(?s)^\s*#\s+[^\r\n]*\r?\n', ''
  $content = $content.Replace("</script", "<_/script")
  $out = $out.Replace($key, $content)
}

# Claude Artifactは <!doctype html><head>...</head><body> の骨格を自動付与するが、
# nginxで直接配信するこのファイルには骨格が無いため、文字コード判定に失敗し文字化けする。
# ここで明示的にDOCTYPE・meta charsetを付与した完全なHTML文書にする。
$wrapped = "<!DOCTYPE html>`r`n<html lang=`"ja`">`r`n<head>`r`n<meta charset=`"UTF-8`">`r`n</head>`r`n<body>`r`n$out`r`n</body>`r`n</html>`r`n"

$outPath = "$repo\zabbixserver\runbooks.html"
[System.IO.File]::WriteAllText($outPath, $wrapped, [System.Text.UTF8Encoding]::new($false))

Write-Output "Wrote: $outPath"
Write-Output "Size: $((Get-Item $outPath).Length) bytes"
