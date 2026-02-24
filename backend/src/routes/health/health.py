from datetime import date, datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Query

from src.auth.dependencies import get_current_user
from src.schemas.health import (
    FoodLogEventDefinition,
    FoodLogCreate,
    FoodLogResponse,
    HealthInsightResponse,
    HealthRecommendationsResponse,
    RecommendationItem,
    VitalsCreate,
    VitalsEventDefinition,
    VitalsResponse,
)
from src.services.locusgraph.service import locusgraph_service

router = APIRouter(
    prefix="/health", tags=["health"], dependencies=[Depends(get_current_user)]
)


def safe_parse_datetime(timestamp_str: str, fallback_timestamp: str | None = None) -> datetime:
    """Safely parse ISO format datetime string with fallback options.

    Args:
        timestamp_str: The ISO format string to parse
        fallback_timestamp: Optional fallback timestamp string to use if parsing fails

    Returns:
        Parsed datetime, or current time if all parsing fails
    """
    # Try to parse the timestamp string
    if timestamp_str:
        try:
            return datetime.fromisoformat(timestamp_str)
        except (ValueError, TypeError):
            pass

    # Try the fallback timestamp
    if fallback_timestamp:
        try:
            return datetime.fromisoformat(fallback_timestamp)
        except (ValueError, TypeError):
            pass

    # Fallback to current time
    return datetime.now(timezone.utc)



@router.get("/food/logs", response_model=list[FoodLogResponse])
async def get_food_logs(
    limit: int = Query(10, ge=1, le=100, description="Number of entries to return"),
    meal_type: Optional[str] = Query(None, description="Filter by meal type"),
    date: Optional[date] = Query(
        None, description="Filter by specific date (YYYY-MM-DD)"
    ),
    current_user=Depends(get_current_user),
):
    """Get food logs for the current user."""
    query_parts = ["food logs", f"user {current_user.id}"]
    if meal_type:
        query_parts.append(f"meal type {meal_type}")
    if date:
        query_parts.append(f"date {date.isoformat()}")

    memories = await locusgraph_service.retrieve_context(
        query=" ".join(query_parts),
        limit=limit,
    )

    food_logs = []
    for memory in memories:
        payload = memory.get("payload", {})
        if payload.get("user_id") == str(current_user.id):
            if meal_type and payload.get("meal_type") != meal_type:
                continue

            # Filter by date if specified
            if date:
                logged_at = safe_parse_datetime(
                    payload.get("logged_at"),
                    memory.get("timestamp")
                )
                if logged_at.date() != date:
                    continue

            meal_type = payload.get("meal_type", "other")
            valid_meal_types = ["breakfast", "lunch", "dinner", "snack", "other"]
            if meal_type not in valid_meal_types:
                meal_type = "other"

            food_logs.append(
                FoodLogResponse(
                    id=memory.get("id", ""),
                    user_id=payload.get("user_id", ""),
                    description=payload.get("description", ""),
                    calories=payload.get("calories"),
                    protein_g=payload.get("protein_g"),
                    carbs_g=payload.get("carbs_g"),
                    fat_g=payload.get("fat_g"),
                    meal_type=meal_type,
                    logged_at=safe_parse_datetime(
                        payload.get("logged_at"),
                        memory.get("timestamp")
                    ),
                    created_at=datetime.fromisoformat(memory.get("timestamp", "")),
                )
            )

    return food_logs


