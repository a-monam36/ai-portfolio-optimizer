from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()



class ChatRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=2000, description="The user input to scan")

class FirewallResponse(BaseModel):
    prompt: str
    prompt_received: str
    is_safe: bool

class SafetyVerdict(BaseModel):
    is_safe: bool
    category: str





@app.post("/v1/chat")
async def handle_chat( data: ChatRequest):
    user_text = data.prompt



@app.get("/")

async def root():
    return {"message": "Hello world"}



@app.post("/v1/check")

async def check_prompt():
    return {"status": "received"}





