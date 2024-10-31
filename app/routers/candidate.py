from fastapi import APIRouter, HTTPException, Depends
from app.models import CandidateModel
from app.auth import get_current_user
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId, errors
import os

from fastapi.responses import StreamingResponse
import io
import csv

router = APIRouter()

client = AsyncIOMotorClient(os.getenv("MONGODB_URI"))
db = client["candidate_management"]


@router.post("/candidates", response_model=CandidateModel)
async def create_candidate(
    candidate: CandidateModel, current_user: dict = Depends(get_current_user)
):
    """Create a new candidate.
    
    Args:
        candidate (Candidate): The candidate data to be created.
    
    Returns:
        Candidate: The created candidate.
    """
    # Increment the candidate id
    counter = await db["counters"].find_one_and_update(
        {"_id": "candidate_id"},
        {"$inc": {"sequence_value": 1}},
        upsert=True,
        return_document=True,
    )
    candidate_id = counter["sequence_value"]
    print(f"Generated candidate ID: {candidate_id}")

    candidate_data = candidate.model_dump()
    candidate_data["_id"] = candidate_id  # Set the auto-incremented id

    await db["candidates"].insert_one(candidate_data)
    return candidate_data


@router.get("/candidates/{id}", response_model=CandidateModel)
async def get_candidate(id: int, current_user: dict = Depends(get_current_user)):
    """Retrieve a candidate by ID.

    Args:
        id (int): The ID of the candidate to retrieve.

    Returns:
        Candidate: The retrieved candidate.
    """
    candidate = await db["candidates"].find_one({"_id": id})
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate


@router.get("/all-candidates")
async def get_all_candidates(
    skip: int = 0,
    limit: int = 10,
    search: str = "",
    current_user: dict = Depends(get_current_user),
):
    """Retrieve all candidates with optional search and pagination.

    Args:
        search (str, optional): Search term for filtering candidates.
        skip (int, optional): Number of records to skip for pagination.
        limit (int, optional): Maximum number of records to return.

    Returns:
        List[Candidate]: List of candidates.
    """
    # Implement search and pagination logic
    try:
        query = {}
        if search:
            # Create a regex query to search across all fields
            query = {
                "$or": [
                    {"name": {"$regex": search, "$options": "i"}},
                    {"experience": {"$regex": search, "$options": "i"}},
                    {"skills": {"$regex": search, "$options": "i"}},
                ]
            }

        candidates_cursor = db["candidates"].find(query).skip(skip).limit(limit)
        candidates = await candidates_cursor.to_list(length=limit)

        # Return an empty list if no candidates are found
        return candidates

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put("/candidates/{id}", response_model=CandidateModel)
async def update_candidate(
    id: int, candidate: CandidateModel, current_user: dict = Depends(get_current_user)
):
    """Update an existing candidate.

    Args:
        id (str): The ID of the candidate to update.
        candidate (Candidate): The updated candidate data.

    Returns:
        Candidate: The updated candidate.
    """
    candidate_data = candidate.dict(exclude_unset=True)
    result = await db["candidates"].update_one({"_id": id}, {"$set": candidate_data})

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Candidate not found")

    updated_candidate = await db["candidates"].find_one({"_id": id})
    return updated_candidate


@router.delete("/candidates/{id}", response_model=dict)
async def delete_candidate(id: int, current_user: dict = Depends(get_current_user)):
    """Delete a candidate by ID.

    Args:
        id (str): The ID of the candidate to delete.

    Returns:
        None
    """
    result = await db["candidates"].delete_one({"_id": id})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Candidate not found")

    return {"message": "Candidate deleted successfully"}


@router.get("/generate-report")
async def generate_report(current_user: dict = Depends(get_current_user)):
    """Initiate report generation.

    Returns:
        dict: Message indicating the report generation status.
    """
    # Logic to generate CSV report from MongoDB
    candidates_cursor = db["candidates"].find()

    # Create an in-memory file-like object
    output = io.StringIO()
    writer = csv.writer(output)

    # Write the CSV header
    writer.writerow(["ID", "Name", "Experience", "Skills"])

    # Fetch each candidate and write it to the CSV file
    async for candidate in candidates_cursor:
        writer.writerow(
            [
                str(candidate["_id"]),
                candidate["name"],
                candidate["experience"],
                ",".join(
                    candidate["skills"]
                ),  # Combine skills into a single comma-separated string
            ]
        )

    # Move the cursor to the start of the stream
    output.seek(0)

    # Create a StreamingResponse for CSV
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=candidates_report.csv"},
    )
