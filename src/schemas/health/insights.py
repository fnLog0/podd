"""Pydantic schemas for Health Insights and Recommendations API requests and responses."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class HealthInsightResponse(BaseModel):
    """Schema for health insights response."""

    id: str = Field(..., description="Insight ID")
    user_id: str = Field(..., description="User ID for whom insights are generated")
    insight_type: str = Field(..., description="Type of insight (e.g., 'vitals', 'medication', 'overall')")
    insight: str = Field(..., description="Detailed insight text")
    recommendation: str = Field(..., description="Actionable recommendation based on insight")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0-1)")
    created_at: datetime = Field(..., description="Timestamp when insight was generated")
    data_points_analyzed: int = Field(
        default=0, description="Number of data points analyzed"
    )
    context: Optional[dict] = Field(None, description="Additional context data")


class RecommendationItem(BaseModel):
    """Schema for a single health recommendation."""

    category: str = Field(..., description="Category (e.g., 'diet', 'exercise', 'medication')")
    title: str = Field(..., description="Recommendation title")
    description: str = Field(..., description="Detailed recommendation description")
    priority: str = Field(..., description="Priority level: low, medium, high, urgent")
    actionable: bool = Field(..., description="Whether the recommendation is actionable")
    estimated_impact: Optional[str] = Field(None, description="Description of expected impact")


class HealthRecommendationsResponse(BaseModel):
    """Schema for health recommendations response."""

    id: str = Field(..., description="Recommendations session ID")
    user_id: str = Field(..., description="User ID for whom recommendations are generated")
    recommendations: list[RecommendationItem] = Field(
        default_factory=list, description="List of health recommendations"
    )
    summary: str = Field(..., description="Overall summary of recommendations")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Overall confidence score")
    created_at: datetime = Field(..., description="Timestamp when recommendations were generated")
    data_points_analyzed: int = Field(
        default=0, description="Number of data points analyzed"
    )


class RecommendationQueryParams(BaseModel):
    """Schema for recommendation query parameters."""

    categories: Optional[list[str]] = Field(
        None, description="Filter by recommendation categories"
    )
    priority_min: Optional[str] = Field(
        None, description="Minimum priority level (low, medium, high, urgent)"
    )
    include_actionable_only: bool = Field(
        default=False, description="Only return actionable recommendations"
    )
