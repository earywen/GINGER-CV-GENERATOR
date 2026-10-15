# -*- coding: utf-8 -*-
import uvicorn
from app.core import settings

if __name__ == '__main__':
    uvicorn.run(
        'app.main:app',
        host=settings.HOST,
        port=settings.PORT,
        log_level=settings.LOG_LEVEL.lower()
    )
