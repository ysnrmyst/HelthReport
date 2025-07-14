# データベーススキーマ定義 (BigQuery)

**ノート:** BigQueryはリレーショナルデータベースではないため、主キーや外部キーの制約は物理的には適用されません。しかし、アプリケーションレベルでのデータ一貫性を保つため、これらの関係性を論理的な制約として定義します。

- プロジェクトID: health-report-465810
- データセット名: health_data

## 1. ユーザー (Users) テーブル

Googleアカウント認証で取得するユーザー情報と、アプリケーション内で管理するユーザー固有の情報を格納します。

| カラム名              | データ型      | 制約           | 説明                                                      |
| :-------------------- | :------------ | :------------- | :-------------------------------------------------------- |
| `id`                  | STRING        | 主キー, NOT NULL | ユーザーの一意なID (UUID)                                 |
| `email`               | STRING        | UNIQUE, NOT NULL | ユーザーのメールアドレス (Googleアカウントから取得)         |
| `display_name`        | STRING        | NULL           | ユーザーの表示名 (Googleアカウントから取得、任意)         |
| `profile_picture_url` | STRING        | NULL           | プロフィール画像のURL (Googleアカウントから取得、任意)    |
| `created_at`          | TIMESTAMP     | NOT NULL       | レコード作成日時 (自動設定)                               |
| `updated_at`          | TIMESTAMP     | NOT NULL       | レコード最終更新日時 (自動設定)                           |
| `username`            | STRING        | UNIQUE, NOT NULL | ユーザー名またはメールアドレス                            |
| `password_hash`       | STRING        | NOT NULL       | パスワードのハッシュ値                                      |

## 2. 活動カテゴリ (ActivityCategories) テーブル

ユーザーが行動記録で選択する活動カテゴリを格納します。

| カラム名            | データ型      | 制約           | 説明                                                              |
| :------------------ | :------------ | :------------- | :---------------------------------------------------------------- |
| `id`                | STRING        | 主キー, NOT NULL | カテゴリの一意なID (UUID)                                         |
| `user_id`           | STRING        | 外部キー, NULL | カテゴリを作成したユーザーのID (`Users.id`への参照)。NULLはシステム定義カテゴリ。 |
| `name`              | STRING        | NOT NULL       | カテゴリ名 (例: "学習", "会議", "休憩", "運動")                   |
| `category_group`    | STRING        | NOT NULL       | カテゴリのグループ (例: "業務", "プライベート", "学習")           |
| `description`       | STRING        | NULL           | カテゴリの詳細説明（任意）                                        |
| `is_system_defined` | BOOL          | NOT NULL       | システム定義カテゴリかどうかのフラグ (True: システム定義)         |
| `created_at`        | TIMESTAMP     | NOT NULL       | レコード作成日時 (自動設定)                                       |
| `updated_at`        | TIMESTAMP     | NOT NULL       | レコード最終更新日時 (自動設定)                                   |

## 3. 行動記録 (Activities) テーブル

ユーザーの個々の行動記録と、それに関連する心身の負荷を格納します。

| カラム名           | データ型      | 制約           | 説明                                                              |
| :----------------- | :------------ | :------------- | :---------------------------------------------------------------- |
| `id`               | STRING        | 主キー, NOT NULL | 行動記録の一意なID (UUID)                                         |
| `user_id`          | STRING        | 外部キー, NOT NULL | 記録を行ったユーザーのID (`Users.id`への参照)                     |
| `start_time`       | TIMESTAMP     | NOT NULL       | 活動の開始日時                                                    |
| `end_time`         | TIMESTAMP     | NOT NULL       | 活動の終了日時                                                    |
| `activity_content` | STRING        | NOT NULL       | 活動内容のテキスト記述 (例: "業務でメールを書いていた")           |
| `category_id`      | STRING        | 外部キー, NOT NULL | 活動カテゴリのID (`ActivityCategories.id`への参照)                |
| `fatigue_level`    | INT64         | NOT NULL       | 心身の負荷レベル (1-5の整数値)                                    |
| `fatigue_notes`    | STRING        | NULL           | 負荷に関する自由記述 (例: "微かに疲労感があった")                 |
| `created_at`       | TIMESTAMP     | NOT NULL       | レコード作成日時 (自動設定)                                       |
| `updated_at`       | TIMESTAMP     | NOT NULL       | レコード最終更新日時 (自動設定)                                   |