@router.post("/food/log", response_model=FoodLogResponse)
async def create_food_log(
    food_log_data: FoodLogCreate,
    related_to: Optional[str] = Query(
        None, description="Related event ID (e.g., vitals or medication)"
    ),
    current_user=Depends(get_current_user),
):
    """Log a food item or meal. Can be linked to other health events via related_to."""
    from src.schemas.events import EventKind

    food_log_id = locusgraph_service.new_id()
    context_id = FoodLogEventDefinition.get_context_id(food_log_id)

    logged_at = food_log_data.logged_at or datetime.now(timezone.utc)

    payload = FoodLogEventDefinition.create_payload(
        description=food_log_data.description,
        calories=food_log_data.calories,
        protein_g=food_log_data.protein_g,
        carbs_g=food_log_data.carbs_g,
        fat_g=food_log_data.fat_g,
        meal_type=food_log_data.meal_type,
        logged_at=logged_at,
        user_id=str(current_user.id),
    )

    stored = await locusgraph_service.store_event(
        event_kind=EventKind.FOOD_LOG_CREATE,
        context_id=context_id,
        payload=payload,
        related_to=[related_to] if related_to else None,
    )

    return FoodLogResponse(
        id=food_log_id,
        user_id=str(current_user.id),
        description=food_log_data.description,
        calories=food_log_data.calories,
        protein_g=food_log_data.protein_g,
        carbs_g=food_log_data.carbs_g,
        fat_g=food_log_data.fat_g,
        meal_type=food_log_data.meal_type,
        logged_at=logged_at,
        created_at=datetime.now(timezone.utc),
    )


@router.get("/vitals", response_model=list[VitalsResponse])
async def get_vitals(
    limit: int = Query(10, ge=1, le=100, description="Number of entries to return"),
    date_from: Optional[date] = Query(
        None, description="Filter from date (YYYY-MM-DD)"
    ),
    date_to: Optional[date] = Query(None, description="Filter to date (YYYY-MM-DD)"),
    current_user=Depends(get_current_user),
):
    """Get vitals history for the current user with optional date range filtering."""

    query_parts = [f"vitals user {current_user.id}"]
    if date_from:
        query_parts.append(f"from {date_from.isoformat()}")
    if date_to:
        query_parts.append(f"to {date_to.isoformat()}")

    query = " ".join(query_parts)
    print(f"DEBUG [HEALTH]: Querying vitals with: '{query}'")
    print(f"DEBUG [HEALTH]: Current user ID: {current_user.id}")

    memories = await locusgraph_service.retrieve_context(
        query=query,
        limit=limit,
    )
    print(f"DEBUG [HEALTH]: Retrieved {len(memories)} memories")

    vitals_entries = []
    for memory in memories:
        payload = memory.get("payload", {})
        print(f"DEBUG [HEALTH]: Memory payload user_id: {payload.get('user_id')}")
        if payload.get("user_id") == str(current_user.id):
            logged_at = safe_parse_datetime(
                payload.get("logged_at"),
                memory.get("timestamp")
            )

            # Filter by date range if specified
            if date_from and logged_at.date() < date_from:
                continue
            if date_to and logged_at.date() > date_to:
                continue

            vitals_entries.append(
                VitalsResponse(
                    id=memory.get("id", ""),
                    user_id=payload.get("user_id", ""),
                    blood_pressure_systolic=payload.get("blood_pressure_systolic"),
                    blood_pressure_diastolic=payload.get("blood_pressure_diastolic"),
                    heart_rate=payload.get("heart_rate"),
                    blood_sugar=payload.get("blood_sugar"),
                    temperature=payload.get("temperature"),
                    weight_kg=payload.get("weight_kg"),
                    logged_at=logged_at,
                    created_at=datetime.fromisoformat(memory.get("timestamp", "")),
                )
            )
        else:
            print(f"DEBUG [HEALTH]: Skipping memory - user_id mismatch")

    print(f"DEBUG [HEALTH]: Returning {len(vitals_entries)} vitals entries")
    return vitals_entries


