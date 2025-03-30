from pydantic import BaseModel, field_validator
import phonenumbers


class UserInfo(BaseModel):
    name: str | None = None
    surname: str | None = None
    patronymic: str | None = None
    phone_number: str | None = None

    @field_validator('phone_number')
    @classmethod
    def validate_phone(cls, v):
        if v is None:
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


class UserInfoCreate(UserInfo):
    pass


class UserInfoUpdate(UserInfo):
    pass


class UserInfoResponse(UserInfo):
    pass