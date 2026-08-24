import json
import os
from dataclasses import dataclass, asdict
from dotenv import load_dotenv

load_dotenv()

CONFIG_FILE = "config.json"

@dataclass
class AppConfig:
    api_id: int = int(os.getenv("TG_API_ID", "1234567"))
    api_hash: str = os.getenv("TG_API_HASH", "your_api_hash_here")
    
    # DeepSeek / FreeDeepseekAPI
    deepseek_base_url: str = os.getenv("DEEPSEEK_BASE_URL", "http://localhost:8000/v1")
    deepseek_api_key: str = os.getenv("DEEPSEEK_API_KEY", "free-deepseek-api")
    deepseek_model: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    
    session_name: str = "troll_session"
    
    target_username: str = ""
    target_id: int = 0
    selected_chat_id: int = 0
    selected_chat_title: str = ""
    
    wpm_rate: int = 380
    ladder_pause: float = 0.08       # Сверхбыстрая пулеметная пауза между обрывками (80 мс)
    min_chunk_words: int = 1
    max_chunk_words: int = 3
    style: str = "aggressive"
    parallel_typing: bool = True
    reflex_123: bool = True

    @classmethod
    def load(cls) -> "AppConfig":
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return cls(**data)
            except Exception:
                pass
        return cls()

    def save(self):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(asdict(self), f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"[ERROR] Failed to save config: {e}")
