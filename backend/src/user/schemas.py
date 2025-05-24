from pydantic import BaseModel, field_validator, ConfigDict
import phonenumbers
from datetime import datetime


class UserInfoBase(BaseModel):
    name: str | None = None
    surname: str | None = None
    patronymic: str | None = None
    phone_number: str | None = None

    @field_validator('phone_number')
    @classmethod
    def validate_phone(cls, v):
        if not v:
            return v
        try:
            parsed = phonenumbers.parse(v, None)
            if not phonenumbers.is_valid_number(parsed):
                raise ValueError("Invalid phone number")
            return phonenumbers.format_number(
                parsed,
                phonenumbers.PhoneNumberFormat.E164
            )
        except phonenumbers.NumberParseException:
            raise ValueError("Phone number must be in international format (+XXX...)")

class UserInfoCreate(UserInfoBase):
    pass

class UserInfoUpdate(UserInfoBase):
    pass

class UserInfoResponse(UserInfoBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime