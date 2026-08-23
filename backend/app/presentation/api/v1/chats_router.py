from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from app.presentation.schemas import ChatCreate, ChatResponse, MessageResponse
from app.presentation.dependencies import (
    get_list_chats_usecase,
    get_create_chat_usecase,
    get_delete_chat_usecase,
    get_get_messages_usecase,
    get_current_user_id
)
from app.usecases.chat_usecases import (
    ListChatsUseCase,
    CreateChatUseCase,
    DeleteChatUseCase,
    GetMessagesUseCase
)

router = APIRouter(prefix="/api/chats", tags=["Chats"])

@router.get("", response_model=List[ChatResponse])
async def list_chats(
    usecase: ListChatsUseCase = Depends(get_list_chats_usecase),
    user_id: Optional[str] = Depends(get_current_user_id)
):
    chats = await usecase.execute(user_id=user_id)
    return [
        ChatResponse(
            id=c.id,
            title=c.title,
            model=c.model,
            created_at=c.created_at,
            updated_at=c.updated_at
        )
        for c in chats
    ]

@router.post("", response_model=ChatResponse)
async def create_chat(
    chat_req: ChatCreate,
    usecase: CreateChatUseCase = Depends(get_create_chat_usecase),
    user_id: Optional[str] = Depends(get_current_user_id)
):
    chat = await usecase.execute(title=chat_req.title, model=chat_req.model, user_id=user_id)
    return ChatResponse(
        id=chat.id,
        title=chat.title,
        model=chat.model,
        created_at=chat.created_at,
        updated_at=chat.updated_at
    )

@router.delete("/{chat_id}")
async def delete_chat(
    chat_id: str,
    usecase: DeleteChatUseCase = Depends(get_delete_chat_usecase),
    user_id: Optional[str] = Depends(get_current_user_id)
):
    success = await usecase.execute(chat_id, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Chat not found or unauthorized")
    return {"message": "Chat deleted successfully", "id": chat_id}

@router.get("/{chat_id}/messages", response_model=List[MessageResponse])
async def list_messages(
    chat_id: str,
    usecase: GetMessagesUseCase = Depends(get_get_messages_usecase)
):
    messages = await usecase.execute(chat_id)
    return [
        MessageResponse(
            id=m.id,
            chat_id=m.chat_id,
            sender=m.sender,
            content=m.content,
            image_url=m.image_url,
            created_at=m.created_at
        )
        for m in messages
    ]
