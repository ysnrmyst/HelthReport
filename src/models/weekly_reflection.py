from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import List, Optional
import uuid

class WeeklyReflectionQuestion(BaseModel):
    text: str = Field(..., description="設問文")
    score: int = Field(..., ge=1, le=5, description="5段階評価スコア")

class WeeklyReflectionBase(BaseModel):
    week_start_date: date = Field(..., description="週の開始日")
    reflection_notes: Optional[str] = Field(None, description="週の振り返りノート")
    title: Optional[str] = Field(None, description="AI診断リクエストのタイトル")
    questions: Optional[List[WeeklyReflectionQuestion]] = Field(None, description="設問文＋スコア配列")
    anxieties: Optional[str] = Field(None, description="不安なこと")
    good_things: Optional[str] = Field(None, description="良かったこと")
    ai_diagnosis_result: Optional[str] = Field(None, description="AI診断コメント")
    weekly_total_load_points: Optional[float] = Field(None, description="週次負荷ポイント合計")

class WeeklyReflectionCreate(WeeklyReflectionBase):
    pass

class WeeklyReflectionInDB(WeeklyReflectionBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="週次振り返りの一意なID")
    user_id: str = Field(..., description="ユーザーID")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True

class WeeklyReflectionResponse(WeeklyReflectionInDB):
    pass 