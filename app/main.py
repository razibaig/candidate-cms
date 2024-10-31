from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from app.routers import user, candidate
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# MongoDB connection
client = AsyncIOMotorClient(os.getenv("MONGODB_URI"))
db = client["candidate_management"]

# Include routers
app.include_router(user.router)
app.include_router(candidate.router)


@app.get("/health")
async def health_check():
    """Check the health status of the API.

    Returns:
        dict: Status message indicating the API health.
    """
    return {"status": "API is healthy"}
