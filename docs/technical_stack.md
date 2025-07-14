### 技術スタック提案 (BigQuery特化版)

#### 1. バックエンド (API)

*   **言語**: **Python**
    *   既存のファイルとAI連携のライブラリとの一貫性を維持します。
*   **フレームワーク**: **Flask**
    *   既存のプロジェクト構造に適合します。
*   **認証**: **Google OAuth 2.0 (Python)**
    *   Googleアカウント認証を引き続き利用します。
*   **データベースアクセス**: **Google Cloud BigQuery Client Library for Python**
    *   BigQueryは従来のRDBのようなORM（SQLAlchemyなど）とは直接連携しません。代わりに、BigQueryのPythonクライアントライブラリを直接使用して、データの挿入、取得、更新、削除を行います。
    *   **考慮事項**:
        *   **データ操作**: 個々のレコードの更新や削除は、BigQueryの特性上、従来のRDBよりも複雑になる可能性があります（例: `UPDATE` や `DELETE` はテーブル全体を書き換える操作になる場合があるため、コストやパフォーマンスに影響する可能性があります）。ストリーミング挿入やパーティション分割、クラスタリングなどを適切に利用する必要があります。
        *   **スキーマ設計**: BigQueryのスキーマ設計（ネストされたフィールド、繰り返しフィールドなど）を最大限に活用することで、分析効率を高めることができます。
        *   **コスト**: BigQueryはクエリされたデータ量に基づいて課金されるため、効率的なクエリ設計が重要になります。

#### 2. データベース

*   **種類**: **Google BigQuery**
    *   すべてのデータ（ユーザー、行動記録、カテゴリ、日次/週次振り返り）をBigQueryに格納します。
    *   **データセットとテーブルの構成**:
        *   `users` テーブル
        *   `activities` テーブル
        *   `activity_categories` テーブル
        *   `daily_reflections` テーブル
        *   `weekly_reflections` テーブル
    *   **集計処理**: 日次・週次振り返りの集計は、BigQueryの強力なクエリ機能（SQL）を利用して、`activities` テーブルから定期的に実行し、`daily_reflections` および `weekly_reflections` テーブルに結果を書き込む形になります。これは、バッチ処理（例: Cloud Functions, Cloud Run, Dataflowなど）として実装されることが一般的です。

#### 3. フロントエンド (Web UI)

*   **フレームワーク**: **React (JavaScript/TypeScript)**
*   **スタイリング**: **Bootstrap** (または Material Design)
*   **ビルドツール**: **Vite** (または Webpack)
*   **グラフ・可視化**: **Recharts**
    *   週次振り返り一覧画面でのグラフ表示
    *   ComposedChart（2軸表示）で負荷ポイントと設問スコアを同時表示
    *   レスポンシブ対応でモバイル・デスクトップ両対応

#### 4. AI連携

*   **ライブラリ**: **Google Generative AI SDK (Python)**
    *   `google_generativeai` が `venv` に存在するため、Googleの生成AIモデル（Geminiなど）との連携に利用します。

#### 5. デプロイ・コンテナ化

*   **コンテナ化**: **Docker**
*   **デプロイ先**: Google Cloud Platform (Cloud Run, Cloud Functions, App Engineなど)
    *   BigQueryとの親和性が高く、インフラ管理の負担を軽減できます。
    *   本番Cloud RunサービスURL例：https://health-report-465810-621003261884.us-central1.run.app
