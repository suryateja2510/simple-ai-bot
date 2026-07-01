from __future__ import annotations

from abc import ABC, abstractmethod
from typing import AsyncIterator, List

from app.models.domain import ChatMessage, ChatSession, EpisodicMemoryItem, SearchResultChunk


class AuthService(ABC):
    @abstractmethod
    async def get_current_user(self) -> str:
        raise NotImplementedError


class SessionMemoryService(ABC):
    @abstractmethod
    async def create_session(self, user_id: str, title: str) -> ChatSession:
        raise NotImplementedError

    @abstractmethod
    async def list_sessions(self, user_id: str) -> List[ChatSession]:
        raise NotImplementedError

    @abstractmethod
    async def get_session(self, session_id: str) -> ChatSession | None:
        raise NotImplementedError

    @abstractmethod
    async def add_message(self, session_id: str, message: ChatMessage) -> None:
        raise NotImplementedError


class EpisodicMemoryService(ABC):
    @abstractmethod
    async def get_memory(self, user_id: str) -> EpisodicMemoryItem | None:
        raise NotImplementedError

    @abstractmethod
    async def upsert_memory(self, user_id: str, memory: str) -> EpisodicMemoryItem:
        raise NotImplementedError


class SearchService(ABC):
    @abstractmethod
    async def retrieve(self, query: str) -> List[SearchResultChunk]:
        raise NotImplementedError


class ChatCompletionService(ABC):
    @abstractmethod
    async def stream_complete(self, prompt: str) -> AsyncIterator[str]:
        raise NotImplementedError


class PromptBuilder(ABC):
    @abstractmethod
    def build_prompt(
        self,
        system_prompt: str,
        episodic_memory: str | None,
        session_history: List[ChatMessage],
        retrieved_context: List[SearchResultChunk],
        user_question: str,
    ) -> str:
        raise NotImplementedError
