import asyncio
from datetime import datetime

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from config import load_config
from keyboards import (
    main_menu,
    goals_menu,     # goals_menu(course_key)
    time_menu,
    contact_kb,
    admin_menu,
    lead_actions_kb,
)
import db


# =========================
# TEXTS / LABELS
# =========================

COURSE_LABEL = {
    "math": "Matematika",
    "english": "Ingliz tili",
    "russian": "Rus tili",
}

# goal callback format: goal:<course_key>:<goal_key>
GOAL_LABEL = {
    ("math", "dtm"): "DTM",
    ("math", "school"): "Maktab",
    ("math", "zero"): "0 dan boshlash",

    ("english", "ielts"): "IELTS",
    ("english", "cefr"): "CEFR",
    ("english", "speaking"): "Speaking",
    ("english", "zero"): "0 dan boshlash",

    ("russian", "torfl"): "TORFL",
    ("russian", "school"): "Maktab",
    ("russian", "speaking"): "Suhbat",
    ("russian", "zero"): "0 dan boshlash",
}

TIME_LABEL = {
    "morning": "Ertalab (09:00–10:30)",
    "evening": "Kechki payt (15:00–16:30)",
}

PRICES_TEXT = (
    "Marvel School kurs narxlari:\n\n"
    "📘 Matematika — 500 000 so‘m / oy\n"
    "🇬🇧 Ingliz tili — 500 000 so‘m / oy\n"
    "🇷🇺 Rus tili — 500 000 so‘m / oy\n\n"
    "🎁 Demo dars — bepul ✅\n"
    "Joylar cheklangan!"
)


# =========================
# STATES
# =========================

class LeadFlow(StatesGroup):
    choosing_goal = State()
    choosing_time = State()
    waiting_contact = State()


# =========================
# HELPERS
# =========================

def start_text() -> str:
    return (
        "Assalomu alaykum 👋\n"
        "<b>Marvel School</b> o‘quv markaziga xush kelibsiz!\n\n"
        "Bizda:\n"
        "📘 Matematika\n"
        "🇬🇧 Ingliz tili\n"
        "🇷🇺 Rus tili\n\n"
        "Qaysi kurs sizga kerak?"
    )

def is_admin(user_id: int, admin_ids: set[int]) -> bool:
    return user_id in admin_ids

def lead_card(lead: dict) -> str:
    username = lead.get("username") or "-"
    note = lead.get("note") or "-"
    return (
        "🔥 <b>YANGI LEAD</b>\n\n"
        f"🆔 ID: <b>{lead['id']}</b>\n"
        f"👤 Ism: <b>{lead.get('full_name','-')}</b>\n"
        f"🔗 Username: <b>{username}</b>\n"
        f"📚 Kurs: <b>{lead.get('course','-')}</b>\n"
        f"🎯 Maqsad: <b>{lead.get('goal','-')}</b>\n"
        f"⏰ Vaqt: <b>{lead.get('time_slot','-')}</b>\n"
        f"📞 Tel: <b>{lead.get('phone','-')}</b>\n"
        f"🕒 Sana: <b>{lead.get('created_at','-')}</b>\n"
        f"📝 Izoh: <b>{note}</b>\n"
        f"📌 Status: <b>{lead.get('status','-')}</b>\n"
    )

async def safe_send(bot: Bot, chat_id: int, text: str, **kwargs) -> None:
    try:
        await bot.send_message(chat_id, text, **kwargs)
    except Exception:
        pass


# =========================
# MAIN
# =========================

