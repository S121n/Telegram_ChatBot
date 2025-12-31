
from .start import router as start_router
from .register import router as register_router
from .profile import router as profile_router
from .match import router as match_router
from .chat import router as chat_router
from .report import router as report_router

__all__ = [
    'start_router',
    'register_router',
    'profile_router',
    'match_router',
    'chat_router',
    'report_router'
]