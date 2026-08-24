import random
import aiohttp
import json
from logger import logger

SYSTEM_PROMPTS = {
    "aggressive": """Ты — ультра-агрессивный тролль в Telegram.
Твоя цель: максимально жестко унизить, обоссать и растоптать собеседника с ником {name}.
Используй отборный русский мат, капс, насмешки, фразы 'я тебе мать ебал', 'завали ебало', 'выродок конченый', 'заблеванный хуесос'.
Верни ТОЛЬКО готовый текст ответа без кавычек, вводных слов и метаданных.""",

    "schizo": """Ты — шизоидный неадекват в Telegram.
Твоя цель: спамить капсом, ломаными буквами, смехом (АХВХАХЫАХ 00)))), матом и полным бредом в адрес {name}.
Верни ТОЛЬКО текст без объяснений.""",

    "mixed": """Ты — дерзкий токсичный тролль. Смешивай агрессивные панчи с шизоидным угаром и капсом в адрес {name}."""
}

class DeepSeekAIEngine:
    def __init__(self, base_url: str = "http://localhost:8000/v1", api_key: str = "free-deepseek-api", model: str = "deepseek-chat"):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or "free-deepseek-api"
        self.model = model or "deepseek-chat"

    def update_settings(self, base_url: str, api_key: str, model: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or "free-deepseek-api"
        self.model = model or "deepseek-chat"

    async def generate_reply(self, target_name: str, incoming_text: str, style: str = "aggressive") -> str:
        # Быстрый рефлекс на '123'
        if "123" in incoming_text:
            return f"123 пидорас ебаный {target_name} ты че думаешь я с читом сижу завали ебало нахуй"

        prompt = SYSTEM_PROMPTS.get(style, SYSTEM_PROMPTS["aggressive"]).format(name=target_name)
        endpoint = f"{self.base_url}/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": incoming_text}
            ],
            "max_tokens": 120,
            "temperature": 0.95
        }

        try:
            logger.info(f"[DEEPSEEK] POST {endpoint} (model: {self.model})")
            timeout = aiohttp.ClientTimeout(total=20)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(endpoint, headers=headers, json=payload) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        reply = data["choices"][0]["message"]["content"].strip()
                        # Очистка возможных тегов размышлений DeepSeek R1/V3
                        if "</think>" in reply:
                            reply = reply.split("</think>")[-1].strip()
                        return reply if reply else f"ХАХААХ {target_name} ЗАВАЛИ ЕБАЛО"
                    else:
                        err_body = await resp.text()
                        logger.error(f"[DEEPSEEK HTTP {resp.status}] {err_body}")
        except Exception as e:
            logger.error(f"[DEEPSEEK ERROR] {e}")

        # Fallback при ошибке соединения
        fallbacks = [
            f"ХАХААХ ДОЛБОЕБ {target_name} НАХУЙ ХУЛИ ТЫ ТУТ ПИЗДИШЬ ВООБЩЕ",
            f"ЗАКРОЙ ЕБАЛО {target_name} ВЫБЛЯДОК ПОКА Я ТЕБЕ МАТЬ ЕБУ",
            f"АХЫВАХЫАХ )) {target_name} ДОЛБОЕБ ЗАКРОЙ РОТ НАХУЙ ВАХАХАЫ",
            f"ПИДОРАС ЕБАНЫЙ {target_name} ИДИ НАХУЙ ЗАБЛЕВАННЫЙ"
        ]
        return random.choice(fallbacks)
