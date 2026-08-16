# Legacy database.py - Replaced by Clean Architecture Infrastructure Repositories
# See app/infrastructure/persistence/in_memory_repo.py and app/infrastructure/persistence/supabase_repo.py

from app.presentation.dependencies import get_chat_repository, get_message_repository

__all__ = ["get_chat_repository", "get_message_repository"]
