import asyncio
import random
from typing import List

class TypingEmulator:
    @staticmethod
    def chunk_text(text: str, min_words: int = 1, max_words: int = 3) -> List[str]:
        """
        Разбивает текст на динамические обрывки по 1-3 слова.
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
        """
        Быстрый расчет задержки: при 350-450 WPM задержка составляет 0.02-0.08 сек.
        """
        words_count = len(chunk.split())
        # (words / WPM) * 60 seconds
        delay = (words_count / max(wpm, 30)) * 60.0
        return max(0.02, min(delay, 0.4))
