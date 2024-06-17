# ベースイメージ
FROM python:3.12-slim

# 作業ディレクトリの設定
WORKDIR /app

# 依存関係のコピーとインストール
COPY requirements.txt ./
COPY .env.docker ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# アプリケーションのソースコードをコピー
COPY src/ ./src/

# 環境変数の設定
ENV PYTHONPATH="/app/src"
ENV PYTHONUNBUFFERED="1"
ENV ENV_FILE="/app/.env.docker"

# cronとbashのインストール
RUN apt-get update && apt-get install -y cron bash

# cronジョブスクリプトのコピー
COPY cron_job.sh /usr/local/bin/cron_job.sh

# 実行権限を付与
RUN chmod +x /usr/local/bin/cron_job.sh

# エントリーポイントの更新
ENTRYPOINT ["/usr/local/bin/cron_job.sh"]
