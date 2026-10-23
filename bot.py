
import os
import json
import logging
from pathlib import Path

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ==============================
# JAM_BIKE TELEGRAM SHOP
# ==============================

TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

DATA_FILE = Path("shop_data.json")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TEXTS = {
    "tg": {
        "welcome": "🛴 Хуш омадед ба JAM_BIKE!\nМағозаи электроскутерҳо ⚡",
        "catalog": "🛴 Каталоги электроскутерҳо",
        "cart": "🛒 Сабади ман",
        "orders": "📦 Фармоишҳои ман",
        "language": "🌐 Забон",
        "contact": "📞 Тамос бо мағоза",
        "empty": "Сабади шумо холӣ аст.",
        "added": "✅ Ба сабад илова шуд!",
        "checkout": "📦 Фармоиш додан",
        "name": "Ному насабатонро нависед:",
        "phone": "Рақами телефони худро фиристед:",
        "address": "Суроғаи расониданро нависед:",
        "success": "✅ Фармоиши шумо қабул шуд!",
        "cancel": "❌ Фармоиш бекор шуд.",
        "admin": "👑 Панели администратор",
        "no_products": "Ҳоло маҳсулот илова нашудааст.",
        "choose_lang": "Забонро интихоб кунед:",
        "no_orders": "Шумо ҳоло фармоиш надоред.",
    },
    "ru": {
        "welcome": "🛴 Добро пожаловать в JAM_BIKE!\nМагазин электроскутеров ⚡",
        "catalog": "🛴 Каталог электроскутеров",
        "cart": "🛒 Моя корзина",
        "orders": "📦 Мои заказы",
        "language": "🌐 Язык",
        "contact": "📞 Связаться с магазином",
        "empty": "Ваша корзина пуста.",
        "added": "✅ Добавлено в корзину!",
        "checkout": "📦 Оформить заказ",
        "name": "Введите ваше имя и фамилию:",
        "phone": "Отправьте свой номер телефона:",
        "address": "Введите адрес доставки:",
        "success": "✅ Ваш заказ принят!",
        "cancel": "❌ Заказ отменён.",
        "admin": "👑 Панель администратора",
        "no_products": "Товары пока не добавлены.",
        "choose_lang": "Выберите язык:",
        "no_orders": "У вас пока нет заказов.",
    },
    "en": {
        "welcome": "🛴 Welcome to JAM_BIKE!\nElectric scooter shop ⚡",
        "catalog": "🛴 Electric scooter catalog",
        "cart": "🛒 My cart",
        "orders": "📦 My orders",
        "language": "🌐 Language",
        "contact": "📞 Contact the shop",
        "empty": "Your cart is empty.",
        "added": "✅ Added to cart!",
        "checkout": "📦 Place an order",
        "name": "Enter your full name:",
        "phone": "Send your phone number:",
        "address": "Enter your delivery address:",
        "success": "✅ Your order has been received!",
        "cancel": "❌ Order cancelled.",
        "admin": "👑 Admin panel",
        "no_products": "No products have been added yet.",
        "choose_lang": "Choose a language:",
        "no_orders": "You have no orders yet.",
    },
}

# Намунаи маҳсулот. Баъдтар метавонед тағйир диҳед.
DEFAULT_PRODUCTS = [
    {
        "id": 1,
        "name": "JAM Scooter S1",
        "price": 3500,
        "currency": "TJS",
        "description": "Электроскутер барои шаҳр",
        "photo": "",
        "stock": 5,
    },
    {
        "id": 2,
        "name": "JAM Scooter Pro",
        "price": 5500,
        "currency": "TJS",
        "description": "Модели пуриқтидор",
        "photo": "",
        "stock": 3,
    },
]


def load_data():
    if DATA_FILE.exists():
        try:
            with DATA_FILE.open("r", encoding="utf-8") as f:
                data = json.load(f)
                data.setdefault("products", DEFAULT_PRODUCTS.copy())
                data.setdefault("orders", [])
                data.setdefault("carts", {})
                data.setdefault("users", {})
                return data
        except (json.JSONDecodeError, OSError):
            logger.exception("Хатои хондани маълумот")
    return {
        "products": DEFAULT_PRODUCTS.copy(),
        "orders": [],
        "carts": {},
        "users": {},
    }


data = load_data()


def save_data():
    temp = DATA_FILE.with_suffix(".tmp")
    with temp.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    temp.replace(DATA_FILE)


def get_lang(user_id):
    return data["users"].get(str(user_id), {}).get("lang", "tg")


def set_lang(user_id, lang):
    uid = str(user_id)
    data["users"].setdefault(uid, {})["lang"] = lang
    save_data()


def t(user_id, key):
    return TEXTS[get_lang(user_id)][key]


def main_keyboard(user_id):
    return ReplyKeyboardMarkup(
        [
            [t(user_id, "catalog"), t(user_id, "cart")],
            [t(user_id, "orders"), t(user_id, "language")],
            [t(user_id, "contact")],
        ],
        resize_keyboard=True,
    )


def cart_for(user_id):
    return data["carts"].setdefault(str(user_id), {})


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data["users"].setdefault(str(user.id), {"lang": "tg"})
    save_data()

    await update.message.reply_text(
        t(user.id, "welcome"),
        reply_markup=main_keyboard(user.id),
    )


async def language_menu(update: Update, context: Context
