from datetime import datetime
from typing import Optional
from pydantic import BaseModel, UUID4

class BaseSchema(BaseModel):
    class Config:
        orm_mode = True
        allow_population_by_field_name = True