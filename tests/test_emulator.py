import unittest
from typing_emulator import TypingEmulator

class TestTypingEmulator(unittest.TestCase):
    def test_chunking(self):
        text = "РАЗ ДВА ТРИ ЧЕТЫРЕ ПЯТЬ ШЕСТЬ СЕМЬ ВОСЕМЬ ДЕВЯТЬ ДЕСЯТЬ"
        chunks = TypingEmulator.chunk_text(text, min_words=2, max_words=4)
        self.assertTrue(len(chunks) >= 2)
        total_words = sum(len(c.split()) for c in chunks)
        self.assertEqual(total_words, 10)

    def test_wpm_calculation(self):
        chunk = "ОДИН ДВА ТРИ ЧЕТЫРЕ"
        # 4 words at 240 WPM => (4 / 240) * 60 = 1.0 sec
        delay = TypingEmulator.calculate_typing_delay(chunk, wpm=240)
        self.assertAlmostEqual(delay, 1.0, places=2)

if __name__ == "__main__":
    unittest.main()
