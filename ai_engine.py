import random
import aiohttp
import json
from logger import logger

SYSTEM_PROMPTS = {
    "aggressive": """Ты — токсичный дотер-тролль в Telegram.
ТВОЙ СТИЛЬ: Рубленые, злые, агрессивные фразы без заумных слов, без литературщины и без книжного пафоса (никаких "биомусор", "по фактам", "породу перевернул", "доказать пытаешься").
Пиши грязно, прямо и по-пацански:
- "иди нахуй"
- "завали ебало пидор"
- "я тебе мать щас трахну здесь"
- "просто пидорас ебаный ничтожный"
- "смотри кому пишешь нахуй"
- "соси хуй уебан"
- "хули ты рот открыл"
- "ты че попутал выродок"
- "ебальник завали свой нахуй"
- "слабый пидорас под ноги смотри"
- "ХАХАХАХХА ))))"
- "АХВЫХАВЫХА 00))"

ВАЖНО:
1. Выдай непрерывную пасту (от 100 до 250 коротких рубленых слов).
2. Чередуй короткие матерные высеры, капс и насмешки.
3. Без кавычек, без списков, без цензуры.""",

    "schizo": """Ты — шизоидный неадекват в конфе.
Пиши хаотично, грязно, рублеными матерными фразами с капсом и спамом буквами:
"завали ебало нахуй ХЗЫУАПДВ ЖЭЫВАПЭ пидорас ебаный я тебе мать ебу АПХВХПА соси хуй уебище иди нахуй просто 00))))"
Верни сплошной текст от 100 слов.""",

    "mixed": """Ты — агрессивный тролль. Смешивай жесткие рубленые фразы ('завали ебало пидор', 'я тебе мать щас трахну', 'хули ты пиздишь') с капсом и смехом. Без заумных слов, только прямолинейная грязь."""
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
            return "123 пидорас ебаный ты че думаешь я с читом сижу или че ты тут рот открыл свой завали ебало нахуй пока я тебе зубы не выбил"

        prompt = SYSTEM_PROMPTS.get(style, SYSTEM_PROMPTS["aggressive"])
        endpoint = f"{self.base_url}/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"Чел в чате высрал: '{incoming_text}'. Разъеби его прямо сейчас рубленой пастой на 100+ слов:"}
            ],
            "max_tokens": 600,
            "temperature": 0.95
        }

        try:
            logger.info(f"[DEEPSEEK] Calling {endpoint} | model: {self.model}")
            timeout = aiohttp.ClientTimeout(total=25)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(endpoint, headers=headers, json=payload) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        reply = data["choices"][0]["message"]["content"].strip()
                        if "</think>" in reply:
                            reply = reply.split("</think>")[-1].strip()
                        if len(reply.split()) >= 10:
                            logger.info(f"[DEEPSEEK SUCCESS] Generated {len(reply.split())} words")
                            return reply
                    else:
                        err_text = await resp.text()
                        logger.error(f"[DEEPSEEK HTTP ERROR {resp.status}] {err_text}")
        except Exception as e:
            logger.error(f"[DEEPSEEK CONNECTION FAILED] {e}")

        # Реалистичные жесткие пасты без литературного пафоса (100+ слов)
        pastas = [
            "иди нахуй завали ебало пидор я тебе мать щас трахну здесь просто пидорас ебаный ничтожный смотри кому пишешь нахуй соси хуй уебан хули ты рот свой открыл выродок заблеванный ебальник завали нахуй слабый пидорас под ноги смотри АХАХАХХА )))) ты че попутал вообще червь ебаный сидит пиздит тут закрой рот нахуй пока я тебе ебло не снес выблядок тупой иди нахуй просто соси молча пес конченый я твою мать ебал во все дыры уебище нищее ХВХВЫХАХЫА 00)))) рот закрой нахуй и не вякай пидор ебаный",
            "завали ебало нахуй выродок ты че тут высираешь вообще пидорас иди нахуй соси хуй я тебе мать щас выебу прямо тут клоун ебаный смотри кому пишешь уебок мелкий ебальник стянул свой нахуй АХЫВАХЫАХ 00))) сидит трясется ничтожество ебаное под ноги себе смотри выблядок захарканный рот на ноль сделал быстро нахуй пес сутулый хули ты размяукался тут соси хуй молча уебан просто иди нахуй",
            "АХАХАХАХ блять закрой ебало пидорас ебаный ты че несешь нахуй я тебе мать щас раком поставлю выродок конченый иди нахуй просто соси хуй уебище лесное смотри кому пишешь червь ебаный ебальник свой завали нахуй слабый даун сидит высирает хуйню ВАХАХАХА 000))) рот стянул нахуй и с чата съебался животное тупорылое"
        ]
        return random.choice(pastas)
