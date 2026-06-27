"""
AI Conversation Context building and window trimming helpers (S5-M4).
"""

from __future__ import annotations

from typing import Any


def build_conversation_context(
    messages: list[Any],
    max_messages: int = 10,
) -> list[dict[str, str]]:
    """
    Format and trim past conversation messages to fit LLM context limits.

    Always selects the most recent `max_messages` to preserve the latest
    turns in the chat session.

    Args:
        messages: A list of Message ORM model instances.
        max_messages: Maximum number of recent messages to retain.

    Returns:
        A list of dictionaries containing keys 'role' and 'content'.
    """
    # Select the most recent messages
    recent_messages = messages[-max_messages:] if len(messages) > max_messages else messages

    context_list = []
    for msg in recent_messages:
        context_list.append({
            "role": msg.role,
            "content": msg.content,
        })

    return context_list
