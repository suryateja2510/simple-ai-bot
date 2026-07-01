from __future__ import annotations

import asyncio
from pathlib import Path
from typing import AsyncIterator, Dict, List
from uuid import uuid4

from app.models.domain import (
    ChatMessage,
    ChatSession,
    EpisodicMemoryItem,
    SearchResultChunk,
)
from app.services.interfaces import (
    AuthService,
    ChatCompletionService,
    EpisodicMemoryService,
    SearchService,
    SessionMemoryService,
)


class MockAuthService(AuthService):
    async def get_current_user(self) -> str:
        return "demo-user"


class InMemorySessionMemoryService(SessionMemoryService):
    def __init__(self) -> None:
        self.sessions: Dict[str, ChatSession] = {}

    async def create_session(self, user_id: str, title: str) -> ChatSession:
        session_id = str(uuid4())
        session = ChatSession(id=session_id, user_id=user_id, title=title)
        self.sessions[session_id] = session
        return session

    async def list_sessions(self, user_id: str) -> List[ChatSession]:
        return [session for session in self.sessions.values() if session.user_id == user_id]

    async def get_session(self, session_id: str) -> ChatSession | None:
        return self.sessions.get(session_id)

    async def add_message(self, session_id: str, message: ChatMessage) -> None:
        session = self.sessions.get(session_id)
        if session is None:
            return
        session.messages.append(message)


class InMemoryEpisodicMemoryService(EpisodicMemoryService):
    def __init__(self) -> None:
        self.memories: Dict[str, EpisodicMemoryItem] = {}

    async def get_memory(self, user_id: str) -> EpisodicMemoryItem | None:
        return self.memories.get(user_id)

    async def upsert_memory(self, user_id: str, memory: str) -> EpisodicMemoryItem:
        item = EpisodicMemoryItem(user_id=user_id, memory=memory)
        self.memories[user_id] = item
        return item


class LocalPdfSearchService(SearchService):
    def __init__(self, data_folder: Path) -> None:
        self.data_folder = data_folder
        self.document_path = self.data_folder / "sample.pdf"
        self._load_document()

    def _load_document(self) -> None:
        if not self.document_path.exists():
            return

    async def retrieve(self, query: str) -> List[SearchResultChunk]:
        return [
            SearchResultChunk(
                source="sample.pdf",
                content="This is a local search result for the sample PDF. Use this content to augment the answer.",
                score=0.9,
            )
        ]


class MockChatCompletionService(ChatCompletionService):
    async def stream_complete(self, prompt: str) -> AsyncIterator[str]:
        answer = (
            "Sure, I can help with that. This mock service streams a response token by token "
            "so the UI can render partial output while the model generates text."
        )
        for token in answer.split(" "):
            await asyncio.sleep(0.05)
            yield token + " "
