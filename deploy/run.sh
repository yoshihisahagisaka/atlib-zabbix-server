#!/bin/bash
# CVE/EoL突合 + LLDP新規ネイバー検知バッチの実行ラッパー。
# systemd (msp-security-batch.service) から呼び出される。
#
# /etc/msp-batch/env のZABBIX_PASSWORDはSecret Manager移行後に更新されておらず
# 陳腐化しているため、実行のたびにSecret Managerから最新値を取得して上書きする。
set -euo pipefail

set -a
. /etc/msp-batch/env
set +a

TOKEN=$(curl -s -H "Metadata-Flavor: Google" \
  "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token" \
  | python3 -c 'import sys,json;print(json.load(sys.stdin)["access_token"])')

export ZABBIX_PASSWORD=$(curl -s -H "Authorization: Bearer ${TOKEN}" \
  "https://secretmanager.googleapis.com/v1/projects/msp-zabbix/secrets/zabbix-api-password/versions/latest:access" \
  | python3 -c 'import sys,json,base64; d=json.load(sys.stdin); print(base64.b64decode(d["payload"]["data"]).decode())')

/opt/msp-batch/venv/bin/python3 /opt/msp-batch/batch/main.py
