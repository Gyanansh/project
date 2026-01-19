from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import repo, analysis

app = FastAPI(title="RepoMaster AI API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(repo.router)
app.include_router(analysis.router)

@app.get("/")
async def root():
    return {"message": "Welcome to RepoMaster AI Backend"}
