#!/bin/bash

# 環境変数をロードするために、環境変数をcronにエクスポート
printenv | grep -v "no_proxy" >> /etc/environment

# ログディレクトリの作成
mkdir -p /app/CRON_LOG

# cronジョブの設定
echo "10 * * * * root /usr/local/bin/python /app/src/jrdbdownloader/main.py >> /app/logs/cron.log 2>&1" > /etc/cron.d/jrdbdownloader

# cronジョブの権限設定
chmod 0644 /etc/cron.d/jrdbdownloader

# cronサービスを開始
cron

# ログファイルが作成されるまで待機
touch /app/CRON_LOG/cron.log
tail -f /app/CRON_LOG/cron.log
