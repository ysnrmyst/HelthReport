# API設計ドキュメント

## 認証方式の変更

- これまでのGoogle OAuth認証は廃止し、**ID・パスワード認証**に切り替えます。
- ユーザーはメールアドレス（またはユーザーID）とパスワードでログインします。
- 認証成功時はFlaskセッションに`user_id`を保存し、以降のAPIリクエストで認証状態を管理します。

## 認証API

### ログイン
- `POST /login`
  - リクエストボディ: `{ "username": "string", "password": "string" }`
  - 成功時: 200 OK, セッションにuser_idを保存
  - 失敗時: 401 Unauthorized

### ログアウト
- `GET /logout`
  - セッションをクリア
  - 200 OK

### セッション確認
- `GET /session`
  - ログイン状態かどうかを返す
  - 例: `{ "logged_in": true, "user_id": "..." }`

## ユーザー登録API
- `POST /register`
  - リクエストボディ: `{ "username": "string", "password": "string" }`
  - 成功時: 201 Created, `{ "user_id": "..." }` など
  - 失敗時: 400 Bad Request

## フロントエンド（新規ユーザー登録画面）
- `/register` で新規ユーザー登録フォームを表示
- ユーザー名・パスワードを入力し、登録APIを呼び出す
- 登録成功時はログイン画面へ遷移
- エラー時は画面上にエラーメッセージを表示

## 既存API
- `/api/v1/activities`などのAPIは、セッションの`user_id`で認証・認可を行う

---

## 今後の実装方針
- Google認証関連のコード・依存パッケージは削除
- ID・パスワード認証のためのユーザーテーブル（BigQuery等）を利用
- React側もログインフォームをID・パスワード入力に変更

## 1. 行動記録管理機能

### 1.1. 行動記録の登録 (Create Activity Record)

*   **目的**: 新しい行動記録を登録する。
*   **HTTPメソッド**: `POST`
*   **URL**: `/api/v1/activities`
*   **認証**: 必須 (Googleアカウント認証)
*   **リクエストボディ (JSON)**:
    ```json
    {
      "start_time": "2025-06-29T08:00:00+09:00",
      "end_time": "2025-06-29T09:00:00+09:00",
      "activity_content": "業務でメールを書いていた",
      "category_id": "c7a4a3c5-30e5-4ebf-8a25-7a7a4e8e6e1a",
      "fatigue_level": 3,
      "fatigue_notes": "微かに疲労感があった"
    }
    ```
*   **レスポンス (JSON)**:
    *   **成功 (201 Created)**: 登録された行動記録のデータ
        ```json
        {
          "id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
          "user_id": "f0e9d8c7-b6a5-4321-fedc-ba9876543210",
          "start_time": "2025-06-29T08:00:00+09:00",
          "end_time": "2025-06-29T09:00:00+09:00",
          "activity_content": "業務でメールを書いていた",
          "category_id": "c7a4a3c5-30e5-4ebf-8a25-7a7a4e8e6e1a",
          "fatigue_level": 3,
          "fatigue_notes": "微かに疲労感があった",
          "created_at": "2025-06-29T09:05:00+09:00",
          "updated_at": "2025-06-29T09:05:00+09:00"
        }
        ```

### 1.2. 行動記録の取得 (Get Activity Records)

*   **目的**: ユーザーの行動記録を一覧で取得する。
*   **HTTPメソッド**: `GET`
*   **URL**: `/api/v1/activities`
*   **クエリパラメータ**:
    *   `start_date` (Optional, YYYY-MM-DD)
    *   `end_date` (Optional, YYYY-MM-DD)
    *   `category_id` (Optional, STRING)
    *   `page` (Optional, INT, default: 1)
    *   `limit` (Optional, INT, default: 20)
    *   `sort_by` (Optional, STRING, e.g., `start_time`)
    *   `order` (Optional, STRING, `asc` or `desc`)

