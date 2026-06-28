"""
Conversations module - multi-turn persistent chats and history (S5-M4).
"""

from app.modules.conversations.models import Conversation, Message
from app.modules.conversations.repository import ConversationRepository
from app.modules.conversations.service import ConversationService
from app.modules.conversations.exceptions import ConversationException, ConversationNotFoundException
from app.modules.conversations.router import router

__all__ = [
    "Conversation",
    "Message",
    "ConversationRepository",
    "ConversationService",
    "ConversationException",
    "ConversationNotFoundException",
    "router",
]
