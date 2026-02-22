from pydantic import BaseModel
from typing import Optional

# pydantic model donot know how to serialize if data type is not specified
# Generic classes having T as a placeholder for type
class APIResponse[T](BaseModel): # for consistent api response
    message: str
    success : bool
    content: Optional[T] = None