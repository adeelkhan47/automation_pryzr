from enum import Enum as PyEnum


class Enum(str, PyEnum):
    @classmethod
    def exists(cls, item):
        return item in [x.value for x in cls]

    @classmethod
    def list(cls):
        return [x.value for x in cls]

    @classmethod
    def select(cls, key):
        for member in cls:
            if member.name == key:
                return member.value


class Auth(Enum):
    FACEBOOK = "facebook"
    GOOGLE = "google"
    APPLE = "apple"


class OrganizationSize(Enum):
    MYSELF = "myself"
    RANGE_0_50 = "0-50"
    RANGE_51_100 = "51-100"
    RANGE_101_500 = "101-500"
    RANGE_501_1000 = "501-1000"
    RANGE_1000_PLUS = "1000+"
