"""
Kasip Navigator Telegram Bot
MBTI + Голланд профориентация тесттері (қазақша)
pip install python-telegram-bot==20.7
"""

import logging
import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, ConversationHandler
)

# ========================
# НАСТРОЙКА БЕЗОПАСНОСТИ
# ========================
# Загружаем переменные из файла .env
load_dotenv()

# Безопасно достаем токен из системы (из файла .env)
BOT_TOKEN = os.getenv("BOT_TOKEN")

SITE_URL = "https://sholpanyerkinkyzy.wixsite.com/kasip-navigator"
PROFTEST_URL = "https://sholpanyerkinkyzy.wixsite.com/kasip-navigator/admissions"
CATALOG_URL = "https://sholpanyerkinkyzy.wixsite.com/kasip-navigator/events"

logging.basicConfig(level=logging.INFO)

# ========================
# MBTI СҰРАҚТАРЫ (16 сұрақ) — мектеп оқушыларына арналған
# ========================
MBTI_QUESTIONS = [
    # E vs I — Экстраверт / Интроверт
    {
        "q": "1️⃣ Сынып сапарында немесе мектеп шарасында сен...",
        "a": ("Бірінші болып сөйлеймін, жаңа достар табамын 😄", "Бір-екі жақын досыммен боламын, жаттарға қосылмаймын 🙂"),
        "dim": "EI"
    },
    {
        "q": "2️⃣ Қиын күннен кейін демалу үшін сен...",
        "a": ("Достарға хабарласамын, сыртқа шығамын 🎉", "Үйде жатамын, музыка тыңдаймын немесе ойнаймын 🎧"),
        "dim": "EI"
    },
    {
        "q": "3️⃣ Сынып алдында сөйлеу керек болса...",
        "a": ("Жақсы көремін, мен үшін оңай 👏", "Нервтенемін, мүмкін болса жазбаша тапсырамын 😅"),
        "dim": "EI"
    },
    {
        "q": "4️⃣ Жаңа сынып немесе жаңа топқа келгенде...",
        "a": ("Өзім барып танысамын, тез кірігемін 🤝", "Мені алдымен байқап алады, өзім бірте-бірте ашыламын 👀"),
        "dim": "EI"
    },
    # S vs N — Сенсорлы / Интуитивті
    {
        "q": "5️⃣ Сабақта ne жақсы көресің?",
        "a": ("Нақты есептер, фактілер, тәжірибелер 📐", "Неге солай? деп ойлану, жаңа идеялар талқылау 🤔"),
        "dim": "SN"
    },
    {
        "q": "6️⃣ Болашақ мамандық туралы ойлағанда...",
        "a": ("Нақты білемін, қадамдарды жоспарладым ✅", "Қызықты идеяларым бар, бірақ әлі нақты емес 🌈"),
        "dim": "SN"
    },
    {
        "q": "7️⃣ Реферат немесе жоба жазғанда сен...",
        "a": ("Нақты деректер мен мысалдар іздеймін 📊", "Өз идеямды қосамын, шығармашыл тәсіл қолданамын 🎨"),
        "dim": "SN"
    },
    {
        "q": "8️⃣ Фильм немесе кітап таңдағанда...",
        "a": ("Шынайы оқиғаларды, документалды жақсы көремін 🎬", "Фантастика, ғылыми-фантастика, магия жақсы көремін ✨"),
        "dim": "SN"
    },
    # T vs F — Ойлаушы / Сезімтал
    {
        "q": "9️⃣ Достарың дауласып қалса, сен...",
        "a": ("Кім дұрыс, кім бұрыс екенін логикамен анықтаймын ⚖️", "Екі жақтың да сезімін ескеремін, татуластырамын 💛"),
        "dim": "TF"
    },
    {
        "q": "🔟 Мұғалім сенің жұмысыңды сынаса...",
        "a": ("Нені дұрыс жасамағанымды түсінгім келеді, сезімге мән бермеймін 📝", "Алдымен ренжимін, бірақ кейін түсінемін 😔"),
        "dim": "TF"
    },
    {
        "q": "1️⃣1️⃣ Топта шешім қабылдағанда...",
        "a": ("Ең тиімді және логикалық шешімді таңдаймын 🧠", "Барлығы қуанышты болатын шешімді таңдаймын 🤗"),
        "dim": "TF"
    },
    {
        "q": "1️⃣2️⃣ Кино кейіпкері өлсе сен...",
        "a": ("Сюжеттің логикасын ойлаймын 🎭", "Жылап немесе күйзеліп кетемін 😢"),
        "dim": "TF"
    },
    # J vs P — Жоспарлаушы / Икемді
    {
        "q": "1️⃣3️⃣ Үй тапсырмасын...",
        "a": ("Бірінші отырып бітіремін, кешіктірмеймін 📅", "Дедлайн жақындаса ғана жасаймын 😬"),
        "dim": "JP"
    },
    {
        "q": "1️⃣4️⃣ Каникулды қалай өткізесің?",
        "a": ("Алдын ала жоспар жасаймын, күн санап белгілеймін 🗓️", "Не болса сол, спонтанды кетемін 🌍"),
        "dim": "JP"
    },
    {
        "q": "1️⃣5️⃣ Сенің сөмкең/үстелің...",
        "a": ("Тәртіпті, бәрі өз орнында 🗂️", "Кейде ретсіз, бірақ маған түсінікті 😄"),
        "dim": "JP"
    },
    {
        "q": "1️⃣6️⃣ Жаңа ереже немесе өзгеріс болса...",
        "a": ("Тез бейімделемін, жоспарымды өзгертемін ✔️", "Ыңғайсыз болады, кенеттен өзгеріс ұнамайды 😤"),
        "dim": "JP"
    },
]

