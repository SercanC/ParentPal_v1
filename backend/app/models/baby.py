from sqlalchemy import Column, String, JSON, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from app.models.enums import SyncStatus

class Baby(Base):
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    primary_caregiver_id = Column(String, ForeignKey("user.id"), nullable=False)
    development_data = Column(JSON, default={})
    version = Column(Integer, default=1)
    sync_status = Column(Enum(SyncStatus), default=SyncStatus.SYNCED)

    # Relationships
    primary_caregiver = relationship("User", back_populates="babies")
    care_team = relationship("CareTeamMember", back_populates="baby")
    activities = relationship("Activity", back_populates="baby")