# 健康管理アプリケーション 要件定義

## 1. アプリケーションの目的

ユーザーの健康状態を管理し、過度な負荷による体調悪化を未然に防ぐためのサポートを行う。日々の活動、睡眠データを記録し、体調との関連性を分析して個別のアドバイスを提供する。

## 2. 主要機能

### 2.1. データ入力機能

*   **活動記録**: 日付、カテゴリ（業務、学習、休憩など）、活動内容、時間を記録する。
*   **体調記録**: 日付、体調（5段階評価）、睡眠時間、自由記述のメモを記録する。

### 2.2. データ表示・振り返り機能

*   **日次サマリー**: 特定の日の活動記録と体調を一覧表示する。
*   **週次レポート**: 週ごとのデータ集計（平均睡眠時間、活動時間の合計、体調の推移など）と、AIによる総括コメントを表示する。

### 2.3. アドバイス機能

*   **個別アドバイス**: 記録されたデータに基づき、AIがパーソナライズされたアドバイス（例：「今日は〇〇に注意しましょう」）を生成する。

### 2.4. ユーザー管理

*   **認証**: GoogleアカウントによるOAuth 2.0認証を実装する。
*   **プロフィール**: ユーザー名やプロフィール画像を設定できる。

## 3. 非機能要件

*   **セキュリティ**: ユーザーデータは安全に保管し、不正アクセスを防ぐ。
*   **プライバシー**: プライバシーポリシーを明記し、ユーザーの同意なしにデータを第三者に提供しない。
*   **データ管理**: ユーザーは自身のデータをいつでも削除できる（論理削除、物理削除の両方を検討）。

## 4. 技術スタック（案）

*   **バックエンド**: Python (Flask)
*   **フロントエンド**: HTML, CSS, JavaScript (React)
*   **データベース**: Google BigQuery（データセット名: health_data、プロジェクトID: health-report-465810）
*   **AI/ML**: Vertex AI Gemini API
*   **認証**: Google OAuth 2.0
*   **デプロイ**: Google Cloud Run