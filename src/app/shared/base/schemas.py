from pydantic import BaseModel, ConfigDict

class APIModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")
