from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from .user import UserService
from .baby import BabyService
from .activity import ActivityService
from .care_team import CareTeamService

class ServiceFactory:
    def __init__(self, db: AsyncSession):
        self.db = db
        self._user_service: Optional[UserService] = None
        self._baby_service: Optional[BabyService] = None
        self._activity_service: Optional[ActivityService] = None
        self._care_team_service: Optional[CareTeamService] = None

    @property
    def user(self) -> UserService:
        if not self._user_service:
            self._user_service = UserService(self.db)
        return self._user_service

    @property
    def baby(self) -> BabyService:
        if not self._baby_service:
            self._baby_service = BabyService(self.db)
        return self._baby_service

    @property
    def activity(self) -> ActivityService:
        if not self._activity_service:
            self._activity_service = ActivityService(self.db)
        return self._activity_service

    @property
    def care_team(self) -> CareTeamService:
        if not self._care_team_service:
            self._care_team_service = CareTeamService(self.db)
        return self._care_team_service