async def main():
    cfg = load_config()
    await db.init_db()

    bot = Bot(
        cfg.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    print("✅ Bot ishga tushdi. Telegram’da /start bosing.")

    # -------------------------
    # USER: START / MENU
    # -------------------------
    @dp.message(CommandStart())
    async def cmd_start(m: Message, state: FSMContext):
        await state.clear()
        await m.answer(start_text(), reply_markup=main_menu())

    @dp.message(Command("menu"))
    async def cmd_menu(m: Message, state: FSMContext):
        await state.clear()
        await m.answer(start_text(), reply_markup=main_menu())

    @dp.message(Command("myid"))
    async def cmd_myid(m: Message):
        await m.answer(f"Sening Telegram ID: <b>{m.from_user.id}</b>")

    # Reply keyboard "Home"
    @dp.message(F.text == "🏠 Bosh menyu")
    async def home(m: Message, state: FSMContext):
        await state.clear()
        await m.answer(start_text(), reply_markup=main_menu())

    # -------------------------
    # USER: INFO buttons
    # -------------------------
    @dp.callback_query(F.data.startswith("info:"))
    async def info_handler(c: CallbackQuery, state: FSMContext):
        await c.answer()
        key = c.data.split(":", 1)[1]

        if key == "prices":
            await state.clear()
            await c.message.edit_text(PRICES_TEXT, reply_markup=main_menu())
            return

        if key == "location":
            await state.clear()
            await c.message.edit_text(
                f"📍 Manzil: <b>{cfg.location_text}</b>\n\n"
                "Ro‘yxatdan o‘tish uchun kurs tanlang ✅",
                reply_markup=main_menu()
            )
            return

        if key == "operator":
            await state.clear()
            await c.message.edit_text(
                f"☎️ Operator: <b>{cfg.operator_phone}</b>\n\n"
                "Yoki bot orqali ro‘yxatdan o‘ting — admin siz bilan bog‘lanadi.",
                reply_markup=main_menu()
            )
            return

        if key == "demo":
            await state.clear()
            await c.message.edit_text(
                "🧑‍🏫 Demo dars bepul ✅\n\n"
                "Demo darsga yozilish uchun avval kursni tanlang.",
                reply_markup=main_menu()
            )
            return

    # -------------------------
    # USER: Course -> Goals (dynamic)
    # -------------------------
    @dp.callback_query(F.data.startswith("course:"))
    async def course_pick(c: CallbackQuery, state: FSMContext):
        await c.answer()
        course_key = c.data.split(":", 1)[1]
        course = COURSE_LABEL.get(course_key)

        if not course:
            await c.message.answer("Xatolik: kurs topilmadi. /menu")
            return

        await state.update_data(course_key=course_key, course=course)
        await state.set_state(LeadFlow.choosing_goal)

        await c.message.edit_text(
            f"✅ Tanlandi: <b>{course}</b>\n\nQaysi maqsad uchun o‘qimoqchisiz?",
            reply_markup=goals_menu(course_key)
        )

    # back -> main menu
    @dp.callback_query(F.data == "back:main")
    async def back_main(c: CallbackQuery, state: FSMContext):
        await c.answer()
        await state.clear()
        await c.message.edit_text(start_text(), reply_markup=main_menu())

    # -------------------------
    # USER: Goal -> Time
    # -------------------------
    @dp.callback_query(F.data.startswith("goal:"))
    async def goal_pick(c: CallbackQuery, state: FSMContext):
        await c.answer()
        parts = c.data.split(":")  # goal:<course_key>:<goal_key>
        if len(parts) != 3:
            await c.message.answer("Xatolik: goal formati noto‘g‘ri. /menu")
            return

        _, course_key, goal_key = parts
        goal = GOAL_LABEL.get((course_key, goal_key), goal_key)

        await state.update_data(goal=goal)
        await state.set_state(LeadFlow.choosing_time)

        await c.message.edit_text(
            f"✅ Maqsad: <b>{goal}</b>\n\nQaysi vaqt sizga qulay?",
            reply_markup=time_menu()
        )

    # back -> goals (for that course)
    @dp.callback_query(F.data == "back:goals")
    async def back_goals(c: CallbackQuery, state: FSMContext):
        await c.answer()
        data = await state.get_data()
        course = data.get("course", "Kurs")
        course_key = data.get("course_key", "math")

        await state.set_state(LeadFlow.choosing_goal)
        await c.message.edit_text(
            f"✅ Tanlandi: <b>{course}</b>\n\nQaysi maqsad uchun o‘qimoqchisiz?",
            reply_markup=goals_menu(course_key)
        )

    # -------------------------
    # USER: Time -> Contact
    # -------------------------
    @dp.callback_query(F.data.startswith("time:"))
    async def time_pick(c: CallbackQuery, state: FSMContext):
        await c.answer()
        time_key = c.data.split(":", 1)[1]
        time_slot = TIME_LABEL.get(time_key)

        if not time_slot:
            await c.message.answer("Xatolik: vaqt topilmadi. /menu")
            return

        await state.update_data(time_slot=time_slot)
        await state.set_state(LeadFlow.waiting_contact)

        await c.message.answer(
            "Ro‘yxatdan o‘tish uchun telefon raqamingizni yuboring 👇",
            reply_markup=contact_kb()
        )

    @dp.message(LeadFlow.waiting_contact, F.contact)
    async def got_contact(m: Message, state: FSMContext):
        data = await state.get_data()
        course = data.get("course")
        goal = data.get("goal")
        time_slot = data.get("time_slot")

        if not (course and goal and time_slot):
            await m.answer("Xatolik: ma'lumot yetarli emas. /menu")
            await state.clear()
            return

        lead_id = await db.add_lead(
            tg_user_id=m.from_user.id,
            username=m.from_user.username,
            full_name=(m.from_user.full_name or "—").strip(),
            course=course,
            goal=goal,
            time_slot=time_slot,
            phone=m.contact.phone_number,
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
        )

        # reply keyboardni olib tashlab, inline menu ko‘rsatamiz
        await m.answer(
            "Rahmat! ✅\n\nAdminimiz 5–10 daqiqa ichida siz bilan bog‘lanadi.",
            reply_markup=ReplyKeyboardRemove()
        )
        await m.answer(start_text(), reply_markup=main_menu())
        await state.clear()

        lead = await db.get_lead(lead_id)
        if lead:
            for admin_id in cfg.admin_ids:
                await safe_send(bot, admin_id, lead_card(lead), reply_markup=lead_actions_kb(lead_id))

    @dp.message(LeadFlow.waiting_contact)
    async def contact_required(m: Message):
        await m.answer("Iltimos, 📲 «Raqamni yuborish» tugmasini bosing yoki 🏠 Bosh menyu ni bosing.")

    # -------------------------
    # ADMIN: simple panel (optional)
    # -------------------------
    @dp.message(Command("admin"))
    async def admin_panel(m: Message, state: FSMContext):
        if not is_admin(m.from_user.id, cfg.admin_ids):
            return
        await state.clear()
        await m.answer("👨‍💼 Admin panel:", reply_markup=admin_menu())

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())