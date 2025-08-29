from fastapi import APIRouter, HTTPException
from app.services.personalize_service import PersonalizeService
from app.models.schemas import (
    RecommendationRequest,
    EventRequest,
    RecommendationResponse,
    EventResponse,
    ErrorResponse
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
personalize_service = PersonalizeService()

@router.post(
    "/get-recommendation/",
    response_model=RecommendationResponse,
    summary="Get movie recommendations",
    description="Get personalized movie recommendations for a user"
)
async def get_movies_recommendation(request: RecommendationRequest):
    try:
        recommendations = await personalize_service.get_recommendations(
            content_type='movies',
            user_id=request.user_id,
            num_results=request.num_results
        )
        
        return RecommendationResponse(
            success=True,
            data=recommendations,
            count=len(recommendations),
            message=f"Successfully retrieved {len(recommendations)} movie recommendations"
        )
    except Exception as e:
        logger.error(f"Movies recommendation error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="Error retrieving movie recommendations",
                detail=str(e)
            ).dict()
        )

@router.get(
    "/recommendations/",
    response_model=RecommendationResponse,
    summary="Get movie recommendations (GET)",
    description="Get personalized movie recommendations for a user via GET"
)
async def get_movies_recommendations_get(user_id: str = "yurtseveronr@gmail.com", num_results: int = 5):
    try:
        recommendations = await personalize_service.get_recommendations(
            content_type='movies',
            user_id=user_id,
            num_results=num_results
        )
        
        return RecommendationResponse(
            success=True,
            data=recommendations,
            count=len(recommendations),
            message=f"Successfully retrieved {len(recommendations)} movie recommendations"
        )
    except Exception as e:
        logger.error(f"Movies recommendation error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="Error retrieving movie recommendations",
                detail=str(e)
            ).dict()
        )

@router.post(
    "/create-event/",
    response_model=EventResponse,
    summary="Create movie interaction event",
    description="Record user interaction with a movie (VIEW, LIKE, etc.)"
)
async def create_movie_event(request: EventRequest):
    try:
        event_id = await personalize_service.create_event(
            content_type='movies',
            user_id=request.user_id,
            item_id=request.item_id,
            event_type=request.event_type
        )
        
        return EventResponse(
            success=True,
            message=f"Movie interaction event successfully recorded: {request.event_type}",
            event_id=event_id
        )
    except Exception as e:
        logger.error(f"Movies event error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="Error recording movie interaction event",
                detail=str(e)
            ).dict()
        )