MBTI_RESULTS = {
    "INTJ": {
        "name": "🧠 Стратег — INTJ",
        "desc": "Сен терең ойлайтын, стратегиялық жоспар құра білетін адамсың. Күрделі мәселелерді шешуді жақсы көресің, жалғыз жұмыс жасауды ұнатасың. Болашақты алдын ала көре аласың.",
        "careers": ["💻 Бағдарламалаушы / IT-архитектор", "📊 Инвестициялық банкир / Қаржы талдаушы", "⚖️ Корпоративтік заңгер", "🔬 Ғалым / Зерттеуші", "📋 Жоба менеджері", "🏛️ Дипломат / Саясат кеңесшісі"]
    },
    "INTP": {
        "name": "🔬 Логик — INTP",
        "desc": "Сен аналитикалық ойлайтын, теорияны жақсы түсінетін адамсың. Күрделі жүйелерді зерттеп, жаңа идеялар ойлап тапқанды жақсы көресің.",
        "careers": ["💻 Бағдарламалаушы / Разработчик", "🧮 Математик / Статистик", "🔭 Физик / Химик", "🤖 AI / Жасанды интеллект маманы", "📐 Архитектор", "🧠 Философ / Ғалым"]
    },
    "ENTJ": {
        "name": "👑 Командир — ENTJ",
        "desc": "Сен туа біткен көшбасшысың. Адамдарды жетелей аласың, стратегиялық шешімдер қабылдайсың. Биік мақсаттарға жетуді ұнатасың.",
        "careers": ["🏢 Бизнес директоры / CEO", "⚖️ Судья / Нотариус", "🏛️ Мемлекет қайраткері / Саясаткер", "📊 Бизнес-кеңесші / Стратег", "🎓 Университет ректоры", "🚀 Стартап негізін қалаушы"]
    },
    "ENTP": {
        "name": "💡 Өнертапқыш — ENTP",
        "desc": "Сен шығармашыл, жаңашыл ойлайтын адамсың. Дауласуды, идея генерациялауды жақсы көресің. Дайын шешімдерге сенбейсің, өзіңше іздейсің.",
        "careers": ["📱 Стартап негізін қалаушы / Кәсіпкер", "📰 Журналист / Редактор", "⚖️ Заңгер / Адвокат", "📣 PR-маман / Бренд-менеджер", "🧪 Инженер-өнертапқыш", "🎙️ Теле/радио жүргізушісі"]
    },
    "INFJ": {
        "name": "🌟 Кеңесші — INFJ",
        "desc": "Сен интуициясы күшті, адамдарды жақсы түсінетін адамсың. Дүниені жақсартуға ұмтыласың, терең мағыналы жұмыс жасағанды жақсы көресің.",
        "careers": ["🧠 Психотерапевт / Психолог", "👨‍🏫 Мұғалім / Тьютор", "✍️ Жазушы / Блогер", "🌍 Социолог / Антрополог", "🎗️ Гуманитарлық ұйым қызметкері", "🩺 Дәрігер / Психиатр"]
    },
    "INFP": {
        "name": "🌸 Медиатор — INFP",
        "desc": "Сен жоғары эмпатиялы, шығармашыл, мәнге бағытталған адамсың. Адамдарға қолдау беруді, өнер арқылы өзіңді білдіруді жақсы көресің.",
        "careers": ["✍️ Жазушы / Сценарист", "🧠 Психолог / Кеңесші", "👨‍🏫 Мұғалім / Тьютор", "🎨 Иллюстратор / Дизайнер", "🎵 Музыкант / Өнер маманы", "🌍 Әлеуметтік қызметші"]
    },
    "ENFJ": {
        "name": "🌠 Ұстаз — ENFJ",
        "desc": "Сен адамдарды жетелей алатын, шабыттандыра білетін харизматты адамсың. Басқалардың өсуіне көмектесу — сенің табиғи қасиетің.",
        "careers": ["👨‍🏫 Мұғалім / Оқытушы", "🧠 Психолог / Коуч", "👥 HR-маман / Оқыту жетекшісі", "🌍 Әлеуметтік қызметші", "🏛️ Саясаткер / Қоғам қайраткері", "🩺 Нутрициолог / Дәрігер"]
    },
    "ENFP": {
        "name": "🎨 Инноватор — ENFP",
        "desc": "Сен энергиялы, шығармашыл, адамдарды шабыттандыра алатын адамсың. Жаңа идеялар мен мүмкіндіктер іздейсің, бір жерде тұрып қалмайсың.",
        "careers": ["📣 Маркетолог / PR-маман", "📰 Журналист / Контент-маман", "🎙️ Коуч / Мотивациялық спикер", "🎨 Дизайнер / Шығармашыл директор", "👨‍🏫 Мұғалім / Тренер", "🚀 Кәсіпкер / Жоба менеджері"]
    },
    "ISTJ": {
        "name": "📋 Инспектор — ISTJ",
        "desc": "Сен сенімді, жауапты, тәртіпті адамсың. Нақты фактілерге сүйенесің, жұмысыңды 100% орындайсың. Тұрақтылық пен тәртіпті бағалайсың.",
        "careers": ["💰 Қаржы талдаушы / Аудитор", "⚖️ Адвокат / Нотариус", "🏗️ Инженер / Техник", "🛡️ Салық инспекторы / Мемлекет қызметші", "🖥️ Жүйе администраторы", "🏥 Радиолог / Дәрігер"]
    },
    "ISFJ": {
        "name": "🛡️ Қорғаушы — ISFJ",
        "desc": "Сен мейірімді, жауапты, адамдарды қамқорлайтын адамсың. Басқаларға көмек беру — сенің күшің. Ұзақ мерзімді, сенімді қарым-қатынас орнатасың.",
        "careers": ["🩺 Медбике / Дәрігер", "👨‍🏫 Педагог / Тәрбиеші", "🌍 Әлеуметтік қызметші", "🧠 Психолог / Кеңесші", "👥 HR-маман", "🌿 Эколог / Ветеринар"]
    },
    "ESTJ": {
        "name": "🏛️ Басқарушы — ESTJ",
        "desc": "Сен ұйымдастыра білетін, тәртіпті, жоғары жауапкершілікті мойнына алатын адамсың. Нақты ережелер мен құрылым ішінде жақсы жұмыс жасайсың.",
        "careers": ["🏢 Менеджер / Директор", "⚖️ Судья / Прокурор", "💼 Қаржы директоры / CFO", "🎓 Мектеп директоры / Декан", "🏥 Фармацевт / Медицина менеджері", "🚚 Логистика менеджері"]
    },
    "ESFJ": {
        "name": "🤝 Консул — ESFJ",
        "desc": "Сен адамдармен тіл табыса алатын, қамқор, дисциплинді адамсың. Басқалар сенімен қауіпсіз сезінеді. Адамдар арасын жақсартуды ұнатасың.",
        "careers": ["🧠 Психолог / Логопед", "👨‍🏫 Мұғалім / Педагог", "🌍 Әлеуметтік қызметші", "🎉 Іс-шара ұйымдастырушысы", "📣 PR-маман / Қызмет менеджері", "🏨 Қонақүй / Ресторан менеджері"]
    },
    "ISTP": {
        "name": "🔧 Шебер — ISTP",
        "desc": "Сен практикалық, іске бейім, техниканы жақсы түсінетін адамсың. Қолыңмен жасауды, механизмдерді зерттеуді жақсы көресің. Икемді және дербессің.",
        "careers": ["⚙️ Инженер / Механик", "💻 IT-маман / Кибер қауіпсіздік", "🤖 Робототехник", "✈️ Ұшқыш / Техник", "🏥 Хирург / Дәрігер", "🎨 Өнеркәсіп дизайнері"]
    },
    "ISFP": {
        "name": "🎨 Суретші — ISFP",
        "desc": "Сен шығармашыл, сезімтал, сұлулықты сезе алатын адамсың. Жесткий ережелерді ұнатпайсың, өзіңдік стилің бар. Адамдармен гармония іздейсің.",
        "careers": ["🎨 Графикалық / Интерьер дизайнері", "📸 Фотограф / Видеограф", "🎵 Музыкант / Дыбыс маманы", "🌿 Зоолог / Ветеринар", "🍽️ Аспаз / Кондитер", "🌸 Бақташы / Флорист"]
    },
    "ESTP": {
        "name": "⚡ Кәсіпкер — ESTP",
        "desc": "Сен энергиялы, іске бейім, жылдам шешім қабылдайтын адамсың. Тәуекел алудан қорықпайсың. Адамдармен тіл табысасың, жаңа нәрселерге ашықсың.",
        "careers": ["🚀 Кәсіпкер / Бизнесмен", "📊 Сату маманы / Брокер", "🏋️ Спорт тренері / Спортшы", "🚒 Құтқарушы / Авариялық қызмет", "🎙️ Спортшы / Каскадер", "✈️ Ұшқыш / Нұсқаушы"]
    },
    "ESFP": {
        "name": "🎉 Энтузиаст — ESFP",
        "desc": "Сен харизматты, оптимистік, адамдарды қуантатын адамсың. Жаңалық пен тәжірибе іздейсің. Атмосфера жасай аласың, адамдарды бірлестіресің.",
        "careers": ["🎭 Актер / Ведущий", "🎪 Аниматор / Event-менеджер", "👨‍🏫 Мұғалім / Тренер", "🏋️ Фитнес тренері / Спортшы", "📣 Сату кеңесшісі / Промоутер", "✈️ Туризм менеджері / Гид"]
    },
}

