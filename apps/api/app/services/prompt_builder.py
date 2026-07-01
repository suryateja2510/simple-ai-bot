from __future__ import annotations

from typing import List

from app.models.domain import ChatMessage, SearchResultChunk
from app.services.interfaces import PromptBuilder


class SimplePromptBuilder(PromptBuilder):
    def build_prompt(
        self,
        system_prompt: str,
        episodic_memory: str | None,
        session_history: List[ChatMessage],
        retrieved_context: List[SearchResultChunk],
        user_question: str,
    ) -> str:
        sections: List[str] = [system_prompt]

        if episodic_memory:
            sections.append("Episodic memory:\n" + episodic_memory)

        if session_history:
            history = "\n".join(
                f"{message.role}: {message.content}" for message in session_history[-10:]
            )
            sections.append("Session history:\n" + history)

        if retrieved_context:
            context = "\n".join(
                f"[{chunk.source}] {chunk.content}" for chunk in retrieved_context
            )
            sections.append("Retrieved context:\n" + context)

        sections.append("User question:\n" + user_question)
        return "\n\n".join(sections)
