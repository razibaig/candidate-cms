from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic models."""
    
    @classmethod
    def __get_validators__(cls):
        """Yield the validator for ObjectId.
        """
        yield cls.validate

    @classmethod
    def validate(cls, v):
        """Validate the ObjectId.

            Args:
                v: The value to validate.

            Returns:
                ObjectId: The validated ObjectId.

            Raises:
                ValueError: If the ObjectId is invalid.
        """
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid object id")
        return ObjectId(v)


class UserModel(BaseModel):
    """Data model for user information.

    Attributes:
        id (Optional[int]): The user ID.
        username (str): The username of the user.
        email (EmailStr): The email of the user.
        password (str): The password of the user.
    """
    id: Optional[int] = Field(default=None, alias="_id")
    username: str
    email: EmailStr
    password: str

    class Config:
        """Pydantic configuration for UserModel."""
        populate_by_name = True
        json_encoders = {ObjectId: str}


class CandidateModel(BaseModel):
    """Data model for candidate information.

    Attributes:
        id (Optional[int]): The candidate ID.
        name (str): The name of the candidate.
        experience (int): The experience of the candidate in years.
        skills (list[str]): The skills of the candidate.
    """
    id: Optional[int] = Field(default=None, alias="_id")
    name: str
    experience: int
    skills: list[str]

    class Config:
        """Pydantic configuration for CandidateModel."""
        populate_by_name = True
        json_encoders = {ObjectId: str}
