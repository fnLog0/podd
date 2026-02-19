from src.routes.health.food_log import router as food_log_router
from src.routes.health.health import router as health_router
from src.routes.health.tracking import router as tracking_router
from src.routes.health.vitals import router as vitals_router

__all__ = ["food_log_router", "health_router", "tracking_router", "vitals_router"]