# ========================
# ГОЛЛАНД СҰРАҚТАРЫ (18 сұрақ)
# ========================
HOLLAND_QUESTIONS = [
    # ===== R — РЕАЛИСТІК =====
    {
        "q": "1️⃣ Сен мектепте физика, химия немесе технология сабақтарын жақсы көресің бе?\n\n💡 Яғни — нақты заттармен, формулалармен, тәжірибелермен жұмыс жасағанды ұнатасың ба?",
        "type": "R"
    },
    {
        "q": "2️⃣ Бұзылған нәрсені өзің жөндегің немесе қандай да бір құрал-жабдықпен жұмыс жасағың келе ме?\n\n💡 Мысалы: велосипед жөндеу, компьютер бөлшектеу, ұя жасау сияқты нәрселер.",
        "type": "R"
    },
    {
        "q": "3️⃣ Табиғатта болуды, жануарлармен немесе өсімдіктермен жұмыс жасауды жақсы көресің бе?\n\n💡 Мысалы: бақша өсіру, жануарлар күту, экскурсияда табиғатты зерттеу.",
        "type": "R"
    },
    # ===== I — ЗЕРТТЕУШІЛІК =====
    {
        "q": "4️⃣ «Неліктен?» деген сұрақ сені көп ойландыра ма?\n\n💡 Мысалы: аспан неге көк? адам неге түс көреді? жер сілкінісі қалай болады? — мұндай сұрақтарды іздеп зерттейсің бе?",
        "type": "I"
    },
    {
        "q": "5️⃣ Математика немесе ғылым пәндерінде күрделі есеп шыққанда — оны шешу сені қызықтыра ма, жалықтырмай ма?\n\n💡 Жауап тапқан кезде «Ааа, түсіндім!» деп қуанасың ба?",
        "type": "I"
    },
    {
        "q": "6️⃣ Интернеттен немесе кітаптан бір тақырыпты терең оқып-зерттегің келе ме?\n\n💡 Мысалы: ғарыш, жасанды интеллект, тарих, биология — бір тақырыпқа сағаттап кіріп кетесің бе?",
        "type": "I"
    },
    # ===== A — ШЫҒАРМАШЫЛ =====
    {
        "q": "7️⃣ Сурет салу, музыка тыңдау немесе ойнау, би билеу, photo/видео түсіру сені шын қызықтыра ма?\n\n💡 Бос уақытыңда осы нәрселерді өз қалауыңмен жасайсың ба?",
        "type": "A"
    },
    {
        "q": "8️⃣ Мектепте шығарма, эссе немесе шығармашыл жоба жасағанда — бұл сен үшін қызықты ма?\n\n💡 Өз идеяңды, өз стиліңді қосқанда жақсы көресің бе?",
        "type": "A"
    },
    {
        "q": "9️⃣ Театр, кино, дизайн, сәулет немесе мода сияқты өнер салаларына қызығушылығың бар ма?\n\n💡 Мысалы: фильм сценарийі жазу, үй интерьерін ойластыру, киім дизайны — осындай нәрселер сені тартады ма?",
        "type": "A"
    },
    # ===== S — ӘЛЕУМЕТТІК =====
    {
        "q": "🔟 Достарың немесе сыныптастарың саған мәселесін айтқанда — тыңдап, көмектесуге дайын боласың ба?\n\n💡 Адамдардың жайын сұрайтын, олардың сезімін ескеретін адам сенсің бе?",
        "type": "S"
    },
    {
        "q": "1️⃣1️⃣ Кішіге үйрету немесе топта бірге жұмыс жасау сені жалықтырмай ма?\n\n💡 Мысалы: бауырыңа немесе досыңа сабақ түсіндіру, топ жобасында белсенді болу.",
        "type": "S"
    },
    {
        "q": "1️⃣2️⃣ Болашақта адамдарға тікелей пайда беретін мамандықта жұмыс жасағың келе ме?\n\n💡 Мысалы: дәрігер, мұғалім, психолог, әлеуметтік қызметші — адамдарға қызмет ету идеясы ұнай ма?",
        "type": "S"
    },
    # ===== E — КӘСІПКЕРЛІК =====
    {
        "q": "1️⃣3️⃣ Топта немесе ойында басшы болуды, шешім қабылдауды ұнатасың ба?\n\n💡 Мысалы: сынып старостасы, команда капитаны, жоба жетекшісі — осы рөлдер сені қорқытпай, керісінше тартады ма?",
        "type": "E"
    },
    {
        "q": "1️⃣4️⃣ Адамдарды өз идеяңа сендіру немесе бір нәрсені «сату» (идея, жоба, пікір) сен үшін оңай ма?\n\n💡 Мысалы: досыңды бір нәрсеге көндіру, мектеп жобаңды жақсы қорғау.",
        "type": "E"
    },
    {
        "q": "1️⃣5️⃣ Болашақта өз бизнесіңді ашу немесе бір ұйымды басқару туралы ойлайсың ба?\n\n💡 Кәсіпкер, менеджер, саясатшы, заңгер сияқты мамандықтар сені қызықтыра ма?",
        "type": "E"
    },
    # ===== C — КОНВЕНЦИОНАЛДЫ =====
    {
        "q": "1️⃣6️⃣ Нақты тапсырмаларды мұқият, қателіксіз орындау сен үшін маңызды ма?\n\n💡 Мысалы: кесте жасау, есеп толтыру, тізімді реттеу — осындай жұмыс сені тыныштандыра ма?",
        "type": "C"
    },
    {
        "q": "1️⃣7️⃣ Ақша, сандар, статистика немесе экономика тақырыптары сені қызықтыра ма?\n\n💡 Мысалы: бюджет жоспарлау, математикалық есептер, Excel кестелері — осы нәрселер сені жалықтырмай ма?",
        "type": "C"
    },
    {
        "q": "1️⃣8️⃣ Нақты ережелер мен тәртіп болған ортада жұмыс жасау саған ыңғайлы ма?\n\n💡 Мысалы: мемлекеттік қызмет, банк, бухгалтерия — нақты жүйе бойынша жұмыс сені қорқытпай ма?",
        "type": "C"
    },
]

