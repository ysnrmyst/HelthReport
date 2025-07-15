# 1. Node.js/Reactビルド用ステージ
FROM node:18-slim AS frontend-build
WORKDIR /frontend
COPY static/frontend/package*.json ./
RUN npm ci
COPY static/frontend ./
ARG REACT_APP_API_BASE_URL
RUN REACT_APP_API_BASE_URL=$REACT_APP_API_BASE_URL CI=true npm run build

# 2. Python/Flask本番用ステージ
FROM python:3.9-slim

# 必要なシステムパッケージだけインストール
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python依存のみ先にインストール（キャッシュ効率UP）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリ本体をコピー
COPY . .

# フロントエンドのビルド成果物だけをコピー
COPY --from=frontend-build /frontend/build ./static/frontend/build

EXPOSE 8080

CMD ["python", "app.py"]
