from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse

from app.settings import settings


async def api_key_middleware(request: Request, call_next):
    """
    Middleware for API key authentication.
    Checks if the API key in the request header matches the configured API key.
    """
    # Skip authentication for docs and redoc endpoints
    if request.url.path in ["/docs", "/redoc", "/openapi.json", "/"]:
        return await call_next(request)
    
    # Skip options requests (for CORS)
    if request.method == "OPTIONS":
        return await call_next(request)
    
    api_key = request.headers.get(settings.API_KEY_NAME)
    
    if not api_key:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "API key missing"},
        )
    
    if api_key != settings.API_KEY:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": "Invalid API key"},
        )
    
    return await call_next(request) 