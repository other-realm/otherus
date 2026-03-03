"""Push notification service using ntfy.sh."""
import httpx
from app.config import get_settings
from app.services.redis_service import json_get

settings = get_settings()


async def send_push_notification(
    ntfy_topic: str,
    title: str,
    message: str,
    click_url: str = "",
    priority: str = "default",
) -> bool:
    """Send a push notification to a user's ntfy.sh topic."""
    url = f"{settings.ntfy_base_url}/{ntfy_topic}"
    headers = {
        "Title": title,
        "Priority": priority,
        "Content-Type": "text/plain",
    }
    if click_url:
        headers["Click"] = click_url

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, content=message, headers=headers, timeout=5.0)
            return resp.status_code == 200
    except Exception:
        return False


async def notify_user_of_message(
    recipient_user_id: str,
    sender_name: str,
    room_name: str,
    message_preview: str,
) -> bool:
    """Notify a user about a new chat message if they have a ntfy topic set."""
    user = await json_get(f"user:{recipient_user_id}")
    if not user:
        return False
    ntfy_topic = user.get("ntfy_topic")
    if not ntfy_topic:
        return False
    return await send_push_notification(
        ntfy_topic=ntfy_topic,
        title=f"New message from {sender_name}",
        message=f"In {room_name}: {message_preview[:100]}",
        click_url=f"{settings.frontend_url}/chat",
    )
