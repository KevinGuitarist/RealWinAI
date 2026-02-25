from enum import Enum


class Platform(Enum):
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"
    WEBAPP = "webapp"
    EMAIL = "email"
    SMS = "sms"


class UserPersona(Enum):
    CASUAL = "casual fan"
    ANALYTICAL = "data analyst"
    RISK_TAKER = "risk taker"


class BotPersona(Enum):
    AMPLIFIER = "amplifier"
    COMFORTOR = "comfortor"
    TRUST_BUILDER = "trust builder"
    GUIDE = "guide"
    GUARDIAN = "guardian"
