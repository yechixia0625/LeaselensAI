from pydantic import BaseModel, Field


class DemoLoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=128)
    password: str = Field(..., min_length=1, max_length=256)


class DemoSessionResponse(BaseModel):
    authenticated: bool
    username: str | None = None
    authEnabled: bool = True
