from celery import Celery
import os
import csv
import io
from fastapi.responses import StreamingResponse
from motor.motor_asyncio import AsyncIOMotorClient

# Initialize MongoDB client
client = AsyncIOMotorClient(os.getenv("MONGODB_URI"))
db = client["candidate_management"]

celery_app = Celery("tasks", broker=os.getenv("CELERY_BROKER_URL"))


@celery_app.task
def generate_csv_report():
    """Generate a CSV report from MongoDB data.

    Returns:
        StreamingResponse: A CSV file containing the report.
    """
    # Logic to generate CSV report from MongoDB
    loop = asyncio.get_event_loop()
    candidates_cursor = loop.run_until_complete(db["candidates"].find().to_list(None))

    # Create an in-memory file-like object
    output = io.StringIO()
    writer = csv.writer(output)

    # Write the CSV header
    writer.writerow(["ID", "Name", "Experience", "Skills"])

    # Fetch each candidate and write it to the CSV file
    for candidate in candidates_cursor:
        writer.writerow(
            [
                str(candidate["_id"]),
                candidate["name"],
                candidate["experience"],
                ",".join(candidate["skills"]),  # Combine skills into a single comma-separated string
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
