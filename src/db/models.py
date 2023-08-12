"""Models for the database."""

from enum import Enum
from sqlalchemy import Column, Integer, String, Enum as SQLEnum, \
    DateTime, Time
from .database import Base
from pydantic import BaseModel


class StoreTimezone(Base):

    __tablename__ = "store_timezone"

    store_id = Column(String, primary_key=True, index=True)
    timezone_str = Column(String, index=True, default="America/Chicago")


class BusinessHours(Base):

    __tablename__ = "business_hours"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(String, index=True)
    day_of_week = Column(Integer, index=True)
    open_time = Column(Time, default="00:00:00")
    close_time = Column(Time, default="23:59:59")


class StoreStatus(Enum):

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class StoreLogs(Base):

    __tablename__ = "store_logs"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(String, index=True)
    timestamp = Column(DateTime(timezone=True), index=True)
    status = Column(
        SQLEnum(StoreStatus),
        index=True,
        default=StoreStatus.ACTIVE,
        nullable=False,
    )


class Report(Base):

    __tablename__ = "report"

    id = Column(Integer, primary_key=True, index=True)
