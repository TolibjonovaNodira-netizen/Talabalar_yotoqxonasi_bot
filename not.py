import asyncio
import os
import sqlite3

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
)

# =========================
# SOZLAMALAR
# =========================

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN topilmadi!")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# =========================
# MA'LUMOTLAR BAZASI
# =========================

db = sqlite3.connect("talabalar.db")
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER,
    fullname TEXT NOT NULL,
    phone TEXT NOT NULL,
    parent_fullname TEXT NOT NULL,
    parent_phone TEXT NOT NULL,
    birth_date TEXT NOT NULL,
    address TEXT NOT NULL,
    passport TEXT NOT NULL,
    faculty TEXT NOT NULL,
    course TEXT NOT NULL,
    teacher TEXT NOT NULL
)
""")

db.commit()


# =========================
# RO'YXATDAN O'TISH HOLATLARI
# =========================

class Registration(StatesGroup):
    fullname = State()
    phone = State()
    parent_fullname = State()
    parent_phone = State()
    birth_date = State()
    address = State()
    passport = State()
    faculty = State()
    course = State()
    teacher = State()
    confirm = State()


# =========================
# /START
# =========================

@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()

    await message.answer(
        "🏠 <b>Talabalar yotoqxonasi</b> botiga xush kelibsiz!\n\n"
        "Ijara yotoqxonasiga ro'yxatdan o'tish uchun "
        "ma'lumotlaringizni kiriting.\n\n"
        "👤 <b>Ism va familiyangizni kiriting:</b>",
        parse_mode="HTML"
    )

    await state.set_state(Registration.fullname)


# =========================
# ISM-FAMILIYA
# =========================

@dp.message(Registration.fullname)
async def get_fullname(message: Message, state: FSMContext):
    text = (message.text or "").strip()

    if len(text) < 3:
        await message.answer(
            "❗ Ism va familiyangizni to'liq kiriting."
        )
        return

    await state.update_data(fullname=text)

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="📱 Telefon raqamimni yuborish",
                    request_contact=True
                )
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await message.answer(
        "📱 <b>Telefon raqamingizni yuboring:</b>",
        parse_mode="HTML",
        reply_markup=keyboard
    )

    await state.set_state(Registration.phone)


# =========================
# TELEFON
# =========================

@dp.message(Registration.phone, F.contact)
async def get_phone(message: Message, state: FSMContext):
    await state.update_data(
        phone=message.contact.phone_number
    )

    await message.answer(
        "👨‍👩‍👧 <b>Ota-onangizning ism va familiyasini kiriting:</b>",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove()
    )

    await state.set_state(Registration.parent_fullname)


@dp.message(Registration.phone)
async def phone_error(message: Message):
    await message.answer(
        "❗ Iltimos, «📱 Telefon raqamimni yuborish» "
        "tugmasini bosib telefon raqamingizni yuboring."
    )


# =========================
# OTA-ONA ISM FAMILIYA
# =========================

@dp.message(Registration.parent_fullname)
async def get_parent_fullname(
    message: Message,
    state: FSMContext
):
    text = (message.text or "").strip()

    if len(text) < 3:
        await message.answer(
            "❗ Ota-onangizning ism va familiyasini to'liq kiriting."
        )
        return

    await state.update_data(parent_fullname=text)

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="📱 Ota-onamning telefon raqamini yuborish",
                    request_contact=True
                )
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await message.answer(
        "📞 <b>Ota-onangizning telefon raqamini yuboring:</b>",
        parse_mode="HTML",
        reply_markup=keyboard
    )

    await state.set_state(Registration.parent_phone)


# =========================
# OTA-ONA TELEFONI
# =========================

@dp.message(Registration.parent_phone, F.contact)
async def get_parent_phone(
    message: Message,
    state: FSMContext
):
    await state.update_data(
        parent_phone=message.contact.phone_number
    )

    await message.answer(
        "🎂 <b>Tug'ilgan sanangizni kiriting:</b>\n\n"
        "Masalan: 15.03.2005",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove()
    )

    await state.set_state(Registration.birth_date)


@dp.message(Registration.parent_phone)
async def parent_phone_error(message: Message):
    await message.answer(
        "❗ Iltimos, telefon raqamini tugma orqali yuboring."
    )


# =========================
# TUG'ILGAN SANA
# =========================

@dp.message(Registration.birth_date)
async def get_birth_date(
    message: Message,
    state: FSMContext
):
    text = (message.text or "").strip()

    if len(text) < 8:
        await message.answer(
            "❗ Tug'ilgan sanani to'g'ri kiriting.\n"
            "Masalan: 15.03.2005"
        )
        return

    await state.update_data(birth_date=text)

    await message.answer(
        "🏠 <b>Doimiy manzilingizni kiriting:</b>",
        parse_mode="HTML"
    )

    await state.set_state(Registration.address)


# =========================
# MANZIL
# =========================

@dp.message(Registration.address)
async def get_address(
    message: Message,
    state: FSMContext
):
    text = (message.text or "").strip()

    if len(text) < 5:
        await message.answer(
            "❗ Manzilingizni to'liqroq kiriting."
        )
        return

    await state.update_data(address=text)

    await message.answer(
        "🪪 <b>Pasport seriya va raqamingizni kiriting:</b>\n\n"
        "Masalan: AA1234567",
        parse_mode="HTML"
    )

    await state.set_state(Registration.passport)


# =========================
# PASPORT
# =========================

@dp.message(Registration.passport)
async def get_passport(
    message: Message,
    state: FSMContext
):
    text = (message.text or "").strip().upper()

    if len(text) < 5:
        await message.answer(
            "❗ Pasport seriya va raqamini to'g'ri kiriting."
        )
        return

    await state.update_data(passport=text)

    await message.answer(
        "🎓 <b>Fakultetingiz nomini kiriting:</b>",
        parse_mode="HTML"
    )

    await state.set_state(Registration.faculty)


# =========================
# FAKULTET
# =========================

@dp.message(Registration.faculty)
async def get_faculty(
    message: Message,
    state: FSMContext
):
    text = (message.text or "").strip()

    if len(text) < 2:
        await message.answer(
            "❗ Fakultet nomini kiriting."
        )
        return

    await state.update_data(faculty=text)

    await message.answer(
        "📚 <b>Nechinchi kursda o'qiysiz?</b>\n\n"
        "Masalan: 1-kurs",
        parse_mode="HTML"
    )

    await state.set_state(Registration.course)


# =========================
# KURS
# =========================

@dp.message(Registration.course)
async def get_course(
    message: Message,
    state: FSMContext
):
    text = (message.text or "").strip()

    if len(text) < 1:
        await message.answer(
            "❗ Kurs raqamini kiriting."
        )
        return

    await state.update_data(course=text)

    await message.answer(
        "👨‍🏫 <b>O'qituvchingizning ism va familiyasini kiriting:</b>",
        parse_mode="HTML"
    )

    await state.set_state(Registration.teacher)


# =========================
# O'QITUVCHI
# =========================

@dp.message(Registration.teacher)
async def get_teacher(
    message: Message,
    state: FSMContext
):
    text = (message.text or "").strip()

    if len(text) < 3:
        await message.answer(
            "❗ O'qituvchining ism va familiyasini to'liq kiriting."
        )
        return

    await state.update_data(teacher=text)

    data = await state.get_data()

    summary = (
        "📋 <b>MA'LUMOTLARINGIZNI TEKSHIRING</b>\n\n"
        f"👤 Ism-familiya: {data['fullname']}\n"
        f"📱 Telefon: {data['phone']}\n"
        f"👨‍👩‍👧 Ota-ona: {data['parent_fullname']}\n"
        f"📞 Ota-ona telefoni: {data['parent_phone']}\n"
        f"🎂 Tug'ilgan sana: {data['birth_date']}\n"
        f"🏠 Manzil: {data['address']}\n"
        f"🪪 Pasport: {data['passport']}\n"
        f"🎓 Fakultet: {data['faculty']}\n"
        f"📚 Kurs: {data['course']}\n"
        f"👨‍🏫 O'qituvchi: {data['teacher']}\n\n"
        "Ma'lumotlaringiz to'g'rimi?"
    )

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="✅ Tasdiqlash"),
                KeyboardButton(text="❌ Qayta kiritish")
            ]
        ],
        resize_keyboard=True
    )

    await message.answer(
        summary,
        parse_mode="HTML",
        reply_markup=keyboard
    )

    await state.set_state(Registration.confirm)


# =========================
# QAYTA KIRITISH
# =========================

@dp.message(
    Registration.confirm,
    F.text == "❌ Qayta kiritish"
)
async def restart(
    message: Message,
    state: FSMContext
):
    await state.clear()

    await message.answer(
        "🔄 Ro'yxatdan o'tish qaytadan boshlandi.\n\n"
        "👤 <b>Ism va familiyangizni kiriting:</b>",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove()
    )

    await state.set_state(Registration.fullname)


# =========================
# TASDIQLASH
# =========================

@dp.message(
    Registration.confirm,
    F.text == "✅ Tasdiqlash"
)
async def confirm(
    message: Message,
    state: FSMContext
):
    data = await state.get_data()

    cursor.execute(
        """
        INSERT INTO students (
            telegram_id,
            fullname,
            phone,
            parent_fullname,
            parent_phone,
            birth_date,
            address,
            passport,
            faculty,
            course,
            teacher
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            message.from_user.id,
            data["fullname"],
            data["phone"],
            data["parent_fullname"],
            data["parent_phone"],
            data["birth_date"],
            data["address"],
            data["passport"],
            data["faculty"],
            data["course"],
            data["teacher"],
        )
    )

    db.commit()

    await message.answer(
        "✅ <b>Ro'yxatdan muvaffaqiyatli o'tdingiz!</b>\n\n"
        "Ma'lumotlaringiz yotoqxona ro'yxatiga saqlandi.",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove()
    )

    # ADMINGA XABAR
    if ADMIN_ID != 0:
        admin_text = (
            "🏠 <b>YANGI TALABA RO'YXATDAN O'TDI</b>\n\n"
            f"👤 Ism-familiya: {data['fullname']}\n"
            f"📱 Telefon: {data['phone']}\n"
            f"👨‍👩‍👧 Ota-ona: {data['parent_fullname']}\n"
            f"📞 Ota-ona telefoni: {data['parent_phone']}\n"
            f"🎂 Tug'ilgan sana: {data['birth_date']}\n"
            f"🏠 Manzil: {data['address']}\n"
            f"🪪 Pasport: {data['passport']}\n"
            f"🎓 Fakultet: {data['faculty']}\n"
            f"📚 Kurs: {data['course']}\n"
            f"👨‍🏫 O'qituvchi: {data['teacher']}"
        )

        try:
            await bot.send_message(
                ADMIN_ID,
                admin_text,
                parse_mode="HTML"
            )
        except Exception as error:
            print("Admin xabarida xatolik:", error)

    await state.clear()


# =========================
# BOTNI ISHGA TUSHIRISH
# =========================

async def main():
    print("🤖 Talabalar yotoqxonasi boti ishga tushdi!")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
