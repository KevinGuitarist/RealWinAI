from sqlalchemy import Boolean, Column, Float, String,Integer, ForeignKey, DateTime 
from sqlalchemy.orm import relationship
from sqlalchemy import func
from source.core.models import Model
from source.app.access.models import Role 

class User(Model):

    __tablename__ = "User"
    username = Column(name="username", type_=String, unique=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)  # hashed via werkzeug
    first_name = Column(name="first_name", type_=String, nullable=True)
    last_name = Column(name="last_name", type_=String, nullable=True)
    active = Column(name="active", type_=Boolean, default=True, server_default="true")
    verified_user = Column(name="verified_user", type_=Boolean, nullable=False, default=False)
    phone = Column(name="phone", type_=String)
    sub = Column(name="sub", type_=String)
    password_timestamp = Column(name="password_timestamp", type_=Float)

      # M.A.X. specific fields (added by migration)
    telegram_user_id = Column(Integer, unique=True, nullable=True)
    telegram_chat_id = Column(String, unique=True, nullable=True, index=True)  # For Telegram Chat ID lookup
    preferred_channel = Column(String(50), default="webapp")
    personality_string = Column(String, nullable=True)

    source = Column(String, nullable=True) 

    last_login_ip   = Column(String(45), nullable=True, index=True)
    geo_country     = Column(String(64),  nullable=True)
    geo_region      = Column(String(128), nullable=True)
    geo_city        = Column(String(128), nullable=True)
    geo_latitude    = Column(Float,       nullable=True)
    geo_longitude   = Column(Float,       nullable=True)
    last_seen_at    = Column(DateTime,    nullable=True)


    roles = relationship(
        Role,
        secondary="user_roles",
        back_populates="users",
        lazy="selectin",   # <- async-safe eager loader

    )

    settings = relationship(
        "UserSettings",
        uselist=False,
        back_populates="user",
        cascade="all, delete-orphan",
    )


# Properties for M.A.X. compatibility
    @property
    def phone_number(self):
        """Alias for phone field for M.A.X. compatibility"""
        return self.phone

    @property
    def account_creation_date(self):
        """Alias for create_date field for M.A.X. compatibility"""
        return self.create_date

    @property
    def created_at(self):
        """Alias for create_date field for M.A.X. compatibility"""
        return self.create_date
