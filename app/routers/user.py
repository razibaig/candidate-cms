from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.models import UserModel
from app.auth import get_password_hash, verify_password, create_access_token
from app.utils import validate_password
from motor.motor_asyncio import AsyncIOMotorClient
import os

router = APIRouter()

client = AsyncIOMotorClient(os.getenv("MONGODB_URI"))
db = client["candidate_management"]


@router.post("/user")
async def create_user(user: UserModel):
    """Create a new user.

    Validates the password complexity and checks for existing users
    before creating a new user in the database.

    Args:
        user (UserModel): The user data to be created.

    Returns:
        dict: A message indicating successful user creation.
    """
    # Validate password complexity
    if not validate_password(user.password):
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters long and include numbers and special characters",
        )

    # Increment the user id
    counter = await db["counters"].find_one_and_update(
        {"_id": "user_id"},
        {"$inc": {"sequence_value": 1}},
        upsert=True,
        return_document=True,
    )
    user_id = counter["sequence_value"]

    existing_user = await db["users"].find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user.password)
    user_data = user.model_dump()
    user_data["password"] = hashed_password
    user_data["_id"] = user_id  # Set the auto-incremented id

    await db["users"].insert_one(user_data)
    return {"message": "User created successfully"}


# The /token endpoint for user login
@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login and generate a JWT access token.

    Args:
        form_data (OAuth2PasswordRequestForm): The form data containing username and password.

    Returns:
        dict: The access token and token type.

    Raises:
        HTTPException: If the email or password is incorrect.
    """
    # Find the user by email (username in form_data)
    user = await db["users"].find_one({"email": form_data.username})
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    # Create JWT access token
    access_token = create_access_token(data={"sub": user["email"]})
    return {"access_token": access_token, "token_type": "bearer"}
