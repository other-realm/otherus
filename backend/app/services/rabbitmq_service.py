"""RabbitMQ service for chat message orchestration via aio-pika."""
import json
import asyncio
from typing import Callable, Coroutine, Any, Optional
import aio_pika
from aio_pika import ExchangeType
from app.config import get_settings

_connection: Optional[aio_pika.abc.AbstractRobustConnection] = None
_channel: Optional[aio_pika.abc.AbstractChannel] = None
EXCHANGE_NAME = "other_us_chat"


async def get_channel() -> aio_pika.abc.AbstractChannel:
    global _connection, _channel
    settings = get_settings()
    if _connection is None or _connection.is_closed:
        _connection = await aio_pika.connect_robust(settings.rabbitmq_url)
    if _channel is None or _channel.is_closed:
        _channel = await _connection.channel()
    return _channel


async def get_exchange() -> aio_pika.abc.AbstractExchange:
    channel = await get_channel()
    exchange = await channel.declare_exchange(
        EXCHANGE_NAME, ExchangeType.TOPIC, durable=True
    )
    return exchange


async def publish_message(room_id: str, message: dict) -> None:
    """Publish a chat message to the room's topic."""
    exchange = await get_exchange()
    routing_key = f"room.{room_id}"
    await exchange.publish(
        aio_pika.Message(
            body=json.dumps(message).encode(),
            content_type="application/json",
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        ),
        routing_key=routing_key,
    )


async def subscribe_to_room(
    room_id: str,
    callback: Callable[[dict], Coroutine[Any, Any, None]],
    consumer_tag: str = "",
) -> aio_pika.abc.AbstractQueue:
    """Subscribe to messages for a specific room."""
    channel = await get_channel()
    exchange = await get_exchange()
    queue = await channel.declare_queue(
        f"room_{room_id}_{consumer_tag}",
        durable=True,
        auto_delete=False,
    )
    await queue.bind(exchange, routing_key=f"room.{room_id}")

    async def on_message(msg: aio_pika.abc.AbstractIncomingMessage):
        async with msg.process():
            data = json.loads(msg.body)
            await callback(data)

    await queue.consume(on_message, consumer_tag=consumer_tag or None)
    return queue


async def close_connection():
    global _connection, _channel
    if _channel and not _channel.is_closed:
        await _channel.close()
    if _connection and not _connection.is_closed:
        await _connection.close()
    _connection = None
    _channel = None
