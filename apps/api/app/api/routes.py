from __future__ import annotations

import asyncio
import time
from collections import deque
from typing import AsyncIterator

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse, StreamingResponse

from app.models.domain import ChatMessage
from app.schemas.chat import ChatRequest
from app.schemas.session import (
    ChatMessageDto,
    EpisodicMemoryRequest,
    EpisodicMemoryResponse,
    SessionCreateResponse,
    SessionDetail,
    SessionSummary,
)
from app.services.dependencies import ServiceContainer

router = APIRouter(prefix="", tags=["chat"])

RATE_LIMIT_WINDOW_SECONDS = 6
RATE_LIMIT_MAX_REQUESTS = 3


def get_container(request: Request) -> ServiceContainer:
    return request.app.state.container


def _get_client_key(request: Request) -> str:
    if request.client and request.client.host:
        return request.client.host
    forwarded_for = request.headers.get("x-forwarded-for", "")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return "unknown"


def _record_request(request: Request) -> bool:
    client_key = _get_client_key(request)
    now = time.time()
    rate_history = request.app.state.client_rate_limit_history
    history = rate_history.setdefault(client_key, deque())
    while history and now - history[0] > RATE_LIMIT_WINDOW_SECONDS:
        history.popleft()
    if len(history) >= RATE_LIMIT_MAX_REQUESTS:
        return False
    history.append(now)
    return True


def create_system_prompt() -> str:
    return (
        "You are a helpful AI chatbot. Answer clearly and keep the response friendly. "
        "Use only the information available in the retrieved context and session history."
    )


@router.get("/", include_in_schema=False)
async def root() -> RedirectResponse:
    return RedirectResponse(url="/docs")


@router.post("/sessions", response_model=SessionCreateResponse)
async def create_session(container: ServiceContainer = Depends(get_container)) -> SessionCreateResponse:
    user_id = await container.auth.get_current_user()
    session = await container.session_memory.create_session(user_id=user_id, title="New chat session")
    return SessionCreateResponse(session_id=session.id)


@router.get("/sessions", response_model=list[SessionSummary])
async def list_sessions(container: ServiceContainer = Depends(get_container)) -> list[SessionSummary]:
    user_id = await container.auth.get_current_user()
    sessions = await container.session_memory.list_sessions(user_id=user_id)
    return [
        SessionSummary(session_id=session.id, title=session.title, created_at=session.created_at)
        for session in sessions
    ]


@router.get("/sessions/{session_id}", response_model=SessionDetail)
async def get_session(session_id: str, container: ServiceContainer = Depends(get_container)) -> SessionDetail:
    session = await container.session_memory.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionDetail(
        session_id=session.id,
        title=session.title,
        messages=[
            ChatMessageDto(role=message.role, content=message.content, created_at=message.created_at)
            for message in session.messages
        ],
        created_at=session.created_at,
    )


@router.get("/memory/episodic", response_model=EpisodicMemoryResponse | None)
async def get_episodic_memory(
    container: ServiceContainer = Depends(get_container),
) -> EpisodicMemoryResponse | None:
    user_id = await container.auth.get_current_user()
    memory = await container.episodic_memory.get_memory(user_id=user_id)
    if memory is None:
        return None
    return EpisodicMemoryResponse(
        user_id=memory.user_id,
        memory=memory.memory,
        created_at=memory.created_at,
    )


@router.put("/memory/episodic", response_model=EpisodicMemoryResponse)
async def upsert_episodic_memory(
    request: EpisodicMemoryRequest,
    container: ServiceContainer = Depends(get_container),
) -> EpisodicMemoryResponse:
    user_id = await container.auth.get_current_user()
    memory = await container.episodic_memory.upsert_memory(user_id=user_id, memory=request.memory)
    return EpisodicMemoryResponse(
        user_id=memory.user_id,
        memory=memory.memory,
        created_at=memory.created_at,
    )


@router.post("/chat/stream")
async def stream_chat(
    chat_request: ChatRequest,
    request: Request,
    container: ServiceContainer = Depends(get_container),
) -> StreamingResponse:
    if not _record_request(request):
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please wait a moment before retrying.",
        )

    session = await container.session_memory.get_session(chat_request.session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    user_id = await container.auth.get_current_user()
    episodic_item = await container.episodic_memory.get_memory(user_id=user_id)
    retrieved_context = await container.search.retrieve(chat_request.user_input)

    prompt = container.prompt_builder.build_prompt(
        system_prompt=create_system_prompt(),
        episodic_memory=episodic_item.memory if episodic_item else None,
        session_history=session.messages,
        retrieved_context=retrieved_context,
        user_question=chat_request.user_input,
    )

    async def event_stream() -> AsyncIterator[bytes]:
        assistant_text = ""
        await container.session_memory.add_message(
            chat_request.session_id,
            ChatMessage(role="user", content=chat_request.user_input),
        )

        async for token in container.chat_completion.stream_complete(prompt):
            assistant_text += token
            yield token.encode("utf-8")

        await container.session_memory.add_message(
            chat_request.session_id,
            ChatMessage(role="assistant", content=assistant_text.strip()),
        )

    session_locks = request.app.state.chat_stream_locks
    lock = session_locks.setdefault(chat_request.session_id, asyncio.Lock())
    if lock.locked():
        raise HTTPException(
            status_code=429,
            detail="A chat request is already in progress for this session.",
        )

    async with lock:
        return StreamingResponse(event_stream(), media_type="text/plain")
