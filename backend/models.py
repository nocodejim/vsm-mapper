from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from datetime import datetime
from .main import Base # Import Base from main.py

class ValueStreamMap(Base):
    __tablename__ = "value_stream_maps"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    steps = relationship("VSMStep", back_populates="map", cascade="all, delete-orphan")

class VSMStep(Base):
    __tablename__ = "vsm_steps"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    map_id = Column(Integer, ForeignKey("value_stream_maps.id"))
    step_number = Column(Integer)
    name = Column(String, nullable=False)
    process_time = Column(String, nullable=False)
    wait_time = Column(String, nullable=True)

    map = relationship("ValueStreamMap", back_populates="steps")

# Pydantic Schemas
class VSMStepBase(BaseModel):
    name: str
    process_time: str
    wait_time: str | None = None
    step_number: int

class VSMStepCreate(VSMStepBase):
    pass

class VSMStep(VSMStepBase):
    id: int
    map_id: int

    class Config:
        orm_mode = True

class ValueStreamMapBase(BaseModel):
    title: str | None = None

class ValueStreamMapCreate(ValueStreamMapBase):
    steps: list[VSMStepCreate] = []

class ValueStreamMap(ValueStreamMapBase):
    id: int
    created_at: datetime
    updated_at: datetime
    steps: list[VSMStep] = []

    class Config:
        orm_mode = True
