import os
from typing import Optional
from dotenv import load_dotenv

from app.domain.repositories import (
    IChatRepository,
    IMessageRepository,
    IPaymentRepository,
    ISubscriptionRepository
)
from app.domain.services import ILLMService, IPaymentGatewayService
from app.infrastructure.persistence.supabase_repo import (
    SupabaseChatRepository,
    SupabaseMessageRepository,
    SupabasePaymentRepository,
    SupabaseSubscriptionRepository
)
from app.infrastructure.external.gemini_service import GeminiLLMService, SimulatedGeminiService
from app.infrastructure.external.toss_payment_service import TossPaymentGatewayService
from app.infrastructure.security.cipher import AES256GCMCipher
from app.usecases.chat_usecases import ListChatsUseCase, CreateChatUseCase, DeleteChatUseCase, GetMessagesUseCase
from app.usecases.generate_usecase import GenerateResponseUseCase
from app.usecases.payment_usecases import ConfirmPaymentUseCase, GetUserSubscriptionUseCase

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
SUPABASE_KEY = os.getenv("SUPABASE_SECRET_KEY", "").strip() or os.getenv("SUPABASE_KEY", "").strip()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip() or os.getenv("GOOGLE_API_KEY", "").strip()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "").strip()
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").strip()
TOSS_SECRET_KEY = os.getenv("TOSS_SECRET_KEY", "").strip()
CHAT_ENCRYPTION_KEY = os.getenv("CHAT_ENCRYPTION_KEY", "").strip()

_supabase_client = None
_cipher: Optional[AES256GCMCipher] = None
_llm_service: Optional[ILLMService] = None
_payment_gateway_service: Optional[IPaymentGatewayService] = None

def get_supabase_client():
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client

    if not SUPABASE_URL or not SUPABASE_KEY or "your-supabase-project" in SUPABASE_URL:
        raise RuntimeError("Supabase credentials not configured. Please set SUPABASE_URL and SUPABASE_KEY in .env")

    try:
        from supabase import create_client
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("Connected to Supabase successfully in Clean Architecture.")
        return _supabase_client
    except Exception as e:
        print(f"Failed to initialize Supabase client: {e}")
        raise RuntimeError(f"Failed to connect to Supabase: {e}")

def get_cipher() -> AES256GCMCipher:
    global _cipher
    if _cipher is not None:
        return _cipher
    
    if not CHAT_ENCRYPTION_KEY or "your-32byte" in CHAT_ENCRYPTION_KEY:
        raise RuntimeError("CHAT_ENCRYPTION_KEY must be set in .env for encryption")
        
    _cipher = AES256GCMCipher(CHAT_ENCRYPTION_KEY)
    return _cipher

def get_chat_repository() -> IChatRepository:
    client = get_supabase_client()
    return SupabaseChatRepository(client, get_cipher())

def get_message_repository() -> IMessageRepository:
    client = get_supabase_client()
    return SupabaseMessageRepository(client, get_cipher())

def get_payment_repository() -> IPaymentRepository:
    client = get_supabase_client()
    return SupabasePaymentRepository(client)

def get_subscription_repository() -> ISubscriptionRepository:
    client = get_supabase_client()
    return SupabaseSubscriptionRepository(client)

def get_payment_gateway_service() -> IPaymentGatewayService:
    global _payment_gateway_service
    if _payment_gateway_service is not None:
        return _payment_gateway_service
    _payment_gateway_service = TossPaymentGatewayService(TOSS_SECRET_KEY or None)
    return _payment_gateway_service

def get_llm_service() -> ILLMService:
    global _llm_service
    if _llm_service is not None:
        return _llm_service

    try:
        from app.infrastructure.external.langchain_service import LangChainMultiVendorService
        _llm_service = LangChainMultiVendorService(
            google_api_key=GEMINI_API_KEY,
            openai_api_key=OPENAI_API_KEY,
            anthropic_api_key=ANTHROPIC_API_KEY,
            ollama_base_url=OLLAMA_BASE_URL,
        )
        return _llm_service
    except Exception as e:
        print(f"Failed to initialize LangChainMultiVendorService: {e}")

    _llm_service = SimulatedGeminiService()
    return _llm_service

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
        get_llm_service(),
        get_subscription_repository()
    )

def get_confirm_payment_usecase() -> ConfirmPaymentUseCase:
    return ConfirmPaymentUseCase(
        get_payment_repository(),
        get_subscription_repository(),
        get_payment_gateway_service()
    )

def get_get_user_subscription_usecase() -> GetUserSubscriptionUseCase:
    return GetUserSubscriptionUseCase(get_subscription_repository())

from fastapi import Header

async def get_current_user_id(authorization: Optional[str] = Header(None)) -> Optional[str]:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.split("Bearer ", 1)[1].strip()
    if not token:
        return None
    try:
        client = get_supabase_client()
        user_res = client.auth.get_user(token)
        if user_res and getattr(user_res, "user", None):
            return user_res.user.id
    except Exception:
        return None
    return None


