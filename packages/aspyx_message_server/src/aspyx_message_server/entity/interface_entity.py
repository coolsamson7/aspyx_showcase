import uuid

from sqlalchemy import Column, String, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from .base import Base

class OnEventEntity(Base):
    __tablename__ = "ON_EVENT"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    version_id = Column(Integer, nullable=False, default=0)

    event = Column(String)
    filter = Column(String)
    handlers = relationship("InterfaceHandlerEntity", back_populates="event")  # 1:N relationship

    __mapper_args__ = {
        "version_id_col": version_id
    }

    def __repr__(self):
        return f"<OnEntity(id={self.id}, event={self.event},  filter={self.filter})>"

class InterfaceHandlerEntity(Base):
    __tablename__ = "INTERFACE_HANDLER"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    version_id = Column(Integer, nullable=False, default=0)

    format = Column(String)
    sink = Column(String)
    args = Column(String)
    template = Column(String)

    or_on_event = Column(UUID(as_uuid=True), ForeignKey("ON_EVENT.id"))
    event = relationship("OnEventEntity", back_populates="handlers")

    __mapper_args__ = {
        "version_id_col": version_id
    }

    def __repr__(self):
        return f"<InterfaceHandler(id={self.id}, sink={self.sink}, format={self.format})>"
