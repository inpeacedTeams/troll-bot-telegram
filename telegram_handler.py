import asyncio
from telethon import TelegramClient, events
from telethon.tl.types import User, Chat, Channel
from typing import Callable, Optional

class TelegramHandler:
    def __init__(self, api_id: int, api_hash: str, session_name: str = "troll_session"):
        self.client = TelegramClient(session_name, api_id, api_hash)
        self.target_id: Optional[int] = None
        self.target_username: Optional[str] = None
        self.active_chat_id: Optional[int] = None
        self.is_running = False
        self.on_message_callback: Optional[Callable] = None
        self.on_typing_callback: Optional[Callable] = None

    async def connect(self):
        await self.client.connect()

    async def send_code_req(self, phone: str):
        return await self.client.send_code_request(phone)

    async def sign_in(self, phone: str, code: str, phone_code_hash: str):
        return await self.client.sign_in(phone=phone, code=code, phone_code_hash=phone_code_hash)

    async def is_user_authorized(self) -> bool:
        return await self.client.is_user_authorized()

    async def get_dialogs(self):
        dialogs = []
        async for d in self.client.iter_dialogs(limit=30):
            if d.is_group or d.is_channel or d.is_user:
                dialogs.append({"id": d.id, "title": d.title or d.name})
        return dialogs

    async def get_recent_messages(self, chat_id: int, limit: int = 30):
        messages = []
        async for msg in self.client.iter_messages(chat_id, limit=limit):
            sender = await msg.get_sender()
            sender_name = getattr(sender, 'first_name', '') or getattr(sender, 'username', 'Unknown')
            messages.append({
                "id": msg.id,
                "sender_id": msg.sender_id,
                "sender_name": sender_name,
                "text": msg.text or ""
            })
        return messages

    def setup_listeners(self, on_message: Callable, on_typing: Optional[Callable] = None):
        self.on_message_callback = on_message
        self.on_typing_callback = on_typing

        @self.client.on(events.NewMessage)
        async def handler(event):
            if not self.is_running or not self.active_chat_id:
                return
            if event.chat_id == self.active_chat_id:
                sender = await event.get_sender()
                sender_id = event.sender_id
                sender_uname = getattr(sender, 'username', '')
                
                is_target = False
                if self.target_id and sender_id == self.target_id:
                    is_target = True
                elif self.target_username and sender_uname and sender_uname.lower() == self.target_username.lower().replace('@', ''):
                    is_target = True

                if self.on_message_callback:
                    await self.on_message_callback(event, is_target)

    async def send_chunk_ladder(self, chat_id: int, chunks: list, ladder_pause: float, wpm: int, emulator):
        for chunk in chunks:
            if not self.is_running:
                break
            async with self.client.action(chat_id, 'typing'):
                await emulator.sleep_wpm(chunk, wpm)
                await self.client.send_message(chat_id, chunk)
            await asyncio.sleep(ladder_pause)