HOLLAND_RESULTS = {
    "R": {
        "name": "🔧 Реалистік (Realistic)",
        "desc": "Техникалық, практикалық жұмысты жақсы көресің.",
        "careers": ["Инженер", "Механик", "Агроном", "Құрылысшы", "IT-маман"]
    },
    "I": {
        "name": "🔬 Зерттеушілік (Investigative)",
        "desc": "Ғылым, талдау, зерттеуді жақсы көресің.",
        "careers": ["Дәрігер", "Ғалым", "Математик", "Психолог", "Фармацевт"]
    },
    "A": {
        "name": "🎨 Шығармашыл (Artistic)",
        "desc": "Өнер, дизайн, шығармашылықты жақсы көресің.",
        "careers": ["Дизайнер", "Сурет маманы", "Музыкант", "Жазушы", "Фотограф"]
    },
    "S": {
        "name": "🤝 Әлеуметтік (Social)",
        "desc": "Адамдармен жұмыс жасауды, көмектесуді жақсы көресің.",
        "careers": ["Педагог", "Психолог", "Дәрігер", "Социолог", "HR маман"]
    },
    "E": {
        "name": "🚀 Кәсіпкерлік (Enterprising)",
        "desc": "Жетекшілік, бизнес, сендіруді жақсы көресің.",
        "careers": ["Менеджер", "Кәсіпкер", "Заңгер", "Журналист", "Саясаткер"]
    },
    "C": {
        "name": "📊 Конвенционалды (Conventional)",
        "desc": "Тәртіп, деректер, нақтылықты жақсы көресің.",
        "careers": ["Бухгалтер", "Экономист", "Банкир", "Программист", "Мемлекеттік қызметші"]
    },
}

