import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Config:
    api_id: int = int(os.getenv("TG_API_ID", "1234567"))
    api_hash: str = os.getenv("TG_API_HASH", "your_api_hash_here")
    openai_key: str = os.getenv("OPENAI_API_KEY", "")
    session_name: str = "troll_session"
    
    target_username: str = ""
    wpm_rate: int = 380
    ladder_pause: float = 0.6
    min_chunk_words: int = 2
    max_chunk_words: int = 8
    style: str = "aggressive"
    parallel_typing: bool = True
