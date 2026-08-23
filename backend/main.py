from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.presentation.api.v1.chats_router import router as chats_router
from app.presentation.api.v1.generate_router import router as generate_router
from app.presentation.api.v1.payments_router import router as payments_router

load_dotenv()

app = FastAPI(title="Jemini Chatbot API (Clean Architecture)", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chats_router)
app.include_router(generate_router)
app.include_router(payments_router)


@app.get("/")
def read_root():
    return {"message": "Jemini Chatbot API is running with Clean Architecture", "status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
