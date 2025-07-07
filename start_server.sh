#!/bin/bash

echo "=== Flaskサーバーを起動します ==="

# ポート8080のプロセスを終了
echo "1. ポート8080の既存プロセスを終了します..."
lsof -i :8080 | grep LISTEN | awk '{print $2}' | xargs kill -9 2>/dev/null || echo "ポート8080のプロセスは見つかりませんでした"

# 環境変数を設定
echo "2. 環境変数を設定します..."
export FLASK_ENV="development"
export OAUTHLIB_INSECURE_TRANSPORT=1

echo "3. Flaskサーバーを起動します..."
echo "Ctrl+Cで停止できます"
echo ""

python app.py 