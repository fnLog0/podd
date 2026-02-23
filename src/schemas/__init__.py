from src.schemas.auth import (
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from src.schemas.chat import ChatHistoryResponse, ChatRequest, ChatResponse
from src.schemas.events import (
    ContextIdPattern,
    EventKind,
    MedicationEventDefinition,
    MedicationScheduleEventDefinition,
    ProfileEventDefinition,
)
from src.schemas.health import (
    FoodLogCreate,
    FoodLogResponse,
    FoodLogUpdate,
    VitalsCreate,
    VitalsResponse,
    VitalsUpdate,
)
from src.schemas.medication import (
    MedicationCreate,
    MedicationLogCreate,
    MedicationLogResponse,
    MedicationResponse,
    MedicationScheduleCreate,
    MedicationScheduleResponse,
    MedicationScheduleUpdate,
    MedicationUpdate,
)
from src.schemas.profile import ProfileCreate, ProfileResponse, ProfileUpdate
from src.schemas.voice import (
    VoiceConversationRequest,
    VoiceConversationResponse,
    VoiceStreamResponse,
    VoiceSynthesizeRequest,
)

__all__ = [
    # Auth schemas
    "LoginRequest",
    "LogoutRequest",
    "RefreshRequest",
    "RegisterRequest",
    "TokenResponse",
    "UserResponse",
    # Chat schemas
    "ChatRequest",
    "ChatResponse",
    "ChatHistoryResponse",
    # Event schemas
    "ContextIdPattern",
    "EventKind",
    "ProfileEventDefinition",
    "MedicationEventDefinition",
    "MedicationScheduleEventDefinition",
    # Profile schemas
    "ProfileCreate",
    "ProfileResponse",
    "ProfileUpdate",
    # FoodLog schemas
    "FoodLogCreate",
    "FoodLogResponse",
    "FoodLogUpdate",
    # Vitals schemas
    "VitalsCreate",
    "VitalsResponse",
    "VitalsUpdate",
    # Medication schemas
    "MedicationCreate",
    "MedicationResponse",
    "MedicationUpdate",
    "MedicationLogCreate",
    "MedicationLogResponse",
    # MedicationSchedule schemas
    "MedicationScheduleCreate",
    "MedicationScheduleResponse",
    "MedicationScheduleUpdate",
    # Voice schemas
    "VoiceStreamResponse",
    "VoiceSynthesizeRequest",
    "VoiceConversationRequest",
    "VoiceConversationResponse",
]

__all__ = [
    # Auth schemas
    "LoginRequest",
    "LogoutRequest",
    "RefreshRequest",
    "RegisterRequest",
    "TokenResponse",
    "UserResponse",
    # Chat schemas
    "ChatRequest",
    "ChatResponse",
    "ChatHistoryResponse",
    # Event schemas
    "ContextIdPattern",
    "EventKind",
    "ProfileEventDefinition",
    "MedicationEventDefinition",
    "MedicationScheduleEventDefinition",
    # Profile schemas
    "ProfileCreate",
    "ProfileResponse",
    "ProfileUpdate",
    # FoodLog schemas
    "FoodLogCreate",
    "FoodLogResponse",
    "FoodLogUpdate",
    # Vitals schemas
    "VitalsCreate",
    "VitalsResponse",
    "VitalsUpdate",
    # Medication schemas
    "MedicationCreate",
    "MedicationResponse",
    "MedicationUpdate",
    "MedicationLogCreate",
    "MedicationLogResponse",
    # MedicationSchedule schemas
    "MedicationScheduleCreate",
    "MedicationScheduleResponse",
    "MedicationScheduleUpdate",
]
