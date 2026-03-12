from pydantic import BaseModel, Field


class CapabilitiesResponse(BaseModel):
    service: str
    version: str
    mode: str = "transparent-relay"
    relay_contract: dict = Field(default_factory=dict)
