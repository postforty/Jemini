import os
from typing import Optional
from dotenv import load_dotenv

from app.domain.repositories import IChatRepository, IMessageRepository
from app.domain.services import ILLMService
from app.infrastructure.persistence.in_memory_repo import InMemoryChatRepository, InMemoryMessageRepository
from app.infrastructure.persistence.supabase_repo import SupabaseChatRepository, SupabaseMessageRepository
from app.infrastructure.external.gemini_service import SimulatedGeminiService
from app.usecases.chat_usecases import ListChatsUseCase, CreateChatUseCase, DeleteChatUseCase, GetMessagesUseCase
from app.usecases.generate_usecase import GenerateResponseUseCase

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "").strip()

# Global instances for In-Memory Fallback
_in_memory_chat_repo: Optional[InMemoryChatRepository] = None
_in_memory_message_repo: Optional[InMemoryMessageRepository] = None
_supabase_client = None

is_valid_supabase = (
    SUPABASE_URL 
    and SUPABASE_KEY 
    and "your-supabase-project" not in SUPABASE_URL 
    and "your-supabase-anon-key" not in SUPABASE_KEY
)

if is_valid_supabase:
    try:
        from supabase import create_client
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("Connected to Supabase successfully in Clean Architecture.")
    except Exception as e:
        print(f"Failed to initialize Supabase client: {e}")


def get_chat_repository() -> IChatRepository:
    global _in_memory_chat_repo
    if _supabase_client:
        return SupabaseChatRepository(_supabase_client)
    if _in_memory_chat_repo is None:
        _in_memory_chat_repo = InMemoryChatRepository()
    return _in_memory_chat_repo

def get_message_repository() -> IMessageRepository:
    global _in_memory_message_repo
    if _supabase_client:
        return SupabaseMessageRepository(_supabase_client)
    if _in_memory_message_repo is None:
        _in_memory_message_repo = InMemoryMessageRepository()
    return _in_memory_message_repo

def get_llm_service() -> ILLMService:
    return SimulatedGeminiService()

def get_list_chats_usecase() -> ListChatsUseCase:
    return ListChatsUseCase(get_chat_repository())

def get_create_chat_usecase() -> CreateChatUseCase:
    return CreateChatUseCase(get_chat_repository())

def get_delete_chat_usecase() -> DeleteChatUseCase:
    return DeleteChatUseCase(get_chat_repository(), get_message_repository())

def get_get_messages_usecase() -> GetMessagesUseCase:
    return GetMessagesUseCase(get_message_repository())

def get_generate_response_usecase() -> GenerateResponseUseCase:
    return GenerateResponseUseCase(
        get_chat_repository(),
        get_message_repository(),
        get_llm_service()
    )
