from pydantic import BaseModel, Field


class UserRequest(BaseModel):
    """Minimal schema for validating incoming user input."""

    message: str = Field(min_length=2, max_length=300, description="The user's prompt or message.")


