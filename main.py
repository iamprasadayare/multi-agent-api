from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn
from agent import process_request

app = FastAPI(title="PRS-AgenticSynergy API")

class ChatRequest(BaseModel):
    message: str

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    with open("index.html", "r") as f:
        return f.read()

@app.post("/chat")
async def chat(request: ChatRequest):
    response_text = await process_request(request.message)
    return {"response": response_text}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