## 4. 日次振り返り (DailyReflections) テーブル

ユーザーごとの日次集計データと振り返り情報、AIによるコメント、そして固定のチェックポイント評価を格納します。

| カラム名                            | データ型      | 制約                                  | 説明                                                              |
| :---------------------------------- | :------------ | :------------------------------------ | :---------------------------------------------------------------- |
| `id`                                | STRING        | 主キー, NOT NULL                      | 日次振り返りレコードの一意なID (UUID)                             |
| `user_id`                           | STRING        | 外部キー, NOT NULL                    | 振り返りを行ったユーザーのID (`Users.id`への参照)                 |
| `reflection_date`                   | DATE          | NOT NULL, UNIQUE (`user_id`, `reflection_date`) | 振り返りの対象日                                                  |
| `total_activity_duration_minutes`   | INT64         | NOT NULL                              | その日の総活動時間 (分単位)                                       |
| `average_fatigue_level`             | NUMERIC       | NOT NULL                              | その日の平均疲労レベル                                            |
| `checkpoint_scores`                 | JSON          | NOT NULL                              | チェックポイント評価 (例: `[{"name": "気分の良さ", "score": 4}, ...]`) |
| `user_comment`                      | STRING        | NULL                                  | ユーザーによるその日の振り返りコメント                            |
| `ai_comment`                        | STRING        | NULL                                  | AIによるその日の行動と負荷の分析結果（テキスト）                  |
| `created_at`                        | TIMESTAMP     | NOT NULL                              | レコード作成日時 (自動設定)                                       |
| `updated_at`                        | TIMESTAMP     | NOT NULL                              | レコード最終更新日時 (自動設定)                                   |

## 5. 週次振り返り (WeeklyReflections) テーブル

ユーザーごとの週次集計データと振り返り情報、そしてAIによる診断結果・AI診断リクエスト内容を格納します。

| カラム名                          | データ型      | 制約                                  | 説明                                                              |
| :-------------------------------- | :------------ | :------------------------------------ | :---------------------------------------------------------------- |
| `id`                              | STRING        | 主キー, NOT NULL                      | 振り返りレコードの一意なID (UUID)                                 |
| `user_id`                         | STRING        | 外部キー, NOT NULL                    | 振り返りを行ったユーザーのID (`Users.id`への参照)                 |
| `week_start_date`                 | DATE          | NOT NULL, UNIQUE (`user_id`, `week_start_date`) | 週の開始日 (例: 月曜日)                                           |
| `most_frequent_category_id`       | STRING        | 外部キー, NULL                        | その週で最も活動時間の長かったカテゴリのID (`ActivityCategories.id`への参照) |
| `reflection_notes`                | STRING        | NULL                                  | 週の振り返りに関する自由記述やシステム生成のサマリー              |
| `ai_diagnosis_result`             | STRING        | NULL                                  | AIによる週次の行動と負荷の分析結果（テキスト）                    |
| `title`                           | STRING        | NULL                                  | AI診断リクエスト時のタイトル                                      |
| `questions`                       | JSON          | NULL                                  | AI診断リクエスト時の設問文＋スコア配列（例: `[{"text": "今週は十分な睡眠が取れましたか？", "score": 4}, ...]`） |
| `anxieties`                       | STRING        | NULL                                  | AI診断リクエスト時の「不安なこと」                                |
| `good_things`                     | STRING        | NULL                                  | AI診断リクエスト時の「良かったこと」                              |
| `created_at`                      | TIMESTAMP     | NOT NULL                              | レコード作成日時 (自動設定)                                       |
| `updated_at`                      | TIMESTAMP     | NOT NULL                              | レコード最終更新日時 (自動設定)                                   |