# ========================
# ЕНТ ПӘНДЕРІ МЕН МАМАНДЫҚТАР
# ========================
ENT_SUBJECTS = [
    "Математика", "Физика", "Химия", "Биология",
    "География", "Дүниежүзі тарихы", "Информатика",
    "Қазақ тілі", "Қазақ әдебиеті", "Орыс тілі",
    "Орыс әдебиеті", "Шет тілі", "Адам. Қоғам. Құқық",
    "Шығармашылық емтихан"
]

ENT_MAP = {
    ("Математика", "Физика"): [
        "📐 Математика мұғалімін даярлау",
        "⚡ Физика мұғалімін даярлау",
        "🔭 Физика (ғылым)",
        "🧮 Математика және статистика",
        "🏗️ Механика және металл өңдеу",
        "🚗 Қозғалтқыштар мен автокөліктер",
        "⚙️ Электр және жылу энергетикасы",
        "📡 Электроника, автоматика және байланыс",
        "🏢 Құрылыс және азаматтық инженерия",
        "⛏️ Тау-кен ісі",
        "🛡️ Әскери іс және қауіпсіздік",
        "🔒 Тіршілік әрекетінің қауіпсіздігі",
    ],
    ("Математика", "Информатика"): [
        "💻 Компьютерлік ғылымдар",
        "📱 Бағдарламалық жасақтама (Разработка)",
        "🔐 Желілер және киберқауіпсіздік",
        "🖥️ Ақпараттық технологиялар",
        "👨‍🏫 Информатика мұғалімін даярлау",
    ],
    ("Математика", "География"): [
        "💰 Аудит және салық салу",
        "🏦 Қаржы, экономика, банк және сақтандыру",
        "📊 Менеджмент және басқару",
        "📣 Маркетинг және жарнама",
        "🗺️ Геодезия және картография",
        "🏨 Қонақ үй бизнесі және мейрамхана ісі",
        "✈️ Туризм",
        "🚚 Көлік қызметтері (Логистика)",
        "⚖️ Құқық және экономика негіздері мұғалімін даярлау",
    ],
    ("Биология", "Химия"): [
        "🩺 Медицина (Жалпы медицина, Педиатрия)",
        "🦷 Стоматология",
        "💊 Фармация",
        "👩‍⚕️ Мейіргер ісі",
        "🧬 Биологиялық ғылымдар",
        "⚗️ Химия (ғылым)",
        "🌾 Өсімдік шаруашылығы",
        "🐄 Мал шаруашылығы",
        "🐟 Балық шаруашылығы",
        "🐾 Ветеринария",
        "🧪 Химиялық инженерия",
        "🍞 Тамақ өнімдерін өндіру",
        "👨‍🏫 Химия мұғалімін даярлау",
        "👨‍🏫 Биология мұғалімін даярлау",
    ],
    ("Биология", "География"): [
        "🧠 Психология",
        "🌍 Әлеуметтік жұмыс",
        "👨‍🏫 Педагогика және психология",
        "👶 Мектепке дейінгі оқыту және тәрбиелеу",
        "📚 Бастауышта оқыту педагогикасы",
        "👨‍👧 Әлеуметтік педагогтарды даярлау",
        "🌿 Орман шаруашылығы",
        "🌎 Қоршаған орта",
    ],
    ("Дүниежүзі тарихы", "География"): [
        "📜 Тарих",
        "🏛️ Философия және этика",
        "🌍 Әлеуметтану",
        "🗺️ Геология және география",
        "🎭 Мәдениеттану",
        "🏛️ Саясаттану",
        "📚 Кітапхана ісі және мұрағаттану",
        "👨‍🏫 География мұғалімін даярлау",
        "👨‍🏫 Гуманитарлық пәндер мұғалімін даярлау",
    ],
    ("Дүниежүзі тарихы", "Адам. Қоғам. Құқық"): [
        "⚖️ Құқық (Юриспруденция)",
        "🕌 Дінтану және теология",
    ],
    ("Шет тілі", "Дүниежүзі тарихы"): [
        "🌐 Тіл білімі (Лингвистика)",
        "📝 Аударма ісі",
        "👨‍🏫 Шет тілі мұғалімін даярлау",
    ],
    ("Қазақ тілі", "Қазақ әдебиеті"): [
        "📖 Әдебиеттану және кітап ісі",
        "👨‍🏫 Қазақ тілі мен әдебиеті мұғалімін даярлау",
    ],
    ("Орыс тілі", "Орыс әдебиеті"): [
        "📖 Орыс әдебиеттануы",
        "👨‍🏫 Орыс тілі мен әдебиеті мұғалімін даярлау",
    ],
    ("Шығармашылық емтихан", "Шығармашылық емтихан"): [
        "🎨 Өнер",
        "👗 Сән және дизайн",
        "🏛️ Сәулет (Архитектура)",
        "🎵 Музыка мұғалімін даярлау",
        "🖌️ Көркем еңбек және сызу мұғалімін даярлау",
        "📰 Журналистика және репортер ісі",
        "🏋️ Дене шынықтыру мұғалімін даярлау",
        "🪖 Бастапқы әскери дайындық мұғалімін даярлау",
    ],
}

