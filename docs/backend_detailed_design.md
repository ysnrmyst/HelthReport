# バックエンド詳細設計

## 1. 全体構造

### 1.1. ディレクトリ構成

Flaskアプリケーションの標準的な構成に倣い、責務に応じてパッケージを分割します。

```
/
├── app.py                # アプリケーションのエントリポイント
├── requirements.txt      # 依存ライブラリ
├── venv/                 # Python仮想環境
├── .env                  # 環境変数ファイル
├── Dockerfile
├── static/               # 静的ファイル (CSS, JavaScript, 画像など)
├── templates/            # HTMLテンプレート
├── docs/                 # 設計ドキュメント
└── src/                  # アプリケーションのソースコード
    ├── __init__.py
    ├── auth/             # 認証関連 (Google OAuth)
    │   ├── __init__.py
    │   └── routes.py
    ├── models/           # データモデル (Pydanticモデルなど)
    │   ├── __init__.py
    │   ├── user.py
    │   ├── activity.py
    │   └── category.py
    ├── services/         # ビジネスロジック (BigQueryとの連携など)
    │   ├── __init__.py
    │   ├── user_service.py
    │   ├── activity_service.py
    │   └── category_service.py
    ├── api/              # APIエンドポイント (Blueprint)
    │   ├── __init__.py
    │   ├── v1/
    │   │   ├── __init__.py
    │   │   ├── users.py
    │   │   ├── activities.py
    │   │   └── categories.py
    └── core/             # コアコンポーネント (DBクライアント, エラーハンドラなど)
        ├── __init__.py
        └── db.py
```

### 1.2. コンポーネントの責務

*   **`app.py`**: Flaskアプリケーションインスタンスを作成し、Blueprintを登録する。アプリケーション全体の設定を読み込む。
*   **`src/auth/`**: Google OAuth 2.0によるユーザー認証・セッション管理を担当する。コールバック処理やログイン・ログアウトのエンドポイントを定義する。
*   **`src/models/`**: APIのレスポンスやリクエストボディ、およびサービス層で扱うデータの構造をPydanticモデルとして定義する。これにより、データのバリデーションと型安全性を確保する。
*   **`src/services/`**: ビジネスロジックを実装する。BigQueryクライアントライブラリを直接使用して、データベースとのデータ操作（CRUD）を行う。
*   **`src/api/v1/`**: Flask Blueprintを使用してAPIのエンドポイントを定義する。各ルートは、リクエストを受け取り、適切なサービスを呼び出し、結果をJSON形式で返す責務を持つ。
*   **`src/core/`**: アプリケーション全体で共有されるコンポーネントを配置する。BigQueryクライアントの初期化や、共通のエラーハンドリング処理などをここにまとめる。

---

## 2. 行動記録管理機能 (Activity Management) の詳細設計

### 2.1. データモデル (`src/models/activity.py`)

API設計書とデータベーススキーマに基づき、Pydanticモデルを定義します。

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
import uuid

class ActivityBase(BaseModel):
    """行動記録の基本モデル"""
    start_time: datetime = Field(..., description="活動の開始日時")
    end_time: datetime = Field(..., description="活動の終了日時")
    activity_content: str = Field(..., description="活動内容のテキスト記述")
    category_id: str = Field(..., description="活動カテゴリのID")
    fatigue_level: int = Field(..., ge=1, le=5, description="心身の負荷レベル (1-5)")
    fatigue_notes: Optional[str] = Field(None, description="負荷に関する自由記述")

class ActivityCreate(ActivityBase):
    """行動記録の作成用モデル"""
    pass

class ActivityUpdate(BaseModel):
    """行動記録の更新用モデル（部分更新を許容）"""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    activity_content: Optional[str] = None
    category_id: Optional[str] = None
    fatigue_level: Optional[int] = Field(None, ge=1, le=5)
    fatigue_notes: Optional[str] = None

class ActivityInDB(ActivityBase):
    """データベース格納用モデル"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="行動記録の一意なID")
    user_id: str = Field(..., description="記録を行ったユーザーのID")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True

class ActivityResponse(ActivityInDB):
    """APIレスポンス用モデル"""
    pass
```

### 2.2. サービス (`src/services/activity_service.py`)

BigQueryとの連携ロジックを実装します。

```python
from google.cloud import bigquery
from typing import List, Optional
from src.models.activity import ActivityCreate, ActivityUpdate, ActivityInDB

# BigQueryクライアントの初期化 (core.dbで管理)
# client = bigquery.Client()
# TABLE_ID = "your-project.your_dataset.activities"

class ActivityService:
    def __init__(self, db_client: bigquery.Client, table_id: str):
        self.client = db_client
        self.table_id = table_id

    def create_activity(self, user_id: str, activity_data: ActivityCreate) -> Optional[ActivityInDB]:
        # データをActivityInDBモデルに変換し、辞書型にする
        # BigQueryにストリーミング挿入するロジック
        pass

    def get_activities_by_user(self, user_id: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[ActivityInDB]:
        # クエリを構築し、ユーザーの行動記録を取得するロジック
        pass

    def get_activity_by_id(self, activity_id: str, user_id: str) -> Optional[ActivityInDB]:
        # 特定のIDの行動記録を取得するロジック
        pass

    def update_activity(self, activity_id: str, user_id: str, update_data: ActivityUpdate) -> Optional[ActivityInDB]:
        # UPDATE文を構築し、行動記録を更新するロジック
        # BigQueryのUPDATEはコストがかかるため、設計に注意が必要
        pass

    def delete_activity(self, activity_id: str, user_id: str) -> bool:
        # DELETE文を実行し、行動記録を削除するロジック
        pass
```

### 2.3. APIルート (`src/api/v1/activities.py`)

Flask Blueprintを使用してエンドポイントを定義します。

```python
from flask import Blueprint, request, jsonify
from src.services.activity_service import ActivityService
from src.models.activity import ActivityCreate, ActivityUpdate
# from src.auth.decorators import login_required # 認証デコレータ

# サービスのインスタンス化 (依存性注入の形が望ましい)
# activity_service = ActivityService(...)

activities_bp = Blueprint('activities', __name__, url_prefix='/api/v1/activities')

@activities_bp.route('/', methods=['POST'])
# @login_required
def create_activity_route(current_user):
    # リクエストボディをPydanticモデルでバリデーション
    # サービスを呼び出して記録を作成
    # 結果をJSONで返す
    pass

@activities_bp.route('/', methods=['GET'])
# @login_required
def get_activities_route(current_user):
    # クエリパラメータを取得
    # サービスを呼び出して記録を取得
    # 結果をJSONで返す
    pass

# ... 他のエンドポイント (GET by ID, PATCH, DELETE) も同様に定義 ...
```
