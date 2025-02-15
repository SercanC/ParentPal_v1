from sqlalchemy import Column, String, JSON, Integer, ForeignKey, Enum, DateTime, Index
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from app.models.enums import CareTeamRole, SyncStatus

class CareTeamMember(Base):
    id = Column(String, primary_key=True, index=True)
    baby_id = Column(String, ForeignKey("baby.id"), nullable=False)
    user_id = Column(String, ForeignKey("user.id"), nullable=False)
    role = Column(Enum(CareTeamRole), nullable=False)
    permissions = Column(JSON, default={})
    version = Column(Integer, default=1)
    sync_status = Column(Enum(SyncStatus), default=SyncStatus.PENDING)
    sync_attempts = Column(Integer, default=0)
    last_sync_attempt = Column(DateTime, nullable=True)

    # Relationships
    baby = relationship("Baby", back_populates="care_team")
    user = relationship("User", back_populates="care_team_memberships")

    # Indexes
    __table_args__ = (
        Index('idx_care_team_access', 'baby_id', 'user_id', 'role'),
        Index('idx_care_team_sync', 'sync_status', 'last_sync_attempt')
    )