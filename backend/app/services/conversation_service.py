"""
Conversation Session Service.
In-memory session state management for patient chat sessions.
Conforms strictly to state machine requirements.
"""

from __future__ import annotations

import uuid
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.clinical.conversation_state import ConversationStage, create_initial_state_dict

logger = logging.getLogger(__name__)

_SESSIONS: Dict[str, Dict[str, Any]] = {}


def create_session() -> Dict[str, Any]:
    """Create and register a new chat session with INITIAL_COMPLAINT stage."""
    session_id = str(uuid.uuid4())
    state_dict = create_initial_state_dict(session_id)
    _SESSIONS[session_id] = state_dict
    logger.info("Created new chat session in INITIAL_COMPLAINT stage: %s", session_id)
    return state_dict


def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve session by session_id."""
    return _SESSIONS.get(session_id)


def update_session(session_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Update session state fields."""
    if session_id in _SESSIONS:
        data["updated_at"] = datetime.utcnow().isoformat()
        _SESSIONS[session_id].update(data)
        return _SESSIONS[session_id]
    return None


def add_message(session_id: str, role: str, content: str) -> None:
    """Append a message to the session history."""
    sess = get_session(session_id)
    if sess:
        sess.setdefault("messages", []).append({
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        })
        sess["updated_at"] = datetime.utcnow().isoformat()


def clear_sessions() -> None:
    """Clear all active sessions (for testing purposes)."""
    _SESSIONS.clear()
