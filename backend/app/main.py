from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.api.v1.endpoints import router as api_v1_router

# Initialize the industrial-grade API application
app = FastAPI(
    title="Delta AS228 Automation Compiler Engine",
    version="1.0.0",
    description="Production-ready engine for deterministic ladder logic compilation."
)

# CORS Policy configuration for secure internal communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Integrating the modularized API endpoints
app.include_router(api_v1_router, prefix="/api/v1")

@app.get("/")
def health_check():
    """System health check endpoint for monitoring production state"""
    return {
        "status": "online",
        "service": "Delta AS228 Automation Compiler Engine",
        "engine_version": "IEC-61131-3-V1"
    }

# File execution entry point
if __name__ == "__main__":
    # Production-ready entry point (app.main target for app package structure)
    uvicorn.run("app.main:app", host="127.0.0.1", port=8001, reload=True)