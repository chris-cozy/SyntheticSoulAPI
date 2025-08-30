from .root import router as root_router
from .messages import router as messages_router
from .jobs import router as jobs_router
from .agents import router as agents_router


all_routers = [root_router, messages_router, jobs_router, agents_router]