def get_ent_specialities(sub1: str, sub2: str):
    key1 = (sub1, sub2)
    key2 = (sub2, sub1)
    result = ENT_MAP.get(key1) or ENT_MAP.get(key2)
    if result:
        return result
    found = []
    for (s1, s2), specs in ENT_MAP.items():
        if sub1 in (s1, s2) or sub2 in (s1, s2):
            found.extend(specs)
    return list(dict.fromkeys(found)) if found else ["❌ Бұл пән жұбы бойынша мамандық табылмады"]

(CHOOSING_TEST, MBTI_Q, MBTI_DONE, HOLLAND_Q, HOLLAND_DONE, ENT_SUB1, ENT_SUB2) = range(7)

# ========================
# START
# ========================
VIDEO_FILE_ID = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global VIDEO_FILE_ID
    context.user_data.clear()
    keyboard = [
        [InlineKeyboardButton("🧠 MBTI Тесті (Тұлға типі)", callback_data="test_mbti")],
        [InlineKeyboardButton("🎯 Профориентация Тесті (Голланд)", callback_data="test_holland")],
        [InlineKeyboardButton("📚 ЕНТ пәндері бойынша мамандық", callback_data="test_ent")],
        [InlineKeyboardButton("🌐 Kasip Navigator Сайты", url=SITE_URL)],
    ]
    text = (
        "👋 Сәлем! *Kasip Navigator* ботына қош келдің!\n\n"
        "Мен саған:\n"
        "✅ MBTI тесті арқылы тұлға типіңді анықтаймын\n"
        "✅ Профориентация тесті арқылы мамандық ұсынамын\n"
        "✅ ЕНТ пәндерің бойынша мамандықтар табамын\n\n"
        "Қайсысын таңдайсың?"
    )
    markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        try:
            if VIDEO_FILE_ID:
                await update.message.reply_video(video=VIDEO_FILE_ID)
            else:
                with open("video.mp4", "rb") as video_file:
                    sent = await update.message.reply_video(video=video_file)
                VIDEO_FILE_ID = sent.video.file_id
        except Exception:
            pass
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=markup)
    else:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=markup)

    return CHOOSING_TEST

# ========================
# ЕНТ — ПӘН ТАНДАУ
# ========================
async def start_ent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("Математика", callback_data="ent1_Математика"),
         InlineKeyboardButton("Физика", callback_data="ent1_Физика")],
        [InlineKeyboardButton("Химия", callback_data="ent1_Химия"),
         InlineKeyboardButton("Биология", callback_data="ent1_Биология")],
        [InlineKeyboardButton("География", callback_data="ent1_География"),
         InlineKeyboardButton("Информатика", callback_data="ent1_Информатика")],
        [InlineKeyboardButton("Дүниежүзі тарихы", callback_data="ent1_Дүниежүзі тарихы")],
        [InlineKeyboardButton("Қазақ тілі", callback_data="ent1_Қазақ тілі"),
         InlineKeyboardButton("Қазақ әдебиеті", callback_data="ent1_Қазақ әдебиеті")],
        [InlineKeyboardButton("Орыс тілі", callback_data="ent1_Орыс тілі"),
         InlineKeyboardButton("Орыс әдебиеті", callback_data="ent1_Орыс әдебиеті")],
        [InlineKeyboardButton("Шет тілі", callback_data="ent1_Шет тілі")],
        [InlineKeyboardButton("Адам. Қоғам. Құқық", callback_data="ent1_Адам. Қоғам. Құқық")],
        [InlineKeyboardButton("🎨 Шығармашылық емтихан", callback_data="ent1_Шығармашылық емтихан")],
    ]
    text = "📚 *ЕНТ бойынша мамандық іздеу*\n\n1️⃣ *Бірінші пәніңді* таңда:"
    markup = InlineKeyboardMarkup(keyboard)

    try:
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=markup)
    except Exception:
        await query.message.reply_text(text, parse_mode="Markdown", reply_markup=markup)

    return ENT_SUB1

