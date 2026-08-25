import random
import aiohttp
import json
import uuid
import time
from collections import deque
from logger import logger

RYZEN_ZERO_FRAMEWORK = "РОЛЬ: Токсичный дотер-тайпер. Отвечай мгновенно короткой рубленой фразой с матом и оскорблением родни без долгих раздумий."

class DeepSeekAIEngine:
    def __init__(self, base_url: str = "http://localhost:8000/v1", api_key: str = "free-deepseek-api", model: str = "deepseek-chat"):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or "free-deepseek-api"
        self.model = model or "deepseek-chat"
        self.session_id = str(uuid.uuid4())
        self.recent_replies = deque(maxlen=40)

    def reset_session(self):
        self.session_id = str(uuid.uuid4())
        self.recent_replies.clear()

    def update_settings(self, base_url: str, api_key: str, model: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or "free-deepseek-api"
        self.model = model or "deepseek-chat"
        self.reset_session()

    def get_instant_fast_reply(self, text: str) -> str:
        text_lower = text.lower()
        if "123" in text_lower:
            return "123 ты че думаешь я с автотайпером или че мудака кусок блять мать те ебу втопи ебало нахуй пидорас ебаный"
        if any(w in text_lower for w in ["докажи", "пруф", "пруфы", "чит", "софт", "бот"]):
            return "ХАХАХА долбоеб какие читы я тебе мать режу руками ты че пиздюк лови в ебало харчу сын шмары"
        
        bursts = [
            "я тебе щас ебальник сломаю нахуй хули ты мне пишешь тут пидорас ебаный захарканный соси хуй молча",
            "ВХАВХАХАХ слабак ебаный че ты мне пишешь пидораса кусок я тебе щас ебало бить буду хуем сиди терпи",
            "иди нахуй просто пидор ебаный соси пенис мне пидорас захарканный мать те ебал втопи ебало нахуй",
            "че ты там залип нахуй я тебе щас ебало хуем разобью пиши сука быстрее пидорас ебаный мать твою ебал"
        ]
        choices = [f for f in bursts if f[:20] not in self.recent_replies] or bursts
        chosen = random.choice(choices)
        self.recent_replies.append(chosen[:20])
        return chosen

    async def generate_silence_provoke(self, target_name: str) -> str:
        return self.get_instant_fast_reply("молчит")

    async def generate_reply(self, target_name: str, incoming_text: str, is_challenge: bool = False, is_reply_to_other: bool = False, was_silent_before: bool = False, style: str = "aggressive") -> str:
        text_clean = incoming_text.strip()
        if not text_clean or "[ photo" in text_clean.lower():
            text_clean = "скинул фотку"

        endpoint = f"{self.base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": RYZEN_ZERO_FRAMEWORK},
                {"role": "user", "content": f"Отреагируй на сообщение '{text_clean}' жестким матом, оскорблением родни и насмешкой в 10-15 слов без размышлений:"}
            ],
            "max_tokens": 40,
            "temperature": 1.1,
            "stream": False
        }

        try:
            timeout = aiohttp.ClientTimeout(total=0.9)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(endpoint, headers=headers, json=payload) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        reply = data["choices"][0]["message"]["content"].strip()
                        if "</think>" in reply:
                            reply = reply.split("</think>")[-1].strip()
                        if len(reply.split()) >= 3:
                            return reply
        except Exception:
            pass

        return self.get_instant_fast_reply(text_clean)
