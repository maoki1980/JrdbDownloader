# JrdbDownloader

## Dockerによるデプロイ方法

### イメージを構築

プロジェクトディレクトリで以下を実行

```bash
docker build --no-cache -t jrdbdownloader .
```

### コンテナを起動

```bash
docker run -d \
--name jrdbdownloader \
-v {absolute_path/to/project_dir}/JRDB_ZIP:/app/JRDB_ZIP \
-v {absolute_path/to/project_dir}/JRDB:/app/JRDB \
-v {absolute_path/to/project_dir}/CRON_LOG:/app/CRON_LOG \
-e TZ=Asia/Tokyo \
-e JRDB_USER={jrdb_user_id} \
-e JRDB_PASS={jrdb_password} \
jrdbdownloader:latest
```

### コンテナ内でコマンドを実行する方法

```bash
docker exec -it jrdbdownloader /bin/bash
```

でコンテナ内に入れる。例えば以下のコマンドで、JRDBのデータの差分をダウンロードできる。

```bash
/usr/local/bin/python /app/src/jrdbdownloader/main.py
```

### イメージファイルの作成

```bash
docker save -o jrdbdownloader.tar jrdbdownloader:latest
```