async def handle_ent_sub1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    sub1 = query.data.replace("ent1_", "")
    context.user_data["ent_sub1"] = sub1

    keyboard = [
        [InlineKeyboardButton("Математика", callback_data="ent2_Математика"),
         InlineKeyboardButton("Физика", callback_data="ent2_Физика")],
        [InlineKeyboardButton("Химия", callback_data="ent2_Химия"),
         InlineKeyboardButton("Биология", callback_data="ent2_Биология")],
        [InlineKeyboardButton("География", callback_data="ent2_География"),
         InlineKeyboardButton("Информатика", callback_data="ent2_Информатика")],
        [InlineKeyboardButton("Дүниежүзі тарихы", callback_data="ent2_Дүниежүзі тарихы")],
        [InlineKeyboardButton("Қазақ тілі", callback_data="ent2_Қазақ тілі"),
         InlineKeyboardButton("Қазақ әдебиеті", callback_data="ent2_Қазақ әдебиеті")],
        [InlineKeyboardButton("Орыс тілі", callback_data="ent2_Орыс тілі"),
         InlineKeyboardButton("Орыс әдебиеті", callback_data="ent2_Орыс әдебиеті")],
        [InlineKeyboardButton("Шет тілі", callback_data="ent2_Шет тілі")],
        [InlineKeyboardButton("Адам. Қоғам. Құқық", callback_data="ent2_Адам. Қоғам. Құқық")],
        [InlineKeyboardButton("🎨 Шығармашылық емтихан", callback_data="ent2_Шығармашылық емтихан")],
    ]
    await query.edit_message_text(
        f"✅ Бірінші пән: *{sub1}*\n\n"
        f"2️⃣ Енді *екінші пәніңді* таңда:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ENT_SUB2

async def handle_ent_sub2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    sub2 = query.data.replace("ent2_", "")
    sub1 = context.user_data["ent_sub1"]

    if sub1 == sub2:
        if sub1 == "Шығармашылық емтихан":
            sub2 = "Шығармашылық емтихан"
        else:
            keyboard = [[InlineKeyboardButton("🔄 Қайтадан таңда", callback_data="test_ent")]]
            await query.edit_message_text(
                "⚠️ Екі пән бірдей болмауы керек! Қайтадан таңда.",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return ENT_SUB2

    specialities = get_ent_specialities(sub1, sub2)
    specs_text = "\n".join([f"   • {s}" for s in specialities])

    keyboard = [
        [InlineKeyboardButton("📚 Мамандықтар каталогы", url=CATALOG_URL)],
        [InlineKeyboardButton("🔄 Басқа пән таңдау", callback_data="test_ent")],
        [InlineKeyboardButton("🧠 MBTI тестін тапсыру", callback_data="test_mbti")],
        [InlineKeyboardButton("🌐 Kasip Navigator", url=SITE_URL)],
    ]
    await query.edit_message_text(
        f"✅ *ЕНТ пәндеріңіз:*\n"
        f"📘 {sub1} + 📗 {sub2}\n\n"
        f"🎓 *Сізге сәйкес мамандықтар:*\n{specs_text}\n\n"
        f"🌐 Толығырақ ақпарат алу үшін Kasip Navigator сайтына кіріңіз!",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return CHOOSING_TEST

# ========================
# MBTI ТЕСТІ
# ========================
async def start_mbti(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["mbti_answers"] = []
    context.user_data["mbti_q"] = 0
    context.user_data["scores"] = {"E": 0, "I": 0, "S": 0, "N": 0, "T": 0, "F": 0, "J": 0, "P": 0}

    idx = 0
    q = MBTI_QUESTIONS[idx]
    total = len(MBTI_QUESTIONS)
    progress = "▓" * (idx + 1) + "░" * (total - idx - 1)
    keyboard = [
        [InlineKeyboardButton(f"A) {q['a'][0]}", callback_data="mbti_A")],
        [InlineKeyboardButton(f"B) {q['a'][1]}", callback_data="mbti_B")],
    ]
    text = f"🧠 *MBTI Тесті* [{idx+1}/{total}]\n{progress}\n\n{q['q']}"
    markup = InlineKeyboardMarkup(keyboard)

    try:
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=markup)
    except Exception:
        await query.message.reply_text(text, parse_mode="Markdown", reply_markup=markup)

    return MBTI_Q

async def ask_mbti_question(query, context):
    idx = context.user_data["mbti_q"]
    q = MBTI_QUESTIONS[idx]
    total = len(MBTI_QUESTIONS)
    progress = "▓" * (idx + 1) + "░" * (total - idx - 1)
    keyboard = [
        [InlineKeyboardButton(f"A) {q['a'][0]}", callback_data="mbti_A")],
        [InlineKeyboardButton(f"B) {q['a'][1]}", callback_data="mbti_B")],
    ]
    await query.edit_message_text(
        f"🧠 *MBTI Тесті* [{idx+1}/{total}]\n{progress}\n\n{q['q']}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_mbti_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    idx = context.user_data["mbti_q"]
    q = MBTI_QUESTIONS[idx]
    answer = query.data
    dim = q["dim"]
    scores = context.user_data["scores"]

    if answer == "mbti_A":
        scores[dim[0]] += 1
    else:
        scores[dim[1]] += 1

    idx += 1
    context.user_data["mbti_q"] = idx

    if idx < len(MBTI_QUESTIONS):
        await ask_mbti_question(query, context)
        return MBTI_Q
    else:
        await show_mbti_result(query, context)
        return CHOOSING_TEST

async def show_mbti_result(query, context):
    s = context.user_data["scores"]
    mbti_type = (
        ("E" if s["E"] >= s["I"] else "I") +
        ("S" if s["S"] >= s["N"] else "N") +
        ("T" if s["T"] >= s["F"] else "F") +
        ("J" if s["J"] >= s["P"] else "P")
    )
    result = MBTI_RESULTS.get(mbti_type, MBTI_RESULTS["INFP"])
    careers_text = "\n".join([f"   • {c}" for c in result["careers"]])

    keyboard = [
        [InlineKeyboardButton("📚 Мамандықтар каталогы", url=CATALOG_URL)],
        [InlineKeyboardButton("🎯 Профориентация тестін тапсыру", callback_data="test_holland")],
        [InlineKeyboardButton("🌐 Kasip Navigator", url=SITE_URL)],
        [InlineKeyboardButton("🔄 Қайтадан бастау", callback_data="restart")],
    ]
    await query.edit_message_text(
        f"✅ *MBTI нәтижесі:* `{mbti_type}`\n\n"
        f"🎭 *{result['name']}*\n\n"
        f"📝 {result['desc']}\n\n"
        f"💼 *Сізге сәйкес мамандықтар:*\n{careers_text}\n\n"
        f"🌐 Толығырақ мамандықтарды Kasip Navigator сайтынан таба аласыз!",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ========================
# ГОЛЛАНД ТЕСТІ
# ========================
async def start_holland(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["holland_scores"] = {"R": 0, "I": 0, "A": 0, "S": 0, "E": 0, "C": 0}
    context.user_data["holland_q"] = 0

    idx = 0
    q = HOLLAND_QUESTIONS[idx]
    total = len(HOLLAND_QUESTIONS)
    progress = "▓" * (idx + 1) + "░" * (total - idx - 1)
    keyboard = [
        [InlineKeyboardButton("✅ Иә, ұнайды", callback_data="holland_yes")],
        [InlineKeyboardButton("❌ Жоқ, ұнамайды", callback_data="holland_no")],
    ]
    text = f"🎯 *Профориентация Тесті* [{idx+1}/{total}]\n{progress}\n\n{q['q']}"
    markup = InlineKeyboardMarkup(keyboard)

    try:
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=markup)
    except Exception:
        await query.message.reply_text(text, parse_mode="Markdown", reply_markup=markup)

    return HOLLAND_Q

async def ask_holland_question(query, context):
    idx = context.user_data["holland_q"]
    q = HOLLAND_QUESTIONS[idx]
    total = len(HOLLAND_QUESTIONS)
    progress = "▓" * (idx + 1) + "░" * (total - idx - 1)
    keyboard = [
        [InlineKeyboardButton("✅ Иә, ұнайды", callback_data="holland_yes")],
        [InlineKeyboardButton("❌ Жоқ, ұнамайды", callback_data="holland_no")],
    ]
    await query.edit_message_text(
        f"🎯 *Профориентация Тесті* [{idx+1}/{total}]\n{progress}\n\n{q['q']}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_holland_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    idx = context.user_data["holland_q"]
    q = HOLLAND_QUESTIONS[idx]

    if query.data == "holland_yes":
        context.user_data["holland_scores"][q["type"]] += 1

    idx += 1
    context.user_data["holland_q"] = idx

    if idx < len(HOLLAND_QUESTIONS):
        await ask_holland_question(query, context)
        return HOLLAND_Q
    else:
        await show_holland_result(query, context)
        return CHOOSING_TEST

async def show_holland_result(query, context):
    scores = context.user_data["holland_scores"]
    sorted_types = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top1 = sorted_types[0][0]
    top2 = sorted_types[1][0]

    r1 = HOLLAND_RESULTS[top1]
    r2 = HOLLAND_RESULTS[top2]

    careers1 = "\n".join([f"   • {c}" for c in r1["careers"]])
    careers2 = "\n".join([f"   • {c}" for c in r2["careers"]])

    keyboard = [
        [InlineKeyboardButton("📚 Мамандықтар каталогы", url=CATALOG_URL)],
        [InlineKeyboardButton("🧠 MBTI тестін тапсыру", callback_data="test_mbti")],
        [InlineKeyboardButton("🌐 Kasip Navigator", url=SITE_URL)],
        [InlineKeyboardButton("🔄 Қайтадан бастау", callback_data="restart")],
    ]
    await query.edit_message_text(
        f"✅ *Профориентация нәтижесі:*\n\n"
        f"🥇 Негізгі бағыт: *{r1['name']}*\n"
        f"📝 {r1['desc']}\n"
        f"💼 Ұсынылатын мамандықтар:\n{careers1}\n\n"
        f"🥈 Қосымша бағыт: *{r2['name']}*\n"
        f"📝 {r2['desc']}\n"
        f"💼 Ұсынылатын мамандықтар:\n{careers2}\n\n"
        f"🌐 Толығырақ ақпарат алу үшін Kasip Navigator сайтына кіріңіз!",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ========================
# RESTART
# ========================
async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.clear()
    keyboard = [
        [InlineKeyboardButton("🧠 MBTI Тесті", callback_data="test_mbti")],
        [InlineKeyboardButton("🎯 Профориентация Тесті", callback_data="test_holland")],
        [InlineKeyboardButton("📚 ЕНТ пәндері бойынша мамандық", callback_data="test_ent")],
        [InlineKeyboardButton("🌐 Kasip Navigator Сайты", url=SITE_URL)],
    ]
    await query.edit_message_text(
        "👋 Қайсысын таңдайсың?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return CHOOSING_TEST

# ========================
# MAIN
# ========================
def main():
    if not BOT_TOKEN:
        print("❌ Қате: Токен табылмады! .env файлын тексеріңіз.")
        return

    app = Application.builder().token(BOT_TOKEN).build()

    # ConversationHandler — боттың қай кезеңде тұрғанын бақылайды
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING_TEST: [
                CallbackQueryHandler(start_mbti, pattern="^test_mbti$"),
                CallbackQueryHandler(start_holland, pattern="^test_holland$"),
                CallbackQueryHandler(start_ent, pattern="^test_ent$"),
                CallbackQueryHandler(restart, pattern="^restart$"),
            ],
            MBTI_Q: [
                CallbackQueryHandler(handle_mbti_answer, pattern="^mbti_"),
            ],
            HOLLAND_Q: [
                CallbackQueryHandler(handle_holland_answer, pattern="^holland_"),
            ],
            ENT_SUB1: [
                CallbackQueryHandler(handle_ent_sub1, pattern="^ent1_"),
            ],
            ENT_SUB2: [
                CallbackQueryHandler(handle_ent_sub2, pattern="^ent2_"),
                CallbackQueryHandler(start_ent, pattern="^test_ent$"),
            ],
        },
        fallbacks=[
            CommandHandler("start", start),
            CallbackQueryHandler(restart, pattern="^restart$"),
        ],
        allow_reentry=True,
    )

    app.add_handler(conv_handler)

    print("✅ Kasip Navigator боты іске қосылды!")
    app.run_polling()

if __name__ == "__main__":
    main()
