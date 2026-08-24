import asyncio
import traceback
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError, SessionPasswordNeededError, FloodError
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
        
        # Счетчик отправленных сообщений для периодического тега (@username раз в N сообщений)
        self.total_sent_count: int = 0
        self.mention_every_n: int = 15
        
        self.current_stream_task: Optional[asyncio.Task] = None
        self.auto_bait_task: Optional[asyncio.Task] = None
        
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
            if event.out:
                return

            sender = await event.get_sender()
            sender_id = event.sender_id
            username = (getattr(sender, 'username', '') or '').lower().replace('@', '')
            first_name = (getattr(sender, 'first_name', '') or '').lower()
            
            is_target = False
            if self.target_id and sender_id == self.target_id:
                is_target = True
            elif self.target_username:
                target_clean = self.target_username.lower().replace('@', '')
                if username and username == target_clean:
                    is_target = True
                elif first_name and target_clean in first_name:
                    is_target = True

            if self.on_message_callback:
                if self.current_stream_task and not self.current_stream_task.done():
                    self.current_stream_task.cancel()
                    self.log(f"[INTERRUPT] Target spoke (@{username}), firing fresh counter-burst!")

                self.current_stream_task = asyncio.create_task(self.on_message_callback(event, is_target, sender))

    async def send_ladder_chunks(self, chat_id: int, chunks: List[str], ladder_pause: float, wpm: int, emulator, target_mention: Optional[str] = None):
        safe_chunks = chunks[:12]
        
        # Проверяем, нужно ли добавить тег @username в начало первого сообщения
        if safe_chunks and target_mention:
            clean_tag = target_mention.strip()
            if clean_tag and not clean_tag.startswith('@'):
                clean_tag = f"@{clean_tag}"
            
            # Если счетчик кратен mention_every_n (или это первый залп)
            if self.total_sent_count == 0 or (self.total_sent_count % self.mention_every_n == 0):
                safe_chunks[0] = f"{clean_tag} {safe_chunks[0]}"
                self.log(f"[TAGGING TARGET] Added mention {clean_tag} to burst header")

        for idx, chunk in enumerate(safe_chunks):
            if not self.is_running:
                break
            try:
                await asyncio.sleep(max(0.35, ladder_pause))
                await self.client.send_message(chat_id, chunk)
                self.total_sent_count += 1
                self.log(f"[SENT #{idx+1}/{len(safe_chunks)}] (Total sent: {self.total_sent_count}) {chunk}")

            except asyncio.CancelledError:
                self.log("[INTERRUPTED] Stream cancelled by fresh message.")
                break
            except FloodWaitError as fwe:
                self.log(f"[FLOOD WAIT] Telegram asked to wait {fwe.seconds}s", level="ERROR")
                await asyncio.sleep(fwe.seconds + 1)
                break
            except Exception as e:
                self.log(f"[RATE/SEND ERROR] {e}", level="ERROR")
                await asyncio.sleep(1.0)
                break
