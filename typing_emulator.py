import asyncio
import random
from typing import List

class TypingEmulator:
    @staticmethod
    def chunk_text(text: str, min_words: int = 2, max_words: int = 6) -> List[str]:
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
        # (words / WPM) * 60 seconds
        delay = (words_count / max(wpm, 30)) * 60.0
        return max(0.15, delay)

    @staticmethod
    async def sleep_wpm(chunk: str, wpm: int = 380):
        delay = TypingEmulator.calculate_typing_delay(chunk, wpm)
        await asyncio.sleep(delay)
