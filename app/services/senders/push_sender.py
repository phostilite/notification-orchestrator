# app/services/senders/push_sender.py
from typing import Dict, Any
import aiohttp
from app.core.config import settings
from .base import NotificationSender, SendResult

class PushSender(NotificationSender):
    async def send(self, notification) -> SendResult:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    settings.PUSH_PROVIDER_URL,
                    headers={
                        "Authorization": f"Bearer {settings.PUSH_PROVIDER_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "user_id": str(notification.user_id),
                        "title": notification.template.name,
                        "body": notification.content,
                        "metadata": notification.metadata
                    }
                ) as response:
                    response_data = await response.json()
                    
                    if response.status == 200:
                        return SendResult(
                            success=True,
                            response=response_data
                        )
                    else:
                        return SendResult(
                            success=False,
                            response=response_data,
                            error_code=str(response.status),
                            error_message=response_data.get("message", "Unknown error")
                        )
                        
        except Exception as e:
            return SendResult(
                success=False,
                error_code="INTERNAL_ERROR",
                error_message=str(e)
            )