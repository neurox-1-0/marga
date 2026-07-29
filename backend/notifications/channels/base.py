from abc import ABC, abstractmethod
from backend.schemas.api import ApprovalCard


class BaseChannel(ABC):
    @abstractmethod
    def notify(self, card: ApprovalCard, dashboard_url: str):
        pass
