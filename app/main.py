import uvicorn
from fastapi import FastAPI, Depends, Security
from fastapi.openapi.models import APIKey, APIKeyIn
from fastapi.security import APIKeyHeader
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from starlette.responses import RedirectResponse

from app.api.api import api_router
from app.api.middleware import api_key_middleware
from app.settings import settings

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[settings.RATE_LIMITING_FREQUENCY],
    enabled=settings.RATE_LIMITING_ENABLE,
)

# Define API key security scheme for OpenAPI/Swagger UI
api_key_header = APIKeyHeader(name=settings.API_KEY_NAME, auto_error=False)

app = FastAPI(
    title="Transfermarkt API",
    openapi_tags=[
        {"name": "competitions", "description": "Operations with competitions data"},
        {"name": "clubs", "description": "Operations with clubs data"},
        {"name": "players", "description": "Operations with players data"},
    ],
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Add middleware for API key authentication
@app.middleware("http")
async def add_api_key_middleware(request, call_next):
    return await api_key_middleware(request, call_next)

# Configure security for OpenAPI/Swagger UI
# Store the original openapi function
original_openapi = app.openapi
app.openapi_schema = None  # Force regeneration of OpenAPI schema

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    # Call the original openapi function, not our custom one
    openapi_schema = original_openapi()
    
    # Add the security scheme to the OpenAPI specification
    openapi_schema["components"] = openapi_schema.get("components", {})
    openapi_schema["components"]["securitySchemes"] = {
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": settings.API_KEY_NAME
        }
    }
    
    # Apply the security globally to all operations
    openapi_schema["security"] = [{"ApiKeyAuth": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

app.include_router(api_router)


@app.get("/", include_in_schema=False)
def docs_redirect():
    return RedirectResponse(url="/docs")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
