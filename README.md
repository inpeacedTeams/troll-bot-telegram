# troll-bot-telegram (trolltype v2.5 — DeepSeek Edition)

Автоматизированный тролль-бот для Telegram с Monkeytype-эстетикой интерфейса, плавными iOS-анимациями, эмуляцией скорости печати (до 450 WPM), логической лесенкой (по 2–8 слов) и интеграцией с **[FreeDeepseekAPI](https://github.com/ForgetMeAI/FreeDeepseekAPI)**.

## Возможности
- 🧠 **FreeDeepseekAPI Integration**: подключение к бесплатному локальному эндпоинту DeepSeek (OpenAI-compatible `/v1`).
- ✨ **iOS Smooth Animations**: пружинные кривые перехода и мягкие анимации вкладок (`animator.py`).
- ⚡ **Вход по Telethon**: безопасное сохранение сессии Telegram и поддержка 2FA.
- 🎯 **Выбор чата и таргета**: динамический список диалогов и выбор таргета в один клик.
- ⌨️ **WPM Typing Emulator**: натуральная эмуляция набора текста со скоростью 30–450 слов/мин.
- 🪜 **Smart Ladder**: логическая разбивка ответа на смысловые фразы по 2–8 слов с задержкой.

## Установка и запуск

1. Запустите [FreeDeepseekAPI](https://github.com/ForgetMeAI/FreeDeepseekAPI) (обычно на `http://localhost:8000/v1`).
2. Клонируйте репозиторий бота:
```bash
git clone https://github.com/inpeacedTeams/troll-bot-telegram.git
cd troll-bot-telegram
pip install -r requirements.txt
```
3. Заполните `.env` (или настройте прямо в интерфейсе на вкладке `deepseek`):
```env
TG_API_ID=1234567
TG_API_HASH=your_api_hash
DEEPSEEK_BASE_URL=http://localhost:8000/v1
DEEPSEEK_API_KEY=free-deepseek-api
DEEPSEEK_MODEL=deepseek-chat
```
4. Запустите приложение:
```bash
python gui.py
```
