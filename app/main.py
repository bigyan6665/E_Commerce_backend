from fastapi import FastAPI,HTTPException,Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.routing import customers
from app.routing import auth
from app.routing import customer_profile
from fastapi.staticfiles import StaticFiles
from app.routing import admin
from app.database import models
from app.database.db import engine
from app.database.db import Base


app = FastAPI()

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
    return {"message":"This is app route"}

# registering routes(defined using APIRouter)
app.include_router(customers.router)
app.include_router(auth.router)
app.include_router(customer_profile.router)
app.include_router(admin.router)