@router.post("/vitals", response_model=VitalsResponse)
async def create_vitals(
    vitals_data: VitalsCreate,
    related_to: Optional[str] = Query(
        None, description="Related event ID (e.g., medication log)"
    ),
    current_user=Depends(get_current_user),
):
    """Log a vitals reading. Can be linked to medication logs or other events via related_to."""
    from src.schemas.events import EventKind

    vitals_id = locusgraph_service.new_id()
    context_id = VitalsEventDefinition.get_context_id(vitals_id)

    logged_at = vitals_data.logged_at or datetime.now(timezone.utc)

    payload = VitalsEventDefinition.create_payload(
        blood_pressure_systolic=vitals_data.blood_pressure_systolic,
        blood_pressure_diastolic=vitals_data.blood_pressure_diastolic,
        heart_rate=vitals_data.heart_rate,
        blood_sugar=vitals_data.blood_sugar,
        temperature=vitals_data.temperature,
        weight_kg=vitals_data.weight_kg,
        logged_at=logged_at,
        user_id=str(current_user.id),
    )

    print(
        f"DEBUG [HEALTH]: Storing vitals for user {current_user.id} with context_id={context_id}"
    )
    print(f"DEBUG [HEALTH]: Payload: {payload}")

    stored = await locusgraph_service.store_event(
        event_kind=EventKind.VITALS_CREATE,
        context_id=context_id,
        payload=payload,
        related_to=[related_to] if related_to else None,
    )

    return VitalsResponse(
        id=vitals_id,
        user_id=str(current_user.id),
        blood_pressure_systolic=vitals_data.blood_pressure_systolic,
        blood_pressure_diastolic=vitals_data.blood_pressure_diastolic,
        heart_rate=vitals_data.heart_rate,
        blood_sugar=vitals_data.blood_sugar,
        temperature=vitals_data.temperature,
        weight_kg=vitals_data.weight_kg,
        logged_at=logged_at,
        created_at=datetime.now(timezone.utc),
    )


@router.get("/recommendations", response_model=HealthRecommendationsResponse)
async def get_recommendations(
    categories: Optional[list[str]] = Query(
        None, description="Filter by recommendation categories"
    ),
    priority_min: Optional[str] = Query(
        None, description="Minimum priority level (low, medium, high, urgent)"
    ),
    actionable_only: bool = Query(
        False, description="Only return actionable recommendations"
    ),
    current_user=Depends(get_current_user),
):
    """
    Generate personalized health recommendations using LLM-powered analysis.

    Analyzes user's health data including:
    - Vitals trends (blood pressure, heart rate, blood sugar)
    - Food intake patterns
    - Medication adherence
    - Activity levels

    Returns actionable recommendations with priority levels and expected impact.
    """
    # Build comprehensive task for recommendations
    task = f"""
    Generate personalized health recommendations for user {current_user.id} based on their health data.
    Analyze the following aspects:
    1. Vitals trends and abnormalities
    2. Food/nutrition patterns
    3. Medication adherence and timing
    4. Overall health patterns

    Provide recommendations in these categories:
    - diet: nutrition and eating habits
    - exercise: physical activity recommendations
    - medication: medication-related suggestions
    - vitals: health metrics monitoring
    - lifestyle: general wellness recommendations

    For each recommendation, include:
    - Category
    - Title (short and clear)
    - Description (detailed explanation)
    - Priority level (low, medium, high, urgent)
    - Whether it's actionable
    - Estimated impact

    Format as JSON with: category, title, description, priority, actionable, estimated_impact
    """

    # Query user's health data
    query = f"all health data for user {current_user.id} including vitals food medication"
    context_ids = []

    # Include profile context if available
    profile_context_id = f"profile:{current_user.id}"
    context_ids.append(profile_context_id)

    # Generate recommendations using LocusGraph
    result = await locusgraph_service.generate_insights(
        task=task,
        locus_query=query,
        limit=50,  # Analyze more data points
        context_ids=context_ids if context_ids else None,
    )

    # Parse recommendations from the insight
    recommendations = []
    insight_text = result.get("insight", "")
    recommendation_text = result.get("recommendation", "")

    # If the LLM provided structured JSON, try to parse it
    import json
    import re

    # Try to extract JSON array from the response
    json_match = re.search(r'\[[\s\S]*\]', insight_text + recommendation_text)
    if json_match:
        try:
            parsed_recommendations = json.loads(json_match.group())
            for rec in parsed_recommendations:
                recommendations.append(
                    RecommendationItem(
                        category=rec.get("category", "general"),
                        title=rec.get("title", "Health Recommendation"),
                        description=rec.get("description", recommendation_text),
                        priority=rec.get("priority", "medium"),
                        actionable=rec.get("actionable", True),
                        estimated_impact=rec.get("estimated_impact"),
                    )
                )
        except (json.JSONDecodeError, KeyError):
            pass

    # If no structured recommendations found, create from the text
    if not recommendations:
        # Create a general recommendation from the text
        recommendations.append(
            RecommendationItem(
                category="overall",
                title="Health Analysis Complete",
                description=recommendation_text or insight_text,
                priority="medium",
                actionable=True,
                estimated_impact="Based on your health data analysis",
            )
        )

    # Apply filters
    if categories:
        recommendations = [r for r in recommendations if r.category in categories]

    if priority_min:
        priority_order = {"low": 1, "medium": 2, "high": 3, "urgent": 4}
        min_level = priority_order.get(priority_min, 0)
        recommendations = [
            r for r in recommendations if priority_order.get(r.priority, 0) >= min_level
        ]

    if actionable_only:
        recommendations = [r for r in recommendations if r.actionable]

    # Generate a summary
    summary = f"Based on analysis of your health data, we have {len(recommendations)} recommendation(s) for you. "
    if recommendations:
        high_priority = [r for r in recommendations if r.priority in ["high", "urgent"]]
        if high_priority:
            summary += f"Priority attention: {len(high_priority)} high/urgent priority item(s)."

    return HealthRecommendationsResponse(
        id=locusgraph_service.new_id(),
        user_id=str(current_user.id),
        recommendations=recommendations,
        summary=summary,
        confidence=result.get("confidence", 0.75),
        created_at=datetime.now(timezone.utc),
        data_points_analyzed=0,  # Would be populated from actual data count
    )


