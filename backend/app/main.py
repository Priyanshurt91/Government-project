from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import services, documents
from app.routes import voice   
from app.routes import submit  

app = FastAPI(
    title="Seva Form AI",
    description="AI-powered Seva Kendra Form Filling Assistant"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(services.router)
app.include_router(documents.router)
app.include_router(voice.router)   
app.include_router(submit.router)  

@app.get("/")
def root():
    return {"status": "running", "message": "Seva Form AI backend is live"}
