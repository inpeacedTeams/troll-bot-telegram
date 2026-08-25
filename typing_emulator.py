import random
from typing import List

PROTECTED_WORDS = {"хуй", "ебало", "пидор", "нах", "нахуй", "рот", "мать", "бля", "блять", "пес", "че", "ты", "я", "те"}

class TypingEmulator:
    @staticmethod
    def apply_typos(text: str, typo_rate: float = 0.02) -> str:
        return text

    @staticmethod
    def chunk_text(text: str, min_words: int = 2, max_words: int = 3) -> List[str]:
        words = text.split()
        chunks = []
        current = []
        
        for w in words:
            current.append(w)
            if len(current) >= random.randint(min_words, max_words):
                chunks.append(" ".join(current))
                current = []
        if current:
            chunks.append(" ".join(current))
        return chunks

    @staticmethod
    def calculate_typing_delay(chunk: str, wpm: int = 800) -> float:
        return 0.01
