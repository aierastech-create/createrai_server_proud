import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from graph.builder import graph
from models.request import GenerateRequest, GenerateResponse
from db.mongo import save_history

# ─── Logging ─────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(levelname)s │ %(message)s",
)
logger = logging.getLogger(__name__)

# ─── FastAPI App ─────────────────────────────────────────
app = FastAPI(
    title="CreatorAI API",
    description="AI-powered YouTube content generation — Ideas, Titles, Scripts & SEO",
    version="1.0.0",
)

# ─── CORS (allow Flutter app to connect) ─────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Health Check ─────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok", "service": "CreatorAI API"}


# ─── Generate Endpoint ───────────────────────────────────
@app.post("/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest):
    logger.info(f"🚀 Generate request — feature={req.feature}, input='{req.input[:50]}...'")

    try:
        result = graph.invoke({
            "user_input": req.input,
            "feature": req.feature.value,
            "response": "",
        })

        output = result.get("response", "")

        # Save to history (non-blocking, graceful)
        save_history(
            user_id="anonymous",
            feature=req.feature.value,
            input_text=req.input,
            output=output,
        )

        return GenerateResponse(
            status="success",
            feature=req.feature.value,
            data=output,
        )

    except Exception as e:
        logger.error(f"❌ Generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─── Run with: uvicorn main:app --reload --port 8000 ────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)