### 1.3. 行動記録の更新 (Update Activity Record)

*   **目的**: 既存の行動記録を更新する。
*   **HTTPメソッド**: `PATCH`
*   **URL**: `/api/v1/activities/{activity_id}`

### 1.4. 行動記録の削除 (Delete Activity Record)

*   **目的**: 既存の行動記録を削除する。
*   **HTTPメソッド**: `DELETE`
*   **URL**: `/api/v1/activities/{activity_id}`

## 2. データ分析・可視化機能

### 2.1. 日次振り返りの取得 (Get Daily Reflections)

*   **目的**: ユーザーの日次振り返りデータを取得する。
*   **HTTPメソッド**: `GET`
*   **URL**: `/api/v1/daily-reflections`
*   **レスポンス (JSON)**:
    *   **成功 (200 OK)**:
        ```json
        {
          "data": [
            {
              "id": "d1e2f3a4-b5c6-7890-1234-567890abcdef",
              "user_id": "f0e9d8c7-b6a5-4321-fedc-ba9876543210",
              "reflection_date": "2025-06-29",
              "total_activity_duration_minutes": 480,
              "average_fatigue_level": 3.5,
              "checkpoint_scores": [
                {"name": "気分の良さ", "score": 4},
                {"name": "集中度", "score": 5}
              ],
              "user_comment": "今日は集中できた。",
              "ai_comment": "生産的な一日でしたね。",
              "created_at": "2025-06-29T23:59:00+09:00",
              "updated_at": "2025-06-29T23:59:00+09:00"
            }
          ]
        }
        ```

### 2.2. 日次振り返りの生成・更新 (Create/Update Daily Reflection)

*   **目的**: 特定の日の日次振り返りを生成または更新する。
*   **HTTPメソッド**: `POST`
*   **URL**: `/api/v1/daily-reflections`
*   **リクエストボディ (JSON)**:
    ```json
    {
      "reflection_date": "2025-06-29",
      "checkpoint_scores": [
        {"name": "気分の良さ", "score": 4},
        {"name": "集中度", "score": 5}
      ],
      "user_comment": "今日は集中できた。"
    }
    ```
*   **レスポンス (JSON)**:
    *   **成功 (200 OK or 201 Created)**: 生成/更新された日次振り返りデータ。

### 2.3. 週次振り返りの取得 (Get Weekly Reflections)

*   **目的**: ユーザーの週次振り返りデータを取得する。
*   **HTTPメソッド**: `GET`
*   **URL**: `/api/v1/weekly-reflections`

### 2.4. 週次振り返りの生成・更新 (Create/Update Weekly Reflection)

*   **目的**: 特定の週の週次振り返りを生成または更新する。
*   **HTTPメソッド**: `POST`
*   **URL**: `/api/v1/weekly-reflections`
*   **リクエストボディ (JSON)**:
    ```json
    {
      "week_start_date": "2025-06-23",
      "reflection_notes": "今週は業務に集中できた。"
    }
    ```
*   **レスポンス (JSON)**:
    *   **成功 (200 OK or 201 Created)**: 生成/更新された週次振り返りデータ。

### 2.5. 週次振り返りAI診断リクエスト (Weekly Reflection AI Diagnosis Request)

*   **目的**: 週次振り返りの内容をAIに送信し、診断コメントを取得する。
*   **HTTPメソッド**: `POST`
*   **URL**: `/api/v1/weekly-reflections/ai-diagnosis`
*   **リクエストボディ (JSON)**:
    ```json
    {
      "title": "週次振り返りAI診断",
      "questions": [
        { "text": "今週は十分な睡眠が取れましたか？", "score": 4 },
        { "text": "今週はバランスの良い食事ができましたか？", "score": 3 },
        { "text": "今週は適度な運動ができましたか？", "score": 5 },
        { "text": "今週はストレスを感じることが多かったですか？", "score": 2 },
        { "text": "今週は仕事や学業に集中できましたか？", "score": 4 },
        { "text": "今週は気分が前向きでしたか？", "score": 5 }
      ],
      "anxieties": "今週は仕事が忙しくて疲れました。",
      "good_things": "家族と過ごす時間が取れました。",
      "reflection_notes": ""
    }
    ```
