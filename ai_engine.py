import random
from openai import AsyncOpenAI
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
        self.client = AsyncOpenAI(base_url=self.base_url, api_key=self.api_key)

    def update_settings(self, base_url: str, api_key: str, model: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or "free-deepseek-api"
        self.model = model or "deepseek-chat"
        self.client = AsyncOpenAI(base_url=self.base_url, api_key=self.api_key)

    async def generate_reply(self, target_name: str, incoming_text: str, style: str = "aggressive") -> str:
        # Быстрый рефлекс на провокацию '123'
        if "123" in incoming_text:
            return f"123 пидорас ебаный {target_name} ты че думаешь я с читом сижу завали ебало нахуй"

        prompt = SYSTEM_PROMPTS.get(style, SYSTEM_PROMPTS["aggressive"]).format(name=target_name)
        
        try:
            logger.info(f"[DEEPSEEK] Requesting response from {self.base_url} (model: {self.model})")
            res = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": incoming_text}
                ],
                max_tokens=120,
                temperature=0.95
            )
            reply = res.choices[0].message.content.strip()
            # Очистка возможных тегов размышлений DeepSeek R1/V3
            if "</think>" in reply:
                reply = reply.split("</think>")[-1].strip()
            return reply if reply else f"ХАХААХ {target_name} ЗАВАЛИ ЕБАЛО"
        except Exception as e:
            logger.error(f"[DEEPSEEK ERROR] {e}")
            fallbacks = [
                f"ХАХААХ ДОЛБОЕБ {target_name} НАХУЙ ХУЛИ ТЫ ТУТ ПИЗДИШЬ ВООБЩЕ",
                f"ЗАКРОЙ ЕБАЛО {target_name} ВЫБЛЯДОК ПОКА Я ТЕБЕ МАТЬ ЕБУ",
                f"АХЫВАХЫАХ )) {target_name} ДОЛБОЕБ ЗАКРОЙ РОТ НАХУЙ ВАХАХАЫ",
                f"ПИДОРАС ЕБАНЫЙ {target_name} ИДИ НАХУЙ ЗАБЛЕВАННЫЙ"
            ]
            return random.choice(fallbacks)
