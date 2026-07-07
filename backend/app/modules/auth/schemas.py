import uuid

from pydantic import BaseModel, Field, field_validator


class RegisterRequest(BaseModel):
    phone: str = Field(min_length=8, max_length=20)
    country_code: str = Field(min_length=2, max_length=2)
    pin: str = Field(min_length=4, max_length=6)

    @field_validator("pin")
    @classmethod
    def pin_must_be_digits(cls, v: str) -> str:
        if not v.isdigit():
            raise ValueError("PIN must contain only digits")
        return v

    @field_validator("country_code")
    @classmethod
    def country_code_upper(cls, v: str) -> str:
        return v.upper()


class RegisterResponse(BaseModel):
    user_id: uuid.UUID
    phone: str
    otp_expires_in_seconds: int
    # Sandbox-only convenience: never populated once a real SMS provider is wired up.
    sandbox_otp_code: str | None = None


class VerifyOtpRequest(BaseModel):
    phone: str
    code: str
    device_id: str | None = None
    device_name: str | None = None


class LoginRequest(BaseModel):
    phone: str
    pin: str
    device_id: str | None = None
    device_name: str | None = None


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str
    all_devices: bool = False


class ChangePinRequest(BaseModel):
    current_pin: str
    new_pin: str = Field(min_length=4, max_length=6)

    @field_validator("new_pin")
    @classmethod
    def pin_must_be_digits(cls, v: str) -> str:
        if not v.isdigit():
            raise ValueError("PIN must contain only digits")
        return v


class ForgotPinRequest(BaseModel):
    phone: str


class ForgotPinResponse(BaseModel):
    message: str
    otp_expires_in_seconds: int
    sandbox_otp_code: str | None = None


class ResetPinRequest(BaseModel):
    phone: str
    code: str
    new_pin: str = Field(min_length=4, max_length=6)

    @field_validator("new_pin")
    @classmethod
    def pin_must_be_digits(cls, v: str) -> str:
        if not v.isdigit():
            raise ValueError("PIN must contain only digits")
        return v


class TokenPairResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class MessageResponse(BaseModel):
    message: str
