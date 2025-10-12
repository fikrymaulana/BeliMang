from pydantic import BaseModel, validator


class AdminRegister(BaseModel):
    username: str
    password: str
    email: str

    @validator("username")
    def validate_username(cls, v):
        if not isinstance(v, str):
            raise ValueError("Username must be string")
        if not v.strip():
            raise ValueError("Username cannot be empty")
        if len(v) < 5 or len(v) > 30:
            raise ValueError("Username must be 5-30 characters")
        return v

    @validator("password")
    def validate_password(cls, v):
        if not isinstance(v, str):
            raise ValueError("Password must be string")
        if not v.strip():
            raise ValueError("Password cannot be empty")
        if len(v) < 5 or len(v) > 30:
            raise ValueError("Password must be 5-30 characters")
        return v

    @validator("email")
    def validate_email(cls, v):
        if not isinstance(v, str):
            raise ValueError("Email must be string")
        if not v.strip():
            raise ValueError("Email cannot be empty")
        if "@" not in v:
            raise ValueError("Email must contain @ character")
        if v.startswith("@") or v.endswith("@"):
            raise ValueError("Email cannot start or end with @ character")
        # Additional basic checks
        return v


class AdminLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    token: str

