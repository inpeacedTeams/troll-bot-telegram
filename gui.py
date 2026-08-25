import sys
import os
import asyncio
import threading
import time
import customtkinter as ctk
from datetime import datetime

from config import AppConfig
from logger import logger
from ai_engine import DeepSeekAIEngine
from typing_emulator import TypingEmulator
from telegram_handler import TelegramHandler
from animator import SmoothAnimator

ctk.set_appearance_mode("dark")
BG = "#323437"
MAIN = "#e2b714"
SUB_ALT = "#2c2e31"
TEXT = "#d1d0c5"
SUB = "#646669"
ERROR = "#ca4754"

class AnimatedPillButton(ctk.CTkButton):
    def __init__(self, master, text, command, **kwargs):
        super().__init__(
            master,
            text=text,
            width=88,
            height=30,
            corner_radius=6,
            font=("JetBrains Mono", 12, "bold"),
            command=command,
            fg_color="transparent",
            text_color=SUB,
            hover_color=SUB_ALT,
            **kwargs
        )
        self.is_active = False

    def set_active(self, active: bool, animate=True):
        self.is_active = active
        if active:
            if animate:
                SmoothAnimator.animate(
                    self, 0.0, 1.0, duration_ms=180, steps=12,
                    update_callback=lambda p: self.configure(fg_color=MAIN, text_color=BG)
                )
            else:
                self.configure(fg_color=MAIN, text_color=BG)
        else:
            self.configure(fg_color="transparent", text_color=SUB)

class TrollTypeDesktopApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("trolltype // Zero-Latency React Engine v4.7")
        self.geometry("1080x780")
        self.minsize(920, 640)
        self.configure(fg_color=BG)

        self.cfg = AppConfig.load()
        self.ai = DeepSeekAIEngine(
            base_url=self.cfg.deepseek_base_url,
            api_key=self.cfg.deepseek_api_key,
            model=self.cfg.deepseek_model
        )
        self.emulator = TypingEmulator()
        self.tg = TelegramHandler(self.cfg.api_id, self.cfg.api_hash, self.cfg.session_name)
        self.tg.on_log_callback = self.append_log
        self.tg.mention_every_n = self.cfg.mention_frequency

        self.target_mode_all = False
        self.current_tab = None
        self.current_typo_rate = 0.06
        self.non_stop_running = True
        
        self.current_ai_task: Optional[asyncio.Task] = None
        
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._run_async_loop, daemon=True)
        self.thread.start()

        self._build_ui()
        self.async_call(self._check_initial_auth())

    def _run_async_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def async_call(self, coro):
        return asyncio.run_coroutine_threadsafe(coro, self.loop)

    def _build_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=28, pady=14)

        logo = ctk.CTkLabel(header, text="⚡ trolltype", font=("JetBrains Mono", 22, "bold"), text_color=MAIN)
        logo.pack(side="left")

        ai_tag = ctk.CTkLabel(header, text="v4.7 sub-second instant react engine", font=("JetBrains Mono", 11), text_color=SUB)
        ai_tag.pack(side="left", padx=12)

        self.lbl_status = ctk.CTkLabel(header, text="AUTH: CHECKING...", font=("JetBrains Mono", 12), text_color=SUB)
        self.lbl_status.pack(side="right")

        self.pill_bar = ctk.CTkFrame(self, fg_color=SUB_ALT, corner_radius=8, height=44)
        self.pill_bar.pack(fill="x", padx=28, pady=4)

        self.btn_tab_auth = AnimatedPillButton(self.pill_bar, "auth", lambda: self.show_tab("auth"))
        self.btn_tab_auth.pack(side="left", padx=4, pady=7)

        self.btn_tab_deepseek = AnimatedPillButton(self.pill_bar, "deepseek", lambda: self.show_tab("deepseek"))
        self.btn_tab_deepseek.pack(side="left", padx=4, pady=7)

        self.btn_tab_target = AnimatedPillButton(self.pill_bar, "target", lambda: self.show_tab("target"))
        self.btn_tab_target.pack(side="left", padx=4, pady=7)

        self.btn_tab_arena = AnimatedPillButton(self.pill_bar, "live arena", lambda: self.show_tab("arena"))
        self.btn_tab_arena.pack(side="left", padx=4, pady=7)

        self.lbl_wpm_val = ctk.CTkLabel(self.pill_bar, text=f"{self.cfg.wpm_rate} WPM", font=("JetBrains Mono", 13, "bold"), text_color=MAIN)
        self.lbl_wpm_val.pack(side="right", padx=12)

        self.wpm_slider = ctk.CTkSlider(self.pill_bar, from_=30, to=450, number_of_steps=42, progress_color=MAIN, command=self._on_wpm_slide)
        self.wpm_slider.set(self.cfg.wpm_rate)
        self.wpm_slider.pack(side="right", padx=8)

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=28, pady=12)

        self._init_auth_tab()
        self._init_deepseek_tab()
        self._init_target_tab()
        self._init_arena_tab()

        self.show_tab("arena", animate=False)

    def _init_auth_tab(self):
        self.tab_auth = ctk.CTkFrame(self.container, fg_color=SUB_ALT, corner_radius=10)
        
        lbl = ctk.CTkLabel(self.tab_auth, text="Telegram API & Authentication", font=("JetBrains Mono", 18, "bold"), text_color=MAIN)
        lbl.pack(pady=(16, 6))

        desc = ctk.CTkLabel(self.tab_auth, text="Укажи API ID и API Hash с my.telegram.org (код приходит в официальный клиент Telegram):", font=("JetBrains Mono", 11), text_color=SUB)
        desc.pack(pady=(0, 12))

        row_creds = ctk.CTkFrame(self.tab_auth, fg_color="transparent")
        row_creds.pack(pady=4)

        self.ent_api_id = ctk.CTkEntry(row_creds, placeholder_text="API ID (e.g. 2938412)", width=170, height=38, corner_radius=8, fg_color=BG, text_color=TEXT)
        self.ent_api_id.pack(side="left", padx=4)
        if self.cfg.api_id and self.cfg.api_id != 1234567:
            self.ent_api_id.insert(0, str(self.cfg.api_id))

        self.ent_api_hash = ctk.CTkEntry(row_creds, placeholder_text="API Hash (32-char hex)", width=240, height=38, corner_radius=8, fg_color=BG, text_color=TEXT)
        self.ent_api_hash.pack(side="left", padx=4)
        if self.cfg.api_hash and self.cfg.api_hash != "your_api_hash_here":
            self.ent_api_hash.insert(0, self.cfg.api_hash)

        self.ent_phone = ctk.CTkEntry(self.tab_auth, placeholder_text="Номер телефона (в формате +79991234567)", width=420, height=38, corner_radius=8, fg_color=BG, text_color=TEXT)
        self.ent_phone.pack(pady=6)

        btn_send_code = ctk.CTkButton(self.tab_auth, text="📩 Запросить код в Telegram", fg_color=MAIN, text_color=BG, width=420, height=38, corner_radius=8, font=("JetBrains Mono", 12, "bold"),
                                      command=lambda: self.async_call(self._action_send_code()))
        btn_send_code.pack(pady=4)

        self.lbl_auth_hint = ctk.CTkLabel(self.tab_auth, text="", font=("JetBrains Mono", 11), text_color=MAIN)
        self.lbl_auth_hint.pack(pady=2)

        self.ent_code = ctk.CTkEntry(self.tab_auth, placeholder_text="Код подтверждения (из чата Telegram)", width=420, height=38, corner_radius=8, fg_color=BG, text_color=TEXT)
        self.ent_code.pack(pady=6)

        self.ent_2fa = ctk.CTkEntry(self.tab_auth, placeholder_text="2FA Облачный пароль (если включен)", width=420, height=38, corner_radius=8, show="*", fg_color=BG, text_color=TEXT)
        self.ent_2fa.pack(pady=6)

        btn_login = ctk.CTkButton(self.tab_auth, text="Войти и сохранить сессию", fg_color=MAIN, text_color=BG, width=420, height=40, corner_radius=8, font=("JetBrains Mono", 13, "bold"),
                                  command=lambda: self.async_call(self._action_sign_in()))
        btn_login.pack(pady=(10, 16))

    def _init_deepseek_tab(self):
        self.tab_deepseek = ctk.CTkFrame(self.container, fg_color=SUB_ALT, corner_radius=10)
        
        lbl = ctk.CTkLabel(self.tab_deepseek, text="FreeDeepseekAPI Endpoint Settings", font=("JetBrains Mono", 18, "bold"), text_color=MAIN)
        lbl.pack(pady=16)

        sub_lbl = ctk.CTkLabel(self.tab_deepseek, text="Укажи адрес сервера FreeDeepseekAPI (например http://127.0.0.1:8000/v1 или http://localhost:9655/v1)", font=("JetBrains Mono", 11), text_color=SUB)
        sub_lbl.pack(pady=(0, 10))

        self.ent_ds_url = ctk.CTkEntry(self.tab_deepseek, placeholder_text="http://127.0.0.1:8000/v1", width=420, height=38, corner_radius=8, fg_color=BG, text_color=TEXT)
        self.ent_ds_url.pack(pady=6)
        self.ent_ds_url.insert(0, self.cfg.deepseek_base_url)

        self.ent_ds_key = ctk.CTkEntry(self.tab_deepseek, placeholder_text="API Key (default: free-deepseek-api)", width=420, height=38, corner_radius=8, fg_color=BG, text_color=TEXT)
        self.ent_ds_key.pack(pady=6)
        self.ent_ds_key.insert(0, self.cfg.deepseek_api_key)

        self.ent_ds_model = ctk.CTkEntry(self.tab_deepseek, placeholder_text="Model (e.g. deepseek-chat)", width=420, height=38, corner_radius=8, fg_color=BG, text_color=TEXT)
        self.ent_ds_model.pack(pady=6)
        self.ent_ds_model.insert(0, self.cfg.deepseek_model)

        btn_row = ctk.CTkFrame(self.tab_deepseek, fg_color="transparent")
        btn_row.pack(pady=6)

        btn_test_ds = ctk.CTkButton(btn_row, text="⚡ Тест подключения", fg_color=BG, text_color=MAIN, width=205, height=36, corner_radius=8, font=("JetBrains Mono", 12, "bold"),
                                    command=lambda: self.async_call(self._test_deepseek_connection()))
        btn_test_ds.pack(side="left", padx=4)

        btn_new_chat = ctk.CTkButton(btn_row, text="🔄 Создать новый чистый чат", fg_color=BG, text_color=TEXT, width=205, height=36, corner_radius=8, font=("JetBrains Mono", 12),
                                     command=self._reset_ai_chat)
        btn_new_chat.pack(side="left", padx=4)

        self.lbl_ds_test = ctk.CTkLabel(self.tab_deepseek, text="", font=("JetBrains Mono", 11), text_color=MAIN)
        self.lbl_ds_test.pack(pady=2)

        btn_save_ds = ctk.CTkButton(self.tab_deepseek, text="Сохранить настройки DeepSeek", fg_color=MAIN, text_color=BG, width=420, height=40, corner_radius=8, font=("JetBrains Mono", 13, "bold"),
                                    command=self._save_deepseek_settings)
        btn_save_ds.pack(pady=10)

    def _reset_ai_chat(self):
        self.ai.reset_session()
        self.lbl_ds_test.configure(text=f"✅ Контекст сброшен! Создана новая чистая сессия: {self.ai.session_id[:8]}", text_color=MAIN)
        self.append_log(f"[DEEPSEEK] Started fresh chat session: {self.ai.session_id}")

    async def _test_deepseek_connection(self):
        url = self.ent_ds_url.get().strip()
        key = self.ent_ds_key.get().strip()
        model = self.ent_ds_model.get().strip()
        self.ai.update_settings(url, key, model)

        self.after(0, lambda: self.lbl_ds_test.configure(text="⏳ Отправка тестового запроса...", text_color=MAIN))
        res = await self.ai.generate_reply("test_user", "привет")
        if res:
            self.after(0, lambda: self.lbl_ds_test.configure(text=f"✅ Ответ получен: {res[:40]}...", text_color=MAIN))
            self.append_log(f"[DEEPSEEK TEST OK] Response: {res}")
        else:
            self.after(0, lambda: self.lbl_ds_test.configure(text=f"❌ Ошибка подключения к {url}! Проверь адрес и запущен ли сервер.", text_color=ERROR))
            self.append_log(f"[DEEPSEEK TEST FAILED] Cannot reach {url}", level="ERROR")

    def _init_target_tab(self):
        self.tab_target = ctk.CTkFrame(self.container, fg_color="transparent")
        self.tab_target.grid_columnconfigure(0, weight=1)
        self.tab_target.grid_columnconfigure(1, weight=2)
        self.tab_target.grid_rowconfigure(0, weight=1)

        left = ctk.CTkFrame(self.tab_target, fg_color=SUB_ALT, corner_radius=10)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        lbl_c = ctk.CTkLabel(left, text="Active Dialogs", font=("JetBrains Mono", 14, "bold"), text_color=MAIN)
        lbl_c.pack(pady=10)

        btn_refresh = ctk.CTkButton(left, text="⟳ Refresh Dialogs", fg_color=BG, text_color=TEXT, font=("JetBrains Mono", 11), height=32, corner_radius=6,
                                    command=lambda: self.async_call(self._load_dialogs()))
        btn_refresh.pack(fill="x", padx=12, pady=4)

        self.chat_list_box = ctk.CTkScrollableFrame(left, fg_color="transparent")
        self.chat_list_box.pack(fill="both", expand=True, padx=8, pady=8)

        right = ctk.CTkFrame(self.tab_target, fg_color=SUB_ALT, corner_radius=10)
        right.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        lbl_m = ctk.CTkLabel(right, text="Recent Chat Log (Click Message to Target)", font=("JetBrains Mono", 14, "bold"), text_color=MAIN)
        lbl_m.pack(pady=10)

        self.msg_list_box = ctk.CTkScrollableFrame(right, fg_color="transparent")
        self.msg_list_box.pack(fill="both", expand=True, padx=8, pady=8)

    def _init_arena_tab(self):
        self.tab_arena = ctk.CTkFrame(self.container, fg_color="transparent")
        self.tab_arena.grid_columnconfigure(0, weight=3)
        self.tab_arena.grid_columnconfigure(1, weight=1)
        self.tab_arena.grid_rowconfigure(0, weight=1)

        feed_panel = ctk.CTkFrame(self.tab_arena, fg_color=SUB_ALT, corner_radius=10)
        feed_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        self.txt_arena = ctk.CTkTextbox(feed_panel, fg_color=BG, text_color=TEXT, font=("JetBrains Mono", 13), wrap="word", corner_radius=8)
        self.txt_arena.pack(fill="both", expand=True, padx=14, pady=14)

        side = ctk.CTkFrame(self.tab_arena, fg_color=SUB_ALT, corner_radius=10)
        side.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        lbl_target_info = ctk.CTkLabel(side, text="CURRENT TARGET", font=("JetBrains Mono", 11), text_color=SUB)
        lbl_target_info.pack(pady=(8, 2))

        self.lbl_active_target = ctk.CTkLabel(side, text=self.cfg.target_username or "None", font=("JetBrains Mono", 15, "bold"), text_color=MAIN)
        self.lbl_active_target.pack(pady=(0, 4))

        self.ent_target_manual = ctk.CTkEntry(side, placeholder_text="Target (@nick or Name)", fg_color=BG, text_color=TEXT, corner_radius=6, height=34)
        self.ent_target_manual.pack(fill="x", padx=14, pady=2)
        if self.cfg.target_username:
            self.ent_target_manual.insert(0, self.cfg.target_username)

        btn_set_target = ctk.CTkButton(side, text="Set Target", fg_color=BG, text_color=TEXT, height=30, corner_radius=6, command=self._set_manual_target)
        btn_set_target.pack(fill="x", padx=14, pady=2)

        self.chk_auto_bait = ctk.CTkCheckBox(side, text="Беспрерывный спам (Non-Stop)", font=("JetBrains Mono", 11), text_color=TEXT,
                                             fg_color=MAIN, hover_color=MAIN, command=self._toggle_auto_bait)
        self.chk_auto_bait.pack(pady=4)
        self.chk_auto_bait.select()

        self.chk_target_all = ctk.CTkCheckBox(side, text="Троллить ВСЕХ в чате", font=("JetBrains Mono", 11), text_color=TEXT,
                                              fg_color=MAIN, hover_color=MAIN, command=self._toggle_target_all)
        self.chk_target_all.pack(pady=2)

        lbl_freq = ctk.CTkLabel(side, text=f"ТЕГАТЬ @username: КАЖДЫЕ {self.cfg.mention_frequency} СОО", font=("JetBrains Mono", 10), text_color=SUB)
        lbl_freq.pack(pady=(6, 1))
        self.lbl_freq_val = lbl_freq

        self.freq_slider = ctk.CTkSlider(side, from_=1, to=30, number_of_steps=29, progress_color=MAIN, command=self._on_freq_slide)
        self.freq_slider.set(self.cfg.mention_frequency)
        self.freq_slider.pack(fill="x", padx=14, pady=2)

        lbl_typo = ctk.CTkLabel(side, text="ПРОЦЕНТ ОПЕЧАТОК: 6%", font=("JetBrains Mono", 10), text_color=SUB)
        lbl_typo.pack(pady=(6, 1))
        self.lbl_typo_val = lbl_typo

        self.typo_slider = ctk.CTkSlider(side, from_=0, to=30, number_of_steps=30, progress_color=MAIN, command=self._on_typo_slide)
        self.typo_slider.set(6)
        self.typo_slider.pack(fill="x", padx=14, pady=2)

        lbl_style = ctk.CTkLabel(side, text="STYLE MODE", font=("JetBrains Mono", 11), text_color=SUB)
        lbl_style.pack(pady=(6, 2))

        self.seg_style = ctk.CTkSegmentedButton(side, values=["aggressive", "schizo", "mixed"], command=self._on_style_change,
                                                selected_color=MAIN, selected_hover_color=MAIN, text_color=BG, corner_radius=6)
        self.seg_style.set(self.cfg.style)
        self.seg_style.pack(fill="x", padx=14, pady=2)

        self.btn_run = ctk.CTkButton(side, text="▶ START ENGINE", fg_color=MAIN, text_color=BG, font=("JetBrains Mono", 14, "bold"),
                                     height=44, corner_radius=8, command=self.toggle_engine)
        self.btn_run.pack(side="bottom", fill="x", padx=14, pady=12)

    def _on_freq_slide(self, val):
        self.cfg.mention_frequency = int(val)
        self.tg.mention_every_n = int(val)
        self.lbl_freq_val.configure(text=f"ТЕГАТЬ @username: КАЖДЫЕ {int(val)} СОО")
        self.cfg.save()

    def _on_typo_slide(self, val):
        self.current_typo_rate = val / 100.0
        self.lbl_typo_val.configure(text=f"ПРОЦЕНТ ОПЕЧАТОК: {int(val)}%")

    def _toggle_auto_bait(self):
        self.non_stop_running = bool(self.chk_auto_bait.get())
        self.cfg.auto_bait_enabled = self.non_stop_running
        self.cfg.save()
        if self.non_stop_running:
            self.append_log("[NON-STOP] Enabled: Continuous stream.")
            if self.tg.is_running:
                self._start_continuous_stream_loop()
        else:
            self.append_log("[NON-STOP] Disabled.")
            if self.tg.auto_bait_task and not self.tg.auto_bait_task.done():
                self.tg.auto_bait_task.cancel()

    def _toggle_target_all(self):
        self.target_mode_all = bool(self.chk_target_all.get())
        self.tg.target_mode_all = self.target_mode_all
        if self.target_mode_all:
            self.lbl_active_target.configure(text="ALL USERS (ВЕСЬ ЧАТ)")
            self.append_log("[MODE] Target mode: TROLL EVERYONE IN CHAT")
        else:
            self.lbl_active_target.configure(text=self.cfg.target_username or "None")
            self.append_log(f"[MODE] Target mode: Single target (@{self.cfg.target_username})")

    def show_tab(self, tab_name: str, animate=True):
        if self.current_tab == tab_name:
            return

        self.current_tab = tab_name
        self.btn_tab_auth.set_active(tab_name == "auth", animate)
        self.btn_tab_deepseek.set_active(tab_name == "deepseek", animate)
        self.btn_tab_target.set_active(tab_name == "target", animate)
        self.btn_tab_arena.set_active(tab_name == "arena", animate)

        target_widget = None
        if tab_name == "auth":
            target_widget = self.tab_auth
        elif tab_name == "deepseek":
            target_widget = self.tab_deepseek
        elif tab_name == "target":
            target_widget = self.tab_target
        else:
            target_widget = self.tab_arena

        self.tab_auth.pack_forget()
        self.tab_deepseek.pack_forget()
        self.tab_target.pack_forget()
        self.tab_arena.pack_forget()

        target_widget.pack(fill="both", expand=True)

        if animate:
            SmoothAnimator.animate(
                self.container, 0.0, 1.0, duration_ms=220, steps=14,
                update_callback=lambda p: None
            )

    def _save_deepseek_settings(self):
        url = self.ent_ds_url.get().strip()
        key = self.ent_ds_key.get().strip()
        model = self.ent_ds_model.get().strip()

        self.cfg.deepseek_base_url = url
        self.cfg.deepseek_api_key = key
        self.cfg.deepseek_model = model
        self.cfg.save()

        self.ai.update_settings(url, key, model)
        self.append_log(f"[DEEPSEEK] Updated endpoint: {url} | Model: {model}")

    def append_log(self, text: str):
        self.after(0, lambda: self._insert_text(text))

    def _insert_text(self, text: str):
        now = datetime.now().strftime("%H:%M:%S")
        self.txt_arena.insert("end", f"[{now}] {text}\n")
        self.txt_arena.see("end")

    def _on_wpm_slide(self, val):
        self.cfg.wpm_rate = int(val)
        self.lbl_wpm_val.configure(text=f"{self.cfg.wpm_rate} WPM")
        self.cfg.save()

    def _on_style_change(self, val):
        self.cfg.style = val
        self.cfg.save()

    def _set_manual_target(self):
        uname = self.ent_target_manual.get().strip().replace('@', '')
        self.cfg.target_username = uname
        self.tg.target_username = uname
        self.tg.target_id = None
        self.lbl_active_target.configure(text=f"@{uname}" if uname else "None")
        self.cfg.save()
        self.append_log(f"[TARGET SET] Target set to: @{uname}")

    async def _check_initial_auth(self):
        authed = await self.tg.is_authorized()
        status_txt = "TG: CONNECTED" if authed else "TG: NOT LOGGED IN"
        color = MAIN if authed else ERROR
        self.after(0, lambda: self.lbl_status.configure(text=status_txt, text_color=color))
        if authed:
            self.tg.bind_listeners(self._handle_incoming_message)

    async def _action_send_code(self):
        api_id_raw = self.ent_api_id.get().strip()
        api_hash = self.ent_api_hash.get().strip()
        phone = self.ent_phone.get().strip()

        if not api_id_raw.isdigit() or not api_hash:
            self.after(0, lambda: self.lbl_auth_hint.configure(text="❌ Заполни валидные API ID и API Hash с my.telegram.org", text_color=ERROR))
            self.append_log("[AUTH ERROR] Invalid API ID / API Hash")
            return

        self.cfg.api_id = int(api_id_raw)
        self.cfg.api_hash = api_hash
        self.cfg.save()

        self.tg.api_id = self.cfg.api_id
        self.tg.api_hash = self.cfg.api_hash
        if self.tg.client:
            await self.tg.client.disconnect()
            self.tg.client = None

        self.after(0, lambda: self.lbl_auth_hint.configure(text="⏳ Подключение к серверам Telegram...", text_color=MAIN))
        
        try:
            await self.tg.send_code(phone)
            self.after(0, lambda: self.lbl_auth_hint.configure(text=f"✅ Код отправлен на {phone} в Telegram!", text_color=MAIN))
            self.append_log(f"[AUTH] Code sent to {phone}. Check Telegram official app.")
        except Exception as e:
            self.after(0, lambda: self.lbl_auth_hint.configure(text=f"❌ Ошибка: {e}", text_color=ERROR))
            self.append_log(f"[AUTH ERROR] {e}", level="ERROR")

    async def _action_sign_in(self):
        phone = self.ent_phone.get().strip()
        code = self.ent_code.get().strip()
        pwd = self.ent_2fa.get().strip() or None
        
        try:
            await self.tg.sign_in_code(phone, code, pwd)
            self.append_log("[AUTH] Successfully logged in!")
            self.after(0, lambda: self.lbl_status.configure(text="TG: CONNECTED", text_color=MAIN))
            self.after(0, lambda: self.lbl_auth_hint.configure(text="✅ Успешный вход! Переходи на вкладку target или live arena.", text_color=MAIN))
            self.tg.bind_listeners(self._handle_incoming_message)
        except Exception as e:
            self.after(0, lambda: self.lbl_auth_hint.configure(text=f"❌ Ошибка входа: {e}", text_color=ERROR))
            self.append_log(f"[AUTH SIGN-IN ERROR] {e}", level="ERROR")

    def _load_dialogs_sync(self, dialogs):
        for w in list(self.chat_list_box.winfo_children()):
            try:
                w.destroy()
            except Exception:
                pass
        for d in dialogs:
            btn = ctk.CTkButton(self.chat_list_box, text=f"{d['title']}", fg_color=BG, text_color=TEXT, anchor="w", corner_radius=6, height=34,
                                command=lambda chat=d: self.async_call(self._select_chat(chat)))
            btn.pack(fill="x", pady=2)

    async def _load_dialogs(self):
        dialogs = await self.tg.get_dialogs_list()
        self.after(0, lambda: self._load_dialogs_sync(dialogs))

    def _render_chat_messages_sync(self, messages):
        for w in list(self.msg_list_box.winfo_children()):
            try:
                w.destroy()
            except Exception:
                pass
        for m in messages:
            sender_display = f"{m['sender_name']} (@{m['username']})" if m['username'] else m['sender_name']
            btn = ctk.CTkButton(self.msg_list_box, text=f"{sender_display}: {m['text'][:45]}", fg_color=BG, text_color=TEXT, anchor="w", corner_radius=6, height=34,
                                command=lambda msg=m: self._pick_target_from_msg(msg))
            btn.pack(fill="x", pady=2)

    async def _select_chat(self, chat_info):
        self.cfg.selected_chat_id = chat_info['id']
        self.cfg.selected_chat_title = chat_info['title']
        self.tg.active_chat_id = chat_info['id']
        self.cfg.save()
        self.append_log(f"[CHAT] Selected chat: {chat_info['title']} ({chat_info['id']})")
        messages = await self.tg.get_recent_messages(chat_info['id'], limit=30)
        self.after(0, lambda: self._render_chat_messages_sync(messages))

    def _pick_target_from_msg(self, msg):
        self.cfg.target_id = msg['sender_id']
        self.cfg.target_username = msg['username'] or msg['sender_name']
        self.tg.target_id = msg['sender_id']
        self.tg.target_username = self.cfg.target_username
        self.lbl_active_target.configure(text=f"@{self.cfg.target_username}")
        self.ent_target_manual.delete(0, "end")
        self.ent_target_manual.insert(0, self.cfg.target_username)
        self.cfg.save()
        self.append_log(f"[TARGET SELECTED] {self.cfg.target_username} (ID: {self.cfg.target_id})")

    async def _handle_incoming_message(self, event, is_target: bool, sender):
        sender_title = getattr(sender, 'username', '') or getattr(sender, 'first_name', 'Unknown')
        text = (event.text or "").strip()
        
        is_reply_to_other = False
        if event.reply_to_msg_id:
            try:
                replied_msg = await event.get_reply_message()
                if replied_msg:
                    me = await self.tg.client.get_me()
                    if replied_msg.sender_id != me.id:
                        is_reply_to_other = True
            except Exception:
                pass

        silence_gap = time.time() - self.tg.last_target_msg_time
        was_silent_before = silence_gap > 3.5

        self.append_log(f"[TARGET INBOUND @{sender_title}] '{text}' -> INSTANT REACTION TRIGGERED")
        
        # Сразу отменяем предыдущую генерацию если она шла
        if self.current_ai_task and not self.current_ai_task.done():
            self.current_ai_task.cancel()

        async def _process_instant_reaction():
            # Мгновенная генерация (до 1-1.8с) или моментальный ответ за 0.01с
            reply_full = await self.ai.generate_reply(
                sender_title,
                text,
                is_challenge=True,
                is_reply_to_other=is_reply_to_other,
                was_silent_before=was_silent_before,
                style=self.cfg.style
            )
            self.append_log(f"[INSTANT REACT READY] {reply_full[:50]}...")

            reply_with_typos = self.emulator.apply_typos(reply_full, typo_rate=self.current_typo_rate)
            chunks = self.emulator.chunk_text(reply_with_typos, self.cfg.min_chunk_words, self.cfg.max_chunk_words)

            mention_tag = self.cfg.target_username if not self.target_mode_all else sender_title
            
            await self.tg.send_ladder_chunks(
                chat_id=event.chat_id,
                chunks=chunks,
                ladder_pause=self.cfg.ladder_pause,
                wpm=self.cfg.wpm_rate,
                emulator=self.emulator,
                target_mention=mention_tag,
                reply_to_msg_id=event.id
            )

        self.current_ai_task = asyncio.create_task(_process_instant_reaction())

    def _start_continuous_stream_loop(self):
        async def _continuous_worker():
            while self.tg.is_running and self.non_stop_running:
                await asyncio.sleep(0.1)
                if not self.tg.is_running or not self.non_stop_running or not self.tg.active_chat_id:
                    break
                
                # Если сейчас генерируется реакция или активно шлется ответ на сообщение таргета — ждем
                if (self.current_ai_task and not self.current_ai_task.done()) or (self.tg.active_send_task and not self.tg.active_send_task.done()):
                    continue

                # Проверяем, действительно ли прошло время тишины
                silence_duration = time.time() - self.tg.last_target_msg_time
                if silence_duration < 3.5:
                    continue

                target_name = self.cfg.target_username or "жертва"
                provoke_text = await self.ai.generate_silence_provoke(target_name)
                
                provoke_with_typos = self.emulator.apply_typos(provoke_text, typo_rate=self.current_typo_rate)
                chunks = self.emulator.chunk_text(provoke_with_typos, self.cfg.min_chunk_words, self.cfg.max_chunk_words)
                
                self.append_log(f"[NON-STOP 15-BURST] Sending silence provoke ({silence_duration:.1f}s)...")
                await self.tg.send_ladder_chunks(
                    chat_id=self.tg.active_chat_id,
                    chunks=chunks,
                    ladder_pause=self.cfg.ladder_pause,
                    wpm=self.cfg.wpm_rate,
                    emulator=self.emulator,
                    target_mention=self.cfg.target_username
                )

        if self.tg.auto_bait_task and not self.tg.auto_bait_task.done():
            self.tg.auto_bait_task.cancel()
        self.tg.auto_bait_task = self.async_call(_continuous_worker())

    def toggle_engine(self):
        if not self.tg.is_running:
            self.tg.is_running = True
            self.tg.active_chat_id = self.cfg.selected_chat_id
            self.tg.target_username = self.cfg.target_username
            self.tg.target_id = self.cfg.target_id
            self.tg.total_sent_count = 0
            self.tg.last_target_msg_time = time.time()
            self.btn_run.configure(text="■ STOP ENGINE", fg_color=ERROR)
            self.append_log(f"[ENGINE] Running on {self.cfg.selected_chat_title} @ {self.cfg.wpm_rate} WPM")
            
            if self.non_stop_running:
                self._start_continuous_stream_loop()
        else:
            self.tg.is_running = False
            if self.tg.auto_bait_task and not self.tg.auto_bait_task.done():
                self.tg.auto_bait_task.cancel()
            self.tg.cancel_active_stream()
            self.btn_run.configure(text="▶ START ENGINE", fg_color=MAIN)
            self.append_log("[ENGINE] Stopped.")

if __name__ == "__main__":
    app = TrollTypeDesktopApp()
    app.mainloop()
