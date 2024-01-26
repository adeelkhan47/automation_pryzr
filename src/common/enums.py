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


class EmailStatus(Enum):
    Successful = "Successful"
    Skipped = "Skipped"
    Failed = "Failed"


class Platforms(Enum):
    Taichi = "Taichi"
    VBLink = "VBlink"
    Firekirin = "Firekirin"
    Acebook = "Acebook"
    Orionstar = "Orionstar"
    GameVault999 = "GameVault999"
    Juwa = "Juwa"
    BlueDragon = "BlueDragon"
    GoldenDragon = "GoldenDragon"
    Milkyway = "Milkyway"
    DragonCrown = "DragonCrown"
    BigWinner = "BigWinner"
    UltraPanda = "UltraPanda"
    DragonWorld = "DragonWorld"
    PandaMaster = "PandaMaster"

