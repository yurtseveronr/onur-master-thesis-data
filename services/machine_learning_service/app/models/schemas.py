from pydantic import BaseModel, Field
from typing import List, Optional

class RecommendationRequest(BaseModel):
    user_id: str = Field(..., min_length=1, description="User ID")
    num_results: int = Field(default=10, ge=1, le=100, description="Number of recommendations")

class EventRequest(BaseModel):
    user_id: str = Field(..., min_length=1, description="User ID")
    item_id: str = Field(..., min_length=1, description="Item ID")
    event_type: str = Field(default="VIEW", description="Event type (VIEW, LIKE, etc.)")

class RecommendationItem(BaseModel):
    item_id: str
    score: float

class RecommendationResponse(BaseModel):
    success: bool
    data: List[RecommendationItem]
    count: int
    message: Optional[str] = None

class EventResponse(BaseModel):
    success: bool
    message: str
    event_id: Optional[str] = None

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    detail: Optional[str] = None