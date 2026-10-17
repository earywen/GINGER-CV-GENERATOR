# -*- coding: utf-8 -*-
from app.routers.cv import router as cv_router
from app.routers.render import router as render_router
from app.routers.feedback import router as feedback_router

__all__ = ["cv_router", "render_router", "feedback_router"]
