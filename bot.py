import os
import json
import re
import telebot
from telebot import types

# ==========================================
# TOKEN
# ==========================================

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN ёфт нашуд!")

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")


# ==========================================
# КАНАЛ
# ==========================================

CHANNEL_USERNAME = "khamai_bozikho"

CHANNEL = f"@{CHANNEL_USERNAME}"

CHANNEL_LINK = f"https://t.me/{CHANNEL_USERNAME}"

# ==========================================
# DATABASE
# ==========================================

DATABASE_FILE = "games.json"


def load_games():
    try:
        with open(
            DATABASE_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

            if not isinstance(data, list):
                return []

            return data

    except FileNotFoundError:
        return []

    except json.JSONDecodeError:
        print("games.json хатои JSON дорад.")
        return []


def save_games(games):
    with open(
        DATABASE_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            games,
            file,
            ensure_ascii=False,
            indent=2
        )


# ==========================================
# БОЗИҲО
# ==========================================

games = load_games()


# ==========================================
# САНҶИШИ ПОДПИСКА
# ==========================================

def is_subscribed(user_id):

    try:

        member = bot.get_chat_member(
            CHANNEL,
            user_id
        )

        return member.status in (
            "member",
            "administrator",
            "creator"
        )

    except Exception as error:

        print(
            "Subscription check error:",
            error
        )

        return False


# ==========================================
# ПОДПИСКА КЛАВИАТУРА
# ==========================================

def subscription_keyboard():

    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(
        types.InlineKeyboardButton(
            text="📢 Ба канал даромадан",
            url=CHANNEL_LINK
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            text="✅ Ман подписка кардам",
            callback_data="check_subscription"
        )
    )

    return keyboard


# ==========================================
# ТАЛАБИ ПОДПИСКА
# ==========================================

def require_subscription(message):

    if is_subscribed(
        message.from_user.id
    ):
        return True

    bot.send_message(
        message.chat.id,

        "🔒 <b>Аввал подписка кунед!</b>\n\n"
        "Барои истифодаи Game Bot аввал ба "
        "канали мо подписка кунед.\n\n"
        "1️⃣ Ба канал дароед.\n"
        "2️⃣ Подписка кунед.\n"
        "3️⃣ Баъд тугмаи "
        "«✅ Ман подписка кардам»-ро пахш кунед.",

        reply_markup=subscription_keyboard()
    )

    return False


# ==========================================
# МЕНЮ
# ==========================================

def main_menu():

    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    keyboard.row(
        "🎮 Ҳамаи бозиҳо",
        "🔎 Ҷустуҷӯи бозӣ"
    )

    return keyboard


# ==========================================
# /START
# ==========================================

@bot.message_handler(commands=["start"])
def start(message):

    if not require_subscription(message):
        return

    bot.send_message(
        message.chat.id,

        "🎮 <b>Хуш омадед!</b>\n\n"
        "Подписка тасдиқ шуд. ✅\n\n"
        "Акнун метавонед бозиҳоро ҷустуҷӯ кунед.",

        reply_markup=main_menu()
    )


# ==========================================
# CHECK SUBSCRIPTION
# ==========================================

@bot.callback_query_handler(
    func=lambda call:
    call.data == "check_subscription"
)
def check_subscription(call):

    if is_subscribed(
        call.from_user.id
    ):

        bot.answer_callback_query(
            call.id,
            "✅ Подписка тасдиқ шуд!"
        )

        bot.send_message(
            call.message.chat.id,

            "🎉 <b>Подписка тасдиқ шуд!</b>\n\n"
            "Акнун ҳамаи бозиҳо дастрасанд.",

            reply_markup=main_menu()
        )

    else:

        bot.answer_callback_query(
            call.id,
            "❌ Аввал ба канал подписка кунед!",
            show_alert=True
        )


# ==========================================
# ҲАМАИ БОЗИҲО
# ==========================================

@bot.message_handler(
    func=lambda message:
    message.text == "🎮 Ҳамаи бозиҳо"
)
def all_games(message):

    if not require_subscription(message):
        return

    games = load_games()

    if not games:

        bot.send_message(
            message.chat.id,
            "📭 Ҳоло ягон бозӣ илова нашудааст."
        )

        return

    text = "🎮 <b>Рӯйхати бозиҳо:</b>\n\n"

    for number, game in enumerate(
        games,
        1
    ):

        name = game["name"]
        link = game["link"]

        text += (
            f"<b>{number}.</b> "
            f"<a href=\"{link}\">{name}</a>\n"
        )

    bot.send_message(
        message.chat.id,
        text,
        disable_web_page_preview=True
    )


# ==========================================
# ҶУСТУҶӮ
# ==========================================

@bot.message_handler(
    func=lambda message:
    message.text == "🔎 Ҷустуҷӯи бозӣ"
)
def search_help(message):

    if not require_subscription(message):
        return

    bot.send_message(
        message.chat.id,

        "🔎 <b>Ҷустуҷӯи бозӣ</b>\n\n"
        "Номи бозӣ ё рақами онро нависед.\n\n"
        "Мисол:\n"
        "Minecraft\n"
        "5"
    )


# ==========================================
# ҶУСТУҶӮ БО НОМ Ё РАҚАМ
# ==========================================

@bot.message_handler(func=lambda message: True)
def find_game(message):

    if not require_subscription(message):
        return

    query = message.text.strip().lower()

    games = load_games()

    # --------------------------------------
    # РАҚАМ
    # --------------------------------------

    if query.isdigit():

        number = int(query)

        if 1 <= number <= len(games):

            game = games[number - 1]

            name = game["name"]
            link = game["link"]

            bot.send_message(
                message.chat.id,

                f"🎮 <b>{number}. {name}</b>\n\n"
                f"🔗 <a href=\"{link}\">"
                f"Кушодани бозӣ"
                f"</a>"
            )

        else:

            bot.send_message(
                message.chat.id,
                "❌ Ин рақами бозӣ вуҷуд надорад."
            )

        return

    # --------------------------------------
    # НОМ
    # --------------------------------------

    found = []

    for number, game in enumerate(
        games,
        1
    ):

        name = game["name"]
        link = game["link"]

        if query in name.lower():

            found.append(
                (
                    number,
                    name,
                    link
                )
            )

    if found:

        text = "🔎 <b>Натиҷа:</b>\n\n"

        for number, name, link in found:

            text += (
                f"<b>{number}.</b> "
                f"<a href=\"{link}\">{name}</a>\n"
            )

        bot.send_message(
            message.chat.id,
            text,
            disable_web_page_preview=True
        )

    else:

        bot.send_message(
            message.chat.id,
            "❌ Бозӣ ёфт нашуд."
        )


# ==========================================
# ГИРИФТАНИ БОЗӢ АЗ КАНАЛ
# ==========================================

def add_game_from_channel(
    message
):

    global games

    # Танҳо аз канали муайян
    if message.chat.username:

        if (
            message.chat.username.lower()
            != CHANNEL_USERNAME.lower()
        ):
            return

    else:
        return

    text = message.text or message.caption or ""

    if not text:
        return

    # --------------------------------------
    # ҶУСТУҶӮИ LINK
    # --------------------------------------

    url_pattern = r"https?://\S+"

    links = re.findall(
        url_pattern,
        text
    )

    if not links:
        print(
            "Дар пости канал link ёфт нашуд."
        )
        return

    link = links[0].rstrip(
        ".,!?)]}>"
    )

    # --------------------------------------
    # ГИРИФТАНИ НОМ
    # --------------------------------------

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    name = None

    for line in lines:

        if (
            line.startswith("http://")
            or line.startswith("https://")
        ):
            continue

        clean = re.sub(
            r"^[🎮🕹️📱🔥⭐️\s]+",
            "",
            line
        ).strip()

        clean = re.sub(
            r"^(game|бозӣ)\s*[:\-]?\s*",
            "",
            clean,
            flags=re.IGNORECASE
        )

        if clean:
            name = clean
            break

    if not name:
        print(
            "Номи бозӣ ёфт нашуд."
        )
        return

    # --------------------------------------
    # ДУБОРА НАБОШАД
    # --------------------------------------

    for game in games:

        if (
            game["name"].lower()
            == name.lower()
        ):
            print(
                f"Бозӣ аллакай вуҷуд дорад: {name}"
            )
            return

        if game["link"] == link:
            print(
                f"Link аллакай вуҷуд дорад: {link}"
            )
            return

    # --------------------------------------
    # ИЛОВА
    # --------------------------------------

    games.append(
        {
            "name": name,
            "link": link
        }
    )

    save_games(games)

    print(
        f"🎮 Бозии нав илова шуд: {name}"
    )


# ==========================================
# CHANNEL POSTS
# ==========================================

@bot.channel_post_handler(
    content_types=[
        "text",
        "photo"
    ]
)
def channel_post(message):

    print(
        "📢 Channel post received"
    )

    add_game_from_channel(
        message
    )


# ==========================================
# START BOT
# ==========================================

print(
    "🤖 Telegram Game Bot started!"
)

bot.infinity_polling(
    timeout=60,
    long_polling_timeout=60
)