@router.get("/insights", response_model=HealthInsightResponse)
async def get_insights(
    insight_type: Optional[str] = Query(
        None,
        description="Type of insight: vitals, medication, food, overall (default: overall)",
    ),
    current_user=Depends(get_current_user),
):
    """
    Generate health insights using LocusGraph's AI-powered analysis.

    Provides intelligent analysis of user's health data including:
    - Trends and patterns in vitals
    - Medication adherence insights
    - Nutrition and food intake patterns
    - Overall health recommendations

    The insights are generated by analyzing all stored health events
    and using AI to identify patterns, correlations, and actionable insights.
    """
    # Build task based on insight type
    if insight_type in ["vitals", "medication", "food"]:
        task = f"""
        Analyze {insight_type} data for user {current_user.id} and provide insights.

        Focus on:
        1. Trends over time (improving, stable, declining)
        2. Patterns (daily, weekly, seasonal)
        3. Anomalies or outliers
        4. Correlations with other health metrics

        Provide specific, actionable insights with confidence levels.
        """
    else:
        task = f"""
        Provide comprehensive health insights for user {current_user.id}.

        Analyze all available health data including:
        - Vitals (blood pressure, heart rate, blood sugar, temperature, weight)
        - Food intake and nutrition patterns
        - Medication adherence and schedules
        - Activity and lifestyle factors

        Provide:
        1. Overall health assessment
        2. Key trends and patterns
        3. Areas of concern
        4. Positive developments
        5. Actionable recommendations
        """

    # Query relevant context
    query_parts = [f"health data user {current_user.id}"]
    if insight_type:
        query_parts.append(insight_type)

    query = " ".join(query_parts)

    # Add profile context for personalized insights
    context_ids = [f"profile:{current_user.id}"]

    # Generate insights using LocusGraph
    result = await locusgraph_service.generate_insights(
        task=task,
        locus_query=query,
        limit=30,
        context_ids=context_ids,
    )

    # Determine insight type
    actual_insight_type = insight_type or "overall"

    return HealthInsightResponse(
        id=locusgraph_service.new_id(),
        user_id=str(current_user.id),
        insight_type=actual_insight_type,
        insight=result.get("insight", "No insights available at this time."),
        recommendation=result.get("recommendation", "Continue monitoring your health data."),
        confidence=result.get("confidence", 0.75),
        created_at=datetime.now(timezone.utc),
        data_points_analyzed=0,  # Would be populated from actual data count
        context={"insight_type": actual_insight_type, "query": query},
    )
