from datetime import datetime, time
from typing import Optional
from pydantic import BaseModel, UUID4

class BaseSchema(BaseModel):
    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        json_encoders = {
            time: lambda v: v.strftime('%H:%M') if v else None
        }