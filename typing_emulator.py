import random
from typing import List

NEARBY_KEYS_RU = {
    'й': ['ц', 'ф', 'ы'],
    'ц': ['й', 'у', 'ы', 'в'],
    'у': ['ц', 'к', 'в', 'а'],
    'к': ['у', 'е', 'а', 'п'],
    'е': ['к', 'н', 'п', 'р'],
    'н': ['е', 'г', 'р', 'о'],
    'г': ['н', 'ш', 'о', 'л'],
    'ш': ['г', 'щ', 'л', 'д'],
    'щ': ['ш', 'з', 'д', 'ж'],
    'з': ['щ', 'х', 'ж', 'э'],
    'х': ['з', 'ъ', 'э'],
    'ф': ['й', 'ы', 'я'],
    'ы': ['ф', 'в', 'я', 'ч'],
    'в': ['ы', 'а', 'ч', 'с'],
    'а': ['в', 'п', 'с', 'м'],
    'п': ['а', 'р', 'м', 'и'],
    'р': ['п', 'о', 'и', 'т'],
    'о': ['р', 'л', 'т', 'ь'],
    'л': ['о', 'д', 'ь', 'б'],
    'д': ['л', 'ж', 'б', 'ю'],
    'ж': ['д', 'э', 'ю', 'з'],
    'э': ['ж', 'х', 'ъ'],
    'я': ['ф', 'ы', 'ч'],
    'ч': ['я', 'с', 'в'],
    'с': ['ч', 'м', 'а'],
    'м': ['с', 'и', 'п'],
    'и': ['м', 'т', 'р'],
    'т': ['и', 'ь', 'о'],
    'ь': ['т', 'б', 'л'],
    'б': ['ь', 'ю', 'д'],
    'ю': ['б', 'ж', 'д']
}

PROTECTED_WORDS = {"хуй", "ебало", "пидор", "нах", "нахуй", "рот", "мать", "бля", "блять", "пес", "че", "ты", "я", "те"}

class TypingEmulator:
    @staticmethod
    def apply_typos(text: str, typo_rate: float = 0.07) -> str:
        if typo_rate <= 0:
            return text

        words = text.split()
        result_words = []

        for word in words:
            clean_w = word.lower().strip()
            if clean_w in PROTECTED_WORDS or len(word) <= 3 or any(ch.isdigit() for ch in word):
                result_words.append(word)
                continue

            chars = list(word)
            new_chars = []
            i = 0
            while i < len(chars):
                char = chars[i]
                lower_char = char.lower()

                if random.random() < typo_rate:
                    typo_type = random.choice(["neighbor", "skip", "swap"])
                    if typo_type == "neighbor" and lower_char in NEARBY_KEYS_RU:
                        sub = random.choice(NEARBY_KEYS_RU[lower_char])
                        new_chars.append(sub.upper() if char.isupper() else sub)
                    elif typo_type == "skip" and len(chars) > 4:
                        pass
                    elif typo_type == "swap" and i + 1 < len(chars):
                        new_chars.append(chars[i+1])
                        new_chars.append(char)
                        i += 1
                    else:
                        new_chars.append(char)
                else:
                    new_chars.append(char)
                i += 1

            result_words.append("".join(new_chars))

        return " ".join(result_words)

    @staticmethod
    def chunk_text(text: str, min_words: int = 1, max_words: int = 3) -> List[str]:
        """
        Разбивает текст на короткие обрывки по 1-3 слова, создавая очередь из 15-25 сообщений на залп.
        """
        words = text.split()
        chunks = []
        current = []
        
        for w in words:
            current.append(w)
            target_len = random.randint(min_words, max_words)
            if len(current) >= target_len:
                chunks.append(" ".join(current))
                current = []
        if current:
            chunks.append(" ".join(current))
        return chunks

    @staticmethod
    def calculate_typing_delay(chunk: str, wpm: int = 380) -> float:
        words_count = len(chunk.split())
        delay = (words_count / max(wpm, 30)) * 60.0
        return max(0.01, min(delay, 0.15))
