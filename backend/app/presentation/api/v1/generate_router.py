from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from app.presentation.schemas import GenerateRequest
from app.presentation.dependencies import get_generate_response_usecase
from app.usecases.generate_usecase import GenerateResponseUseCase

router = APIRouter(prefix="/api/generate", tags=["Generate"])

@router.post("")
async def generate_response(
    req: GenerateRequest,
    usecase: GenerateResponseUseCase = Depends(get_generate_response_usecase)
):
    generator = usecase.execute(
        prompt=req.prompt,
        chat_id=req.chat_id,
        model=req.model,
        image_url=req.image_url
    )
    return StreamingResponse(generator, media_type="text/event-stream")
