import random
from openai import AsyncOpenAI

SYSTEM_PROMPTS = {
    "aggressive": """Ты — ультра-агрессивный тролль в Telegram.
Твоя цель: жестко унизить и раздавить собеседника с ником {name}.
Используй мат, капс, насмешки, фразы 'я тебе мать ебал', 'завали ебало', 'выродок конченый'.
Верни ТОЛЬКО готовый текст ответа без кавычек и метаданных.""",

    "schizo": """Ты — шизоидный неадекват в Telegram.
Твоя цель: спамить капсом, ломаными буквами, смехом (АХВХАХЫАХ 00)))), матом и полным бредом в адрес {name}.
Верни ТОЛЬКО текст без метаданных.""",

    "mixed": """Ты — дерзкий тролль. Смешивай агрессивные панчи с шизоидным угаром и капсом в адрес {name}."""
}

class AIEngine:
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key) if api_key else None

    async def generate_reply(self, target_name: str, incoming_text: str, style: str = "aggressive") -> str:
        if "123" in incoming_text:
            return f"123 пидорас ебаный {target_name} ты че думаешь я с читом сижу завали ебало нахуй"

        if not self.client:
            fallbacks = [
                f"ХАХААХ ДОЛБОЕБ {target_name} НАХУЙ ХУЛИ ТЫ ТУТ ПИЗДИШЬ ВООБЩЕ",
                f"ЗАКРОЙ ЕБАЛО {target_name} ВЫБЛЯДОК ПОКА Я ТЕБЕ МАТЬ ЕБУ",
                f"АХЫВАХЫАХ )) {target_name} ДОЛБОЕБ ЗАКРОЙ РОТ НАХУЙ ВАХАХАЫ",
                f"ПИДОРАС ЕБАНЫЙ {target_name} ИДИ НАХУЙ ЗАБЛЕВАННЫЙ"
            ]
            return random.choice(fallbacks)

        prompt = SYSTEM_PROMPTS.get(style, SYSTEM_PROMPTS["aggressive"]).format(name=target_name)
        try:
            res = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": incoming_text}
                ],
                max_tokens=100,
                temperature=0.9
            )
            return res.choices[0].message.content.strip()
        except Exception:
            return f"ХАХААХ ДОЛБОЕБ {target_name} НАХУЙ ЗАКРОЙ ЕБАЛО"
