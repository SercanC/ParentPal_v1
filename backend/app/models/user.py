from sqlalchemy import Column, String, Boolean, JSON, Integer, DateTime
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class User(Base):
    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    preferences = Column(JSON, default={})
    version = Column(Integer, default=1)
    last_sync = Column(DateTime, nullable=True)

    # Relationships
    babies = relationship("Baby", back_populates="primary_caregiver")
    care_team_memberships = relationship("CareTeamMember", back_populates="user")
    activities = relationship("Activity", back_populates="created_by_user")