*   **レスポンス (JSON)**:
    *   **成功 (200 OK)**:
        ```json
        {
          "ai_comment": "今週は忙しい中でも家族との時間を大切にできて素晴らしいですね。..."
        }
        ```
    *   **失敗 (400 Bad Request)**: エラーメッセージ

### 2.6. 週次振り返り保存・更新 (Create/Update Weekly Reflection)

*   **目的**: 週次振り返りデータを保存または更新する。
*   **HTTPメソッド**: `POST`
*   **URL**: `/api/v1/weekly-reflections`
*   **リクエストボディ (JSON)**:
    ```json
    {
      "title": "週次振り返り",
      "questions": [
        { "text": "今週は十分な睡眠が取れましたか？", "score": 4 },
        { "text": "今週はバランスの良い食事ができましたか？", "score": 3 },
        { "text": "今週は適度な運動ができましたか？", "score": 5 },
        { "text": "今週はストレスを感じることが多かったですか？", "score": 2 },
        { "text": "今週は仕事や学業に集中できましたか？", "score": 4 },
        { "text": "今週は気分が前向きでしたか？", "score": 5 }
      ],
      "anxieties": "今週は仕事が忙しくて疲れました。",
      "good_things": "家族と過ごす時間が取れました。",
      "week_start_date": "2025-06-23",
      "ai_diagnosis_result": "今週は忙しい中でも家族との時間を大切にできて素晴らしいですね。...",
      "reflection_notes": ""
    }
    ```
*   **レスポンス (JSON)**:
    *   **成功 (201 Created)**: 保存された週次振り返りデータ
    *   **失敗 (400 Bad Request)**: 
        *   通常のエラー：詳細なエラーメッセージ
        *   BigQueryストリーミングバッファエラー：「このデータは登録直後のため、2時間程度更新できない場合があります（BigQueryの仕様）。しばらくしてから再度お試しください。」
    }
    ```
*   **レスポンス (JSON)**:
    *   **成功 (200 OK)**:
        ```json
        {
          "ai_comment": "睡眠や運動がしっかり取れており、全体的に良い週でした。ストレスがやや高めなので、リラックスできる時間を意識しましょう。"
        }
        ```

## 3. ユーザー管理機能

### 3.1. ユーザー情報の取得 (Get User Profile)

*   **HTTPメソッド**: `GET`
*   **URL**: `/api/v1/users/me`

### 3.2. ユーザー情報の更新 (Update User Profile)

*   **HTTPメソッド**: `PATCH`
*   **URL**: `/api/v1/users/me`

## 4. 活動カテゴリ管理機能

### 4.1. 活動カテゴリの取得 (Get Activity Categories)

*   **HTTPメソッド**: `GET`
*   **URL**: `/api/v1/activity-categories`

### 4.2. 活動カテゴリの作成 (Create Activity Category)

*   **HTTPメソッド**: `POST`
*   **URL**: `/api/v1/activity-categories`

### 4.3. 活動カテゴリの更新 (Update Activity Category)

*   **HTTPメソッド**: `PATCH`
*   **URL**: `/api/v1/activity-categories/{category_id}`

### 4.4. 活動カテゴリの削除 (Delete Activity Category)

*   **HTTPメソッド**: `DELETE`
*   **URL**: `/api/v1/activity-categories/{category_id}`

## 5. 標準エラーレスポンス

APIからのエラーレスポンスは、以下の統一されたJSON形式で返されます。

```json
{
  "error": {
    "code": "INVALID_INPUT",
    "message": "Invalid input provided.",
    "details": {}
  }
}
```