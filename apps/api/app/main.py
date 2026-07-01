import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.config.settings import AppSettings
from app.services.dependencies import build_service_container


def create_app() -> FastAPI:
    settings = AppSettings()
    container = build_service_container(settings)

    app = FastAPI(
        title="Simple RAG Bot",
        version="0.1.0",
        description="RAG chatbot backend with session memory, episodic memory, and Azure AI Foundry-ready adapters.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.state.container = container
    app.state.chat_stream_locks = {}
    app.state.client_rate_limit_history = {}
    app.include_router(router)
    return app


app = create_app()
