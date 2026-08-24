import asyncio
import customtkinter as ctk
from config import Config
from ai_engine import AIEngine
from typing_emulator import TypingEmulator
from telegram_handler import TelegramHandler

# Monkeytype dark-yellow theme
ctk.set_appearance_mode("dark")
BG_COLOR = "#323437"
MAIN_COLOR = "#e2b714"
SUB_ALT = "#2c2e31"
TEXT_COLOR = "#d1d0c5"

class TrollBotApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("trolltype // Telegram Engine v2.4")
        self.geometry("980x640")
        self.configure(fg_color=BG_COLOR)

        self.cfg = Config()
        self.ai = AIEngine(self.cfg.openai_key)
        self.tg = TelegramHandler(self.cfg.api_id, self.cfg.api_hash)
        self.emulator = TypingEmulator()

        self._build_ui()

    def _build_ui(self):
        # Header
        head = ctk.CTkFrame(self, fg_color="transparent")
        head.pack(fill="x", padx=24, pady=12)
        
        title = ctk.CTkLabel(head, text="⚡ trolltype engine", font=("JetBrains Mono", 20, "bold"), text_color=MAIN_COLOR)
        title.pack(side="left")

        # Config Pill Bar
        pill = ctk.CTkFrame(self, fg_color=SUB_ALT, corner_radius=8)
        pill.pack(fill="x", padx=24, pady=6)

        self.wpm_slider = ctk.CTkSlider(pill, from_=30, to_=450, number_of_steps=42, command=self._on_wpm_change, progress_color=MAIN_COLOR)
        self.wpm_slider.set(self.cfg.wpm_rate)
        self.wpm_slider.pack(side="left", padx=16, pady=8)

        self.wpm_lbl = ctk.CTkLabel(pill, text=f"{self.cfg.wpm_rate} WPM", font=("JetBrains Mono", 13, "bold"), text_color=MAIN_COLOR)
        self.wpm_lbl.pack(side="left", padx=8)

        self.status_lbl = ctk.CTkLabel(pill, text="● READY", font=("JetBrains Mono", 12), text_color="#646669")
        self.status_lbl.pack(side="right", padx=16)

        # Log & Arena Box
        self.log_box = ctk.CTkTextbox(self, fg_color=SUB_ALT, text_color=TEXT_COLOR, font=("JetBrains Mono", 13), wrap="word")
        self.log_box.pack(fill="both", expand=True, padx=24, pady=12)
        self.log_box.insert("end", "[SYSTEM] trolltype initialized. Ready to launch.\n")

        # Controls Bottom
        ctrl = ctk.CTkFrame(self, fg_color="transparent")
        ctrl.pack(fill="x", padx=24, pady=12)

        self.target_entry = ctk.CTkEntry(ctrl, placeholder_text="Target username (e.g. @KotLeopolld)", fg_color=SUB_ALT, text_color=TEXT_COLOR, width=280)
        self.target_entry.pack(side="left", padx=6)

        self.btn_toggle = ctk.CTkButton(ctrl, text="▶ START TROLLING", fg_color=MAIN_COLOR, text_color=BG_COLOR, font=("JetBrains Mono", 13, "bold"), command=self.toggle_engine)
        self.btn_toggle.pack(side="right", padx=6)

    def _on_wpm_change(self, val):
        self.cfg.wpm_rate = int(val)
        self.wpm_lbl.configure(text=f"{self.cfg.wpm_rate} WPM")

    def toggle_engine(self):
        if not self.tg.is_running:
            self.tg.is_running = True
            self.tg.target_username = self.target_entry.get().strip()
            self.status_lbl.configure(text="● RUNNING", text_color=MAIN_COLOR)
            self.btn_toggle.configure(text="■ STOP ENGINE", fg_color="#ca4754")
            self.log_box.insert("end", f"[ENGINE] Active on target: {self.tg.target_username} @ {self.cfg.wpm_rate} WPM\n")
        else:
            self.tg.is_running = False
            self.status_lbl.configure(text="○ STOPPED", text_color="#646669")
            self.btn_toggle.configure(text="▶ START TROLLING", fg_color=MAIN_COLOR)
            self.log_box.insert("end", "[ENGINE] Stopped.\n")

if __name__ == "__main__":
    app = TrollBotApp()
    app.mainloop()
