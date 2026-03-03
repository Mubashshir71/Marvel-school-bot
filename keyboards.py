from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📘 Matematika", callback_data="course:math")],
        [InlineKeyboardButton(text="🇬🇧 Ingliz tili", callback_data="course:english")],
        [InlineKeyboardButton(text="🇷🇺 Rus tili", callback_data="course:russian")],
        [InlineKeyboardButton(text="💰 Narxlar", callback_data="info:prices")],
        [InlineKeyboardButton(text="🧑‍🏫 Demo dars", callback_data="info:demo")],
        [InlineKeyboardButton(text="📍 Manzil", callback_data="info:location")],
        [InlineKeyboardButton(text="☎️ Operator", callback_data="info:operator")],
    ])

def goals_menu(course_key: str) -> InlineKeyboardMarkup:
    # Matematika
    if course_key == "math":
        rows = [
            [InlineKeyboardButton(text="🎯 DTM", callback_data="goal:math:dtm")],
            [InlineKeyboardButton(text="📚 Maktab", callback_data="goal:math:school")],
            [InlineKeyboardButton(text="🧠 0 dan boshlash", callback_data="goal:math:zero")],
        ]

    # Ingliz tili
    elif course_key == "english":
        rows = [
            [InlineKeyboardButton(text="🇬🇧 IELTS", callback_data="goal:english:ielts")],
            [InlineKeyboardButton(text="📄 CEFR", callback_data="goal:english:cefr")],
            [InlineKeyboardButton(text="🗣 Speaking", callback_data="goal:english:speaking")],
            [InlineKeyboardButton(text="🧠 0 dan boshlash", callback_data="goal:english:zero")],
        ]

    # Rus tili
    elif course_key == "russian":
        rows = [
            [InlineKeyboardButton(text="🇷🇺 TORFL", callback_data="goal:russian:torfl")],
            [InlineKeyboardButton(text="📚 Maktab", callback_data="goal:russian:school")],
            [InlineKeyboardButton(text="🗣 Suhbat", callback_data="goal:russian:speaking")],
            [InlineKeyboardButton(text="🧠 0 dan boshlash", callback_data="goal:russian:zero")],
        ]
    else:
        rows = [
            [InlineKeyboardButton(text="🧠 0 dan boshlash", callback_data=f"goal:{course_key}:zero")],
        ]

    rows.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="back:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def time_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌞 Ertalab (09:00–10:30)", callback_data="time:morning")],
        [InlineKeyboardButton(text="🌙 Kechki payt (15:00–16:30)", callback_data="time:evening")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back:goals")],
    ])

def contact_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📲 Raqamni yuborish", request_contact=True)],
            [KeyboardButton(text="🏠 Bosh menyu")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def admin_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📥 Yangi leadlar", callback_data="admin:list:new")],
        [InlineKeyboardButton(text="✅ Bog‘langan", callback_data="admin:list:contacted")],
        [InlineKeyboardButton(text="❌ Yo‘qolgan", callback_data="admin:list:lost")],
        [InlineKeyboardButton(text="📊 Statistika", callback_data="admin:stats")],
        [InlineKeyboardButton(text="📢 Broadcast", callback_data="admin:broadcast")],
    ])

def lead_actions_kb(lead_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Bog‘landim", callback_data=f"admin:status:{lead_id}:contacted"),
            InlineKeyboardButton(text="❌ Yo‘qoldi", callback_data=f"admin:status:{lead_id}:lost"),
        ]
    ])