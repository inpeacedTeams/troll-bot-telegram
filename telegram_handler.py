import asyncio
import traceback
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError, SessionPasswordNeededError
from typing import Callable, Optional, List, Dict
from logger import logger

class TelegramHandler:
    def __init__(self, api_id: int, api_hash: str, session_name: str = "troll_session"):
        self.api_id = api_id
        self.api_hash = api_hash
        self.session_name = session_name
        self.client: Optional[TelegramClient] = None
        self.phone_code_hash: Optional[str] = None
        
        self.target_id: Optional[int] = None
        self.target_username: Optional[str] = None
        self.active_chat_id: Optional[int] = None
        self.is_running = False
        
        self.on_message_callback: Optional[Callable] = None
        self.on_typing_callback: Optional[Callable] = None
        self.on_log_callback: Optional[Callable] = None

    def log(self, text: str, level: str = "INFO"):
        if level == "ERROR":
            logger.error(text)
        else:
            logger.info(text)
        if self.on_log_callback:
            self.on_log_callback(text)

    async def init_client(self):
        if not self.client:
            self.client = TelegramClient(self.session_name, self.api_id, self.api_hash)
            await self.client.connect()

    async def is_authorized(self) -> bool:
        await self.init_client()
        return await self.client.is_user_authorized()

    async def send_code(self, phone: str) -> str:
        await self.init_client()
        res = await self.client.send_code_request(phone)
        self.phone_code_hash = res.phone_code_hash
        return self.phone_code_hash

    async def sign_in_code(self, phone: str, code: str, password: Optional[str] = None):
        try:
            await self.client.sign_in(phone=phone, code=code, phone_code_hash=self.phone_code_hash)
        except SessionPasswordNeededError:
            if password:
                await self.client.sign_in(password=password)
            else:
                raise

    async def get_dialogs_list(self) -> List[Dict]:
        await self.init_client()
        dialogs = []
        async for d in self.client.iter_dialogs(limit=50):
            dialogs.append({
                "id": d.id,
                "title": d.title or d.name or "Unnamed",
                "is_group": d.is_group,
                "is_channel": d.is_channel
            })
        return dialogs

    async def get_recent_messages(self, chat_id: int, limit: int = 40) -> List[Dict]:
        await self.init_client()
        messages = []
        async for msg in self.client.iter_messages(chat_id, limit=limit):
            sender = await msg.get_sender()
            sender_name = getattr(sender, 'first_name', '') or ''
            last_name = getattr(sender, 'last_name', '') or ''
            if last_name:
                sender_name += f" {last_name}"
            username = getattr(sender, 'username', '')
            
            messages.append({
                "id": msg.id,
                "sender_id": msg.sender_id,
                "sender_name": sender_name.strip() or "Anonymous",
                "username": username or "",
                "text": msg.text or "[media/service]"
            })
        return messages

    def bind_listeners(self, on_message: Callable, on_typing: Optional[Callable] = None):
        self.on_message_callback = on_message
        self.on_typing_callback = on_typing

        @self.client.on(events.NewMessage)
        async def message_handler(event):
            if not self.is_running or not self.active_chat_id:
                return
            if event.chat_id != self.active_chat_id:
                return

            sender = await event.get_sender()
            sender_id = event.sender_id
            username = (getattr(sender, 'username', '') or '').lower()
            
            is_target = False
            if self.target_id and sender_id == self.target_id:
                is_target = True
            elif self.target_username and username == self.target_username.lower().replace('@', ''):
                is_target = True

            if self.on_message_callback:
                await self.on_message_callback(event, is_target, sender)

        @self.client.on(events.UserUpdate)
        async def user_typing_handler(event):
            if not self.is_running or not self.active_chat_id:
                return
            if event.typing and self.on_typing_callback:
                if (self.target_id and event.user_id == self.target_id):
                    await self.on_typing_callback(event.user_id)

    async def send_ladder_chunks(self, chat_id: int, chunks: List[str], ladder_pause: float, wpm: int, emulator):
        for idx, chunk in enumerate(chunks):
            if not self.is_running:
                break
            try:
                async with self.client.action(chat_id, 'typing'):
                    await emulator.sleep_wpm(chunk, wpm)
                    await self.client.send_message(chat_id, chunk)
                    self.log(f"[SENT #{idx+1}] {chunk}")
                await asyncio.sleep(ladder_pause)
            except FloodWaitError as fwe:
                self.log(f"[FLOOD WAIT] Need to wait {fwe.seconds}s", level="ERROR")
                await asyncio.sleep(fwe.seconds)
            except Exception as e:
                self.log(f"[ERROR SENDING] {e}", level="ERROR")
