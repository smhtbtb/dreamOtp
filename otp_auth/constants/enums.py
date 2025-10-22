from enum import Enum

class IdentifierType(Enum):
    EMAIL = "email"
    PHONE = "phone"

    @classmethod
    def choices(cls):
        return [(tag.value, tag.name.title()) for tag in cls]
