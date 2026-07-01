from __future__ import annotations

from pydantic import BaseModel
from datetime import datetime
from typing import List


class ChatMessageDto(BaseModel):
    role: str
    content: str
    created_at: datetime


class SessionCreateResponse(BaseModel):
    session_id: str


class SessionSummary(BaseModel):
    session_id: str
    title: str
    created_at: datetime


class SessionDetail(BaseModel):
    session_id: str
    title: str
    messages: List[ChatMessageDto]
    created_at: datetime


class EpisodicMemoryRequest(BaseModel):
    memory: str


class EpisodicMemoryResponse(BaseModel):
    user_id: str
    memory: str
    created_at: datetime
