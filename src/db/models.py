"""Models for the database."""

from enum import Enum
from sqlalchemy import Column, Integer, String, Enum as SQLEnum, \
    DateTime
from .database import Base
from pydantic import BaseModel


class StoreTimezone(Base):

    __tablename__ = "store_timezone"

    store_id = Column(String, primary_key=True, index=True)
    timezone = Column(String, index=True, default="America/Chicago")


class BusinessHours(Base):

    __tablename__ = "business_hours"

    store_id = Column(String, primary_key=True, index=True)
    day_of_week = Column(Integer, primary_key=True, index=True)
    open_time = Column(DateTime, default="00:00:00")
    close_time = Column(DateTime, default="23:59:59")


class StoreStatus(Enum):

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class StoreLogs(Base):

    __tablename__ = "store_logs"

    store_id = Column(String, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), primary_key=True, index=True)
    status = Column(
        SQLEnum(StoreStatus),
        index=True,
        default=StoreStatus.ACTIVE,
        nullable=False,
    )
