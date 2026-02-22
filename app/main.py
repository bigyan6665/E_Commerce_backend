from app.routing import products_routing
from fastapi import FastAPI,HTTPException,Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.routing import customers_routing
from app.routing import auth_routing
from app.routing import customer_profile_routing
from app.routing import order_routing
from fastapi.staticfiles import StaticFiles
from app.routing import admin_routing
from app.database.models import *
from app.database.db import engine
from app.database.db import Base
from fastapi.openapi.utils import get_openapi

app = FastAPI()

# Customize OpenAPI so Swagger UI shows Bearer token input instead of username/password
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="My API",
        version="1.0",
        description="API with JWT auth",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

# for consistent exception
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code, # explicit status code
        content={ # this format is followed whenever HTTPException is raised
            "success": False,
            "message": str(exc.detail), # explicit detail
            "error_code": "HTTP_ERROR"
        },
    )
# for consistent pydantic validation error
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse( # this format is followed whenever pydantic validation error is raised
        status_code=422,
        content={
            "success": False,
            # "message": str(exc.errors()[0].get("msg")),
            "message": str(exc.errors()),
            "error_code": "VALIDATION_ERROR",
        },
    )


@app.get("/")
def root():
    return {"message":"Welcome to my E-commerce Backend"}

# registering routes(defined using APIRouter)
app.include_router(admin_routing.router)
app.include_router(auth_routing.router)
app.include_router(customers_routing.router)
app.include_router(customer_profile_routing.router)
app.include_router(products_routing.router)
app.include_router(order_routing.router)