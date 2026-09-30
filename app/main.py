from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import navigation, locations, health, places, chat

app = FastAPI(
    title="CU Campus Navigation AI",
    description="AI-powered indoor/outdoor campus navigation engine for Chandigarh University",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["Health"])
app.include_router(locations.router, tags=["Locations"])
app.include_router(navigation.router, prefix="/navigation", tags=["Navigation"])
app.include_router(places.router, prefix="/places", tags=["Places"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])

@app.get("/", include_in_schema=False)
def root():
    return {"status": "online", "message": "CU Campus Navigation AI API is running. Send POST requests to /chat/ to interact."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

