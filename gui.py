import sys
import os
import asyncio
import threading
import customtkinter as ctk
from datetime import datetime

from config import AppConfig
from logger import logger
from ai_engine import AIEngine
from typing_emulator import TypingEmulator
from telegram_handler import TelegramHandler

# Monkeytype palette
ctk.set_appearance_mode("dark")
BG = "#323437"
MAIN = "#e2b714"
SUB_ALT = "#2c2e31"
TEXT = "#d1d0c5"
SUB = "#646669"
ERROR = "#ca4754"

class TrollTypeDesktopApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("trolltype // desktop v2.4")
        self.geometry("1060x700")
        self.minsize(900, 600)
        self.configure(fg_color=BG)

        self.cfg = AppConfig.load()
        self.ai = AIEngine(self.cfg.openai_key)
        self.emulator = TypingEmulator()
        self.tg = TelegramHandler(self.cfg.api_id, self.cfg.api_hash, self.cfg.session_name)
        self.tg.on_log_callback = self.append_log

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
        # Header Bar
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=28, pady=12)

        logo = ctk.CTkLabel(header, text="⚡ trolltype", font=("JetBrains Mono", 22, "bold"), text_color=MAIN)
        logo.pack(side="left")

        self.lbl_status = ctk.CTkLabel(header, text="AUTH: CHECKING...", font=("JetBrains Mono", 12), text_color=SUB)
        self.lbl_status.pack(side="right")

        # Monkeytype Pill Bar
        pill = ctk.CTkFrame(self, fg_color=SUB_ALT, corner_radius=8)
        pill.pack(fill="x", padx=28, pady=4)

        self.btn_tab_auth = self._pill_btn(pill, "auth", lambda: self.show_tab("auth"))
        self.btn_tab_target = self._pill_btn(pill, "target", lambda: self.show_tab("target"))
        self.btn_tab_arena = self._pill_btn(pill, "live arena", lambda: self.show_tab("arena"), active=True)

        self.lbl_wpm_val = ctk.CTkLabel(pill, text=f"{self.cfg.wpm_rate} WPM", font=("JetBrains Mono", 13, "bold"), text_color=MAIN)
        self.lbl_wpm_val.pack(side="right", padx=12)

        self.wpm_slider = ctk.CTkSlider(pill, from_=30, to_=450, number_of_steps=42, progress_color=MAIN, command=self._on_wpm_slide)
        self.wpm_slider.set(self.cfg.wpm_rate)
        self.wpm_slider.pack(side="right", padx=8)

        # Tab Views Container
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=28, pady=12)

        self._init_auth_tab()
        self._init_target_tab()
        self._init_arena_tab()

        self.show_tab("arena")

    def _pill_btn(self, parent, text, cmd, active=False):
        btn = ctk.CTkButton(parent, text=text, width=80, height=28, fg_color=MAIN if active else "transparent",
                            text_color=BG if active else SUB, font=("JetBrains Mono", 12, "bold"), command=cmd)
        btn.pack(side="left", padx=4, pady=4)
        return btn

    def _init_auth_tab(self):
        self.tab_auth = ctk.CTkFrame(self.container, fg_color=SUB_ALT, corner_radius=8)
        
        lbl = ctk.CTkLabel(self.tab_auth, text="Telegram Authentication", font=("JetBrains Mono", 16, "bold"), text_color=MAIN)
        lbl.pack(pady=16)

        self.ent_phone = ctk.CTkEntry(self.tab_auth, placeholder_text="+79991234567", width=320, fg_color=BG, text_color=TEXT)
        self.ent_phone.pack(pady=8)

        btn_send_code = ctk.CTkButton(self.tab_auth, text="Send Code", fg_color=MAIN, text_color=BG, font=("JetBrains Mono", 12, "bold"),
                                      command=lambda: self.async_call(self._action_send_code()))
        btn_send_code.pack(pady=6)

        self.ent_code = ctk.CTkEntry(self.tab_auth, placeholder_text="Enter Code", width=320, fg_color=BG, text_color=TEXT)
        self.ent_code.pack(pady=8)

        self.ent_2fa = ctk.CTkEntry(self.tab_auth, placeholder_text="2FA Password (if any)", width=320, show="*", fg_color=BG, text_color=TEXT)
        self.ent_2fa.pack(pady=8)

        btn_login = ctk.CTkButton(self.tab_auth, text="Sign In", fg_color=MAIN, text_color=BG, font=("JetBrains Mono", 12, "bold"),
                                  command=lambda: self.async_call(self._action_sign_in()))
        btn_login.pack(pady=12)

    def _init_target_tab(self):
        self.tab_target = ctk.CTkFrame(self.container, fg_color="transparent")
        
        # Grid layout: Left Chats, Right Messages
        self.tab_target.grid_columnconfigure(0, weight=1)
        self.tab_target.grid_columnconfigure(1, weight=2)
        self.tab_target.grid_rowconfigure(0, weight=1)

        left = ctk.CTkFrame(self.tab_target, fg_color=SUB_ALT, corner_radius=8)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        lbl_c = ctk.CTkLabel(left, text="Active Dialogs", font=("JetBrains Mono", 14, "bold"), text_color=MAIN)
        lbl_c.pack(pady=8)

        btn_refresh = ctk.CTkButton(left, text="⟳ Refresh Dialogs", fg_color=BG, text_color=TEXT, font=("JetBrains Mono", 11),
                                    command=lambda: self.async_call(self._load_dialogs()))
        btn_refresh.pack(fill="x", padx=12, pady=4)

        self.chat_list_box = ctk.CTkScrollableFrame(left, fg_color="transparent")
        self.chat_list_box.pack(fill="both", expand=True, padx=8, pady=8)

        right = ctk.CTkFrame(self.tab_target, fg_color=SUB_ALT, corner_radius=8)
        right.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        lbl_m = ctk.CTkLabel(right, text="Recent Chat Messages (Click to Target)", font=("JetBrains Mono", 14, "bold"), text_color=MAIN)
        lbl_m.pack(pady=8)

        self.msg_list_box = ctk.CTkScrollableFrame(right, fg_color="transparent")
        self.msg_list_box.pack(fill="both", expand=True, padx=8, pady=8)

    def _init_arena_tab(self):
        self.tab_arena = ctk.CTkFrame(self.container, fg_color="transparent")
        
        self.tab_arena.grid_columnconfigure(0, weight=3)
        self.tab_arena.grid_columnconfigure(1, weight=1)
        self.tab_arena.grid_rowconfigure(0, weight=1)

        # Feed Panel
        feed_panel = ctk.CTkFrame(self.tab_arena, fg_color=SUB_ALT, corner_radius=8)
        feed_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        self.txt_arena = ctk.CTkTextbox(feed_panel, fg_color=BG, text_color=TEXT, font=("JetBrains Mono", 13), wrap="word")
        self.txt_arena.pack(fill="both", expand=True, padx=12, pady=12)

        # Control Sidebar
        side = ctk.CTkFrame(self.tab_arena, fg_color=SUB_ALT, corner_radius=8)
        side.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        lbl_target_info = ctk.CTkLabel(side, text="CURRENT TARGET", font=("JetBrains Mono", 12), text_color=SUB)
        lbl_target_info.pack(pady=(12, 2))

        self.lbl_active_target = ctk.CTkLabel(side, text=self.cfg.target_username or "None", font=("JetBrains Mono", 15, "bold"), text_color=MAIN)
        self.lbl_active_target.pack(pady=(0, 12))

        self.ent_target_manual = ctk.CTkEntry(side, placeholder_text="@username", fg_color=BG, text_color=TEXT)
        self.ent_target_manual.pack(fill="x", padx=12, pady=4)
        if self.cfg.target_username:
            self.ent_target_manual.insert(0, self.cfg.target_username)

        btn_set_target = ctk.CTkButton(side, text="Set Manual Target", fg_color=BG, text_color=TEXT, command=self._set_manual_target)
        btn_set_target.pack(fill="x", padx=12, pady=4)

        # Style switch
        lbl_style = ctk.CTkLabel(side, text="STYLE MODE", font=("JetBrains Mono", 12), text_color=SUB)
        lbl_style.pack(pady=(16, 4))

        self.seg_style = ctk.CTkSegmentedButton(side, values=["aggressive", "schizo", "mixed"], command=self._on_style_change,
                                                selected_color=MAIN, selected_hover_color=MAIN, text_color=BG)
        self.seg_style.set(self.cfg.style)
        self.seg_style.pack(fill="x", padx=12, pady=4)

        # Action Buttons
        self.btn_run = ctk.CTkButton(side, text="▶ START ENGINE", fg_color=MAIN, text_color=BG, font=("JetBrains Mono", 14, "bold"),
                                     command=self.toggle_engine)
        self.btn_run.pack(side="bottom", fill="x", padx=12, pady=12)

    def show_tab(self, tab_name):
        self.tab_auth.pack_forget()
        self.tab_target.pack_forget()
        self.tab_arena.pack_forget()

        self.btn_tab_auth.configure(fg_color="transparent", text_color=SUB)
        self.btn_tab_target.configure(fg_color="transparent", text_color=SUB)
        self.btn_tab_arena.configure(fg_color="transparent", text_color=SUB)

        if tab_name == "auth":
            self.tab_auth.pack(fill="both", expand=True)
            self.btn_tab_auth.configure(fg_color=MAIN, text_color=BG)
        elif tab_name == "target":
            self.tab_target.pack(fill="both", expand=True)
            self.btn_tab_target.configure(fg_color=MAIN, text_color=BG)
        else:
            self.tab_arena.pack(fill="both", expand=True)
            self.btn_tab_arena.configure(fg_color=MAIN, text_color=BG)

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
        uname = self.ent_target_manual.get().strip()
        self.cfg.target_username = uname
        self.tg.target_username = uname
        self.lbl_active_target.configure(text=uname or "None")
        self.cfg.save()
        self.append_log(f"[TARGET] Manual target set to: {uname}")

    async def _check_initial_auth(self):
        authed = await self.tg.is_authorized()
        status_txt = "TG: CONNECTED" if authed else "TG: NOT LOGGED IN"
        color = MAIN if authed else ERROR
        self.after(0, lambda: self.lbl_status.configure(text=status_txt, text_color=color))
        if authed:
            self.tg.bind_listeners(self._handle_incoming_message)

    async def _action_send_code(self):
        phone = self.ent_phone.get().strip()
        await self.tg.send_code(phone)
        self.append_log(f"[AUTH] Code requested for {phone}")

    async def _action_sign_in(self):
        phone = self.ent_phone.get().strip()
        code = self.ent_code.get().strip()
        pwd = self.ent_2fa.get().strip() or None
        await self.tg.sign_in_code(phone, code, pwd)
        self.append_log("[AUTH] Successfully logged in!")
        self.after(0, lambda: self.lbl_status.configure(text="TG: CONNECTED", text_color=MAIN))
        self.tg.bind_listeners(self._handle_incoming_message)

    async def _load_dialogs(self):
        dialogs = await self.tg.get_dialogs_list()
        for w in self.chat_list_box.winfo_children():
            w.destroy()
        for d in dialogs:
            btn = ctk.CTkButton(self.chat_list_box, text=f"{d['title']}", fg_color=BG, text_color=TEXT, anchor="w",
                                command=lambda chat=d: self.async_call(self._select_chat(chat)))
            btn.pack(fill="x", pady=2)

    async def _select_chat(self, chat_info):
        self.cfg.selected_chat_id = chat_info['id']
        self.cfg.selected_chat_title = chat_info['title']
        self.tg.active_chat_id = chat_info['id']
        self.cfg.save()
        self.append_log(f"[CHAT] Selected chat: {chat_info['title']} ({chat_info['id']})")
        messages = await self.tg.get_recent_messages(chat_info['id'], limit=30)
        
        for w in self.msg_list_box.winfo_children():
            w.destroy()
        for m in messages:
            sender_display = f"{m['sender_name']} (@{m['username']})" if m['username'] else m['sender_name']
            btn = ctk.CTkButton(self.msg_list_box, text=f"{sender_display}: {m['text'][:45]}", fg_color=BG, text_color=TEXT, anchor="w",
                                command=lambda msg=m: self._pick_target_from_msg(msg))
            btn.pack(fill="x", pady=2)

    def _pick_target_from_msg(self, msg):
        self.cfg.target_id = msg['sender_id']
        self.cfg.target_username = msg['username'] or msg['sender_name']
        self.tg.target_id = msg['sender_id']
        self.tg.target_username = self.cfg.target_username
        self.lbl_active_target.configure(text=f"@{self.cfg.target_username}")
        self.cfg.save()
        self.append_log(f"[TARGET SELECTED] {self.cfg.target_username} (ID: {self.cfg.target_id})")

    async def _handle_incoming_message(self, event, is_target: bool, sender):
        sender_title = getattr(sender, 'username', '') or getattr(sender, 'first_name', 'Unknown')
        text = event.text or ""
        self.append_log(f"[{'TARGET' if is_target else 'USER'} @{sender_title}] {text}")

        if not is_target:
            return

        # AI Generation & Ladder Streaming
        reply_full = await self.ai.generate_reply(sender_title, text, style=self.cfg.style)
        chunks = self.emulator.chunk_text(reply_full, self.cfg.min_chunk_words, self.cfg.max_chunk_words)
        
        await self.tg.send_ladder_chunks(
            chat_id=event.chat_id,
            chunks=chunks,
            ladder_pause=self.cfg.ladder_pause,
            wpm=self.cfg.wpm_rate,
            emulator=self.emulator
        )

    def toggle_engine(self):
        if not self.tg.is_running:
            self.tg.is_running = True
            self.tg.active_chat_id = self.cfg.selected_chat_id
            self.tg.target_username = self.cfg.target_username
            self.tg.target_id = self.cfg.target_id
            self.btn_run.configure(text="■ STOP ENGINE", fg_color=ERROR)
            self.append_log(f"[ENGINE] Running on {self.cfg.selected_chat_title} @ {self.cfg.wpm_rate} WPM")
        else:
            self.tg.is_running = False
            self.btn_run.configure(text="▶ START ENGINE", fg_color=MAIN)
            self.append_log("[ENGINE] Stopped.")

if __name__ == "__main__":
    app = TrollTypeDesktopApp()
    app.mainloop()
