import asyncio
import random
from typing import List

class TypingEmulator:
    @staticmethod
    def chunk_text(text: str, min_words: int = 1, max_words: int = 3) -> List[str]:
        """
        Разбивает длинный текст строго лесенкой по 1-3 слова в сообщении.
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
        return max(0.1, delay)

    @staticmethod
    async def sleep_wpm(chunk: str, wpm: int = 380):
        delay = TypingEmulator.calculate_typing_delay(chunk, wpm)
        await asyncio.sleep(delay)
