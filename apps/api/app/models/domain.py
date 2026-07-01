from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass
class ChatMessage:
    role: str
    content: str
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ChatSession:
    id: str
    user_id: str
    title: str
    messages: List[ChatMessage] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class EpisodicMemoryItem:
    user_id: str
    memory: str
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SearchResultChunk:
    source: str
    content: str
    score: float
