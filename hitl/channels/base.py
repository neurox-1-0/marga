from abc import ABC, abstractmethod
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))
from shared.schemas import ApprovalCard

class BaseChannel(ABC):
    @abstractmethod
    def notify(self, card: ApprovalCard, dashboard_url: str):
        pass
