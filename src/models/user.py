from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
import uuid

class UserBase(BaseModel):
    """ユーザー情報の基本モデル"""
    google_id: str = Field(..., description="Googleアカウントから取得するユーザーID")
    email: str = Field(..., description="ユーザーのメールアドレス")
    display_name: Optional[str] = Field(None, description="ユーザーの表示名")
    profile_picture_url: Optional[str] = Field(None, description="プロフィール画像のURL")

class UserCreate(UserBase):
    """ユーザー情報の作成用モデル"""
    pass

class UserInDB(UserBase):
    """データベース格納用モデル"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="ユーザーの一意なID")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True

class UserResponse(UserInDB):
    """APIレスポンス用モデル"""
    pass 