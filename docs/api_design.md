# API設計

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