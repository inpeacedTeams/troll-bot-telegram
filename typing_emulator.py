import random
from typing import List

NEARBY_KEYS_RU = {
    'й': ['ц', 'ф', 'ы', '1', '2'],
    'ц': ['й', 'у', 'ы', 'в', '2', '3'],
    'у': ['ц', 'к', 'в', 'а', '3', '4'],
    'к': ['у', 'е', 'а', 'п', '4', '5'],
    'е': ['к', 'н', 'п', 'р', '5', '6'],
    'н': ['е', 'г', 'р', 'о', '6', '7'],
    'г': ['н', 'ш', 'о', 'л', '7', '8'],
    'ш': ['г', 'щ', 'л', 'д', '8', '9'],
    'щ': ['ш', 'з', 'д', 'ж', '9', '0'],
    'з': ['щ', 'х', 'ж', 'э', '0', '-'],
    'х': ['з', 'ъ', 'э'],
    'ъ': ['х', 'ж', 'э'],
    'ф': ['й', 'ы', 'я'],
    'ы': ['ф', 'в', 'я', 'ч', 'ц'],
    'в': ['ы', 'а', 'ч', 'с', 'у', 'ц'],
    'а': ['в', 'п', 'с', 'м', 'к', 'у'],
    'п': ['а', 'р', 'м', 'и', 'е', 'к'],
    'р': ['п', 'о', 'и', 'т', 'н', 'е'],
    'о': ['р', 'л', 'т', 'ь', 'г', 'н'],
    'л': ['о', 'д', 'ь', 'б', 'ш', 'г'],
    'д': ['л', 'ж', 'б', 'ю', 'щ', 'ш'],
    'ж': ['д', 'э', 'ю', 'з', 'щ'],
    'э': ['ж', 'х', 'ъ'],
    'я': ['ф', 'ы', 'ч'],
    'ч': ['я', 'с', 'в', 'ы'],
    'с': ['ч', 'м', 'а', 'в'],
    'м': ['с', 'и', 'п', 'а'],
    'и': ['м', 'т', 'р', 'п'],
    'т': ['и', 'ь', 'о', 'р'],
    'ь': ['т', 'б', 'л', 'о'],
    'б': ['ь', 'ю', 'д', 'л'],
    'ю': ['б', 'ж', 'д']
}

class TypingEmulator:
    @staticmethod
    def apply_typos(text: str, typo_rate: float = 0.15) -> str:
        if typo_rate <= 0:
            return text

        words = text.split()
        result_words = []

        for word in words:
            if any(ch.isdigit() for ch in word) or len(word) <= 2:
                result_words.append(word)
                continue

            chars = list(word)
            new_chars = []
            i = 0
            while i < len(chars):
                char = chars[i]
                lower_char = char.lower()

                if random.random() < typo_rate:
                    typo_type = random.choice(["neighbor", "skip", "swap", "double"])
                    if typo_type == "neighbor" and lower_char in NEARBY_KEYS_RU:
                        sub = random.choice(NEARBY_KEYS_RU[lower_char])
                        new_chars.append(sub.upper() if char.isupper() else sub)
                    elif typo_type == "skip" and len(chars) > 3:
                        pass
                    elif typo_type == "swap" and i + 1 < len(chars):
                        new_chars.append(chars[i+1])
                        new_chars.append(char)
                        i += 1
                    elif typo_type == "double":
                        new_chars.append(char)
                        new_chars.append(char)
                    else:
                        new_chars.append(char)
                else:
                    new_chars.append(char)
                i += 1

            result_words.append("".join(new_chars))

        return " ".join(result_words)

    @staticmethod
    def chunk_text(text: str, min_words: int = 2, max_words: int = 4) -> List[str]:
        """
        Разбивает текст на плотные обрывки по 2-4 слова, чтобы залп укладывался в 6-10 сообщений.
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
