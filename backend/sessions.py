"""sessions.py — remember pending clarifications per session (in memory).

NOTE: lives in RAM → lost on restart and one copy per server process;
fine for development (a shared store is a Phase 5 upgrade)."""
pending = {}  # session_id -> {"original_question": ..., "options": [...]}


def save(session_id, clarification):
    """Remember the pending clarification for a session."""
    pending[session_id] = clarification


def get(session_id):
    """Return the pending clarification, or None if there is none."""
    return pending.get(session_id)


def clear(session_id):
    """Forget the pending clarification (after the user answers)."""
    pending.pop(session_id, None)