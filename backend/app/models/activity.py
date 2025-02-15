from sqlalchemy import Column, String, JSON, Integer, ForeignKey, Enum, DateTime, Index
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from app.models.enums import ActivityType, SyncStatus

class Activity(Base):
    id = Column(String, primary_key=True, index=True)
    baby_id = Column(String, ForeignKey("baby.id"), nullable=False)
    type = Column(Enum(ActivityType), nullable=False)
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=True)
    activity_metadata = Column(JSON, default={})
    created_by = Column(String, ForeignKey("user.id"), nullable=False)
    version = Column(Integer, default=1)
    sync_status = Column(Enum(SyncStatus), default=SyncStatus.PENDING)
    sync_attempts = Column(Integer, default=0)
    last_sync_attempt = Column(DateTime, nullable=True)

    # Relationships
    baby = relationship("Baby", back_populates="activities")
    created_by_user = relationship("User", back_populates="activities")

    # Indexes for efficient querying
    __table_args__ = (
        Index('idx_activity_baby_time', 'baby_id', 'start_time'),
        Index('idx_activity_sync', 'sync_status', 'last_sync_attempt'),
    )