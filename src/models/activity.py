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
    fatigue_level: int = Field(..., ge=0, le=5, description="心身の負荷レベル (0-5)")
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
    fatigue_level: Optional[int] = Field(None, ge=0, le=5)
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
