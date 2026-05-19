import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = "8830817537:AAG3o8U61c_cxroYxIYMjRk2AEuTZnGc2Pc"
SITE_URL = "https://sholpanyerkinkyzy.wixsite.com/kasip-navigator"
CATALOG_URL = "https://sholpanyerkinkyzy.wixsite.com/kasip-navigator/events"

logging.basicConfig(level=logging.INFO)

MBTI_QUESTIONS = [
    {"q": "1️⃣ Сынып сапарында сен...",
     "a": ("Бірінші болып сөйлеймін, жаңа достар табамын 😄", "Бір-екі жақын досыммен боламын 🙂"), "dim": "EI"},
    {"q": "2️⃣ Қиын күннен кейін демалу үшін...",
     "a": ("Достарға хабарласамын, сыртқа шығамын 🎉", "Үйде жатамын, музыка тыңдаймын 🎧"), "dim": "EI"},
]

MBTI_RESULTS = {
    "INFP": {"name": "🌸 Медиатор — INFP", "desc": "Жоғары эмпатиялы, шығармашыл адамсың.",
             "careers": ["✍️ Жазушы", "🧠 Психолог", "🎨 Дизайнер"]},
}

HOLLAND_QUESTIONS = [
    {"q": "1️⃣ Физика, химия сабақтарын жақсы көресің бе?", "type": "R"},
]

HOLLAND_RESULTS = {
    "R": {"name": "🔧 Реалистік тип", "desc": "Техникалық, практикалық жұмысты жақсы көресің.",
          "careers": ["Инженер", "IT маман"]},
}

ENT_MAP = {
    ("Математика", "Физика"): ["📐 Математика мұғалімі", "⚡ Физика мұғалімі", "💻 Компьютерлік ғылымдар"],
}


def get_ent_specialities(sub1, sub2):
    result = ENT_MAP.get((sub1, sub2)) or ENT_MAP.get((sub2, sub1))
    return result if result else ["❌ Мамандық табылмады"]


VIDEO_FILE_ID = None

# СІЗДІҢ ТЕЛЕГРАМДАҒЫ СУРЕТПЕН 100% СӘЙКЕС КЕЛЕТІН МӘТІНДЕР:
MAIN_TEXT = (
    "👋 Сәлем! *Kasip Navigator* жүйесіне қош келдіңіз!\n\n"
    "🤖 Мен сіздің AI көмекшіңіз ретінде, дұрыс мамандық таңдауыңызға көмектесемін. Бастайық!\n\n"
    "Қай бөлімге өткіңіз келеді?"
)

MAIN_KEYBOARD = [
    [InlineKeyboardButton("🧠 MBTI Тесті (Тұлға типі)", callback_data="test_mbti")],
    [InlineKeyboardButton("🎯 Профориентация Тесті (Голланд)", callback_data="test_holland")],
    [InlineKeyboardButton("📚 ЕНТ пәндері бойынша мамандық", callback_data="test_ent")]
]


async def send_main_menu(chat, context):
    global VIDEO_FILE_ID
    markup = InlineKeyboardMarkup(MAIN_KEYBOARD)
    try:
        if VIDEO_FILE_ID:
            await chat.reply_video(video=VIDEO_FILE_ID, caption=MAIN_TEXT, parse_mode="Markdown", reply_markup=markup)
        else:
            with open("video.mp4", "rb") as vf:
                sent = await chat.reply_video(video=vf, caption=MAIN_TEXT, parse_mode="Markdown", reply_markup=markup)
                VIDEO_FILE_ID = sent.video.file_id
    except Exception:
        await chat.reply_text(MAIN_TEXT, parse_mode="Markdown", reply_markup=markup)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await send_main_menu(update.message, context)


async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.clear()
    try:
        await query.delete_message()
    except Exception:
        pass
    await send_main_menu(query.message, context)


async def start_mbti(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["mbti_q"] = 0
    context.user_data["scores"] = {"E": 0, "I": 0, "S": 0, "N": 0, "T": 0, "F": 0, "J": 0, "P": 0}
    await send_mbti_question(query, context)


async def send_mbti_question(query, context):
    idx = context.user_data["mbti_q"]
    q = MBTI_QUESTIONS[idx]
    keyboard = [
        [InlineKeyboardButton(f"A) {q['a'][0]}", callback_data="mbti_A")],
        [InlineKeyboardButton(f"B) {q['a'][1]}", callback_data="mbti_B")],
    ]
    await query.message.reply_text(f"🧠 *MBTI Тесті*\n\n{q['q']}", parse_mode="Markdown",
                                   reply_markup=InlineKeyboardMarkup(keyboard))


def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(start_mbti, pattern="^test_mbti$"))
    app.add_handler(CallbackQueryHandler(restart, pattern="^restart$"))

    print("✅ Бот сәтті іске қосылды!")
    app.run_polling()


if __name__ == "__main__":
    main()