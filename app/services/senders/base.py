# app/services/senders/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class SendResult:
    success: bool
    response: Optional[Dict[str, Any]] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None

class NotificationSender(ABC):
    @abstractmethod
    async def send(self, notification) -> SendResult:
        pass
