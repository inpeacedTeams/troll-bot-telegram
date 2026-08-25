import random
import aiohttp
import json
import uuid
import time
from collections import deque
from logger import logger

RYZEN_ZERO_FRAMEWORK = "РОЛЬ: Токсичный дотер-тайпер без панчей. Только грязный матерный базар в лоб, жесткие наезды на родню и мгновенная реакция на каждое слово."

class DeepSeekAIEngine:
    def __init__(self, base_url: str = "http://localhost:8000/v1", api_key: str = "free-deepseek-api", model: str = "deepseek-chat"):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or "free-deepseek-api"
        self.model = model or "deepseek-chat"
        self.session_id = str(uuid.uuid4())
        self.recent_replies = deque(maxlen=60)

    def reset_session(self):
        self.session_id = str(uuid.uuid4())
        self.recent_replies.clear()

    def update_settings(self, base_url: str, api_key: str, model: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or "free-deepseek-api"
        self.model = model or "deepseek-chat"
        self.reset_session()

    def get_instant_fast_reply(self, text: str) -> str:
        adjectives = ["тупой", "конченый", "выродок", "нищий", "гнилой", "зассаный", "опущенный", "дырявый", "убогий", "слабый"]
        nouns = ["пидорас", "долбоеб", "сын шлюхи", "шалава", "мудак", "клоун", "биомусор", "выблядок", "собака", "шмарововоз"]
        actions = [
            "мать твою в канаве ебал", 
            "отец твой сапоги лижет под залупой", 
            "ты нахуй слова путаешь от страха", 
            "ебало свое стяни и не скули", 
            "ты подзаборный уродец без прав на голос", 
            "я твой рот топтал с ноги", 
            "соси хуй молча ублюдок ебаный"
        ]
        
        gen = f"{random.choice(adjectives)} {random.choice(nouns)} {random.choice(actions)}"
        while gen[:25] in self.recent_replies:
            gen = f"{random.choice(adjectives)} {random.choice(nouns)} {random.choice(actions)}"
        
        self.recent_replies.append(gen[:25])
        return gen

    async def generate_silence_provoke(self, target_name: str) -> str:
        return self.get_instant_fast_reply("молчит")

    async def generate_reply(self, target_name: str, incoming_text: str, is_challenge: bool = False, is_reply_to_other: bool = False, was_silent_before: bool = False, style: str = "aggressive") -> str:
        text_clean = incoming_text.strip()
        if not text_clean or "[ photo" in text_clean.lower():
            text_clean = "скинул хуйню"

        endpoint = f"{self.base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        prompt = f"Оппонент написал: '{text_clean}'. Выдай уникальный матерный наезд без панчей, оскорбляя его и его матуху на 8-12 слов на лету:"
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": RYZEN_ZERO_FRAMEWORK},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 30,
            "temperature": 1.4,
            "stream": False
        }

        try:
            timeout = aiohttp.ClientTimeout(total=0.7)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(endpoint, headers=headers, json=payload) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        reply = data["choices"][0]["message"]["content"].strip()
                        if "</think>" in reply:
                            reply = reply.split("</think>")[-1].strip()
                        if len(reply.split()) >= 3 and reply[:25] not in self.recent_replies:
                            self.recent_replies.append(reply[:25])
                            return reply
        except Exception:
            pass

        return self.get_instant_fast_reply(text_clean)
