from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu():
    """Главное меню"""
    keyboard = [
        [KeyboardButton("🎰 Слоты"), KeyboardButton("🎲 Кости")],
        [KeyboardButton("🎡 Рулетка")],
        [KeyboardButton("💰 Баланс"), KeyboardButton("📊 Статистика")],
        [KeyboardButton("🏆 Топ игроков"), KeyboardButton("🎁 Ежедневный бонус")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_bet_keyboard():
    """Клавиатура для выбора ставки"""
    keyboard = [
        [
            InlineKeyboardButton("10 💰", callback_data="bet_10"),
            InlineKeyboardButton("50 💰", callback_data="bet_50"),
            InlineKeyboardButton("100 💰", callback_data="bet_100")
        ],
        [
            InlineKeyboardButton("250 💰", callback_data="bet_250"),
            InlineKeyboardButton("500 💰", callback_data="bet_500"),
            InlineKeyboardButton("1000 💰", callback_data="bet_1000")
        ],
        [InlineKeyboardButton("❌ Отмена", callback_data="cancel")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_dice_choice_keyboard():
    """Выбор для игры в кости"""
    keyboard = [
        [
            InlineKeyboardButton("⬆️ Больше (4-6)", callback_data="dice_high"),
            InlineKeyboardButton("⬇️ Меньше (1-3)", callback_data="dice_low")
        ],
        [InlineKeyboardButton("❌ Отмена", callback_data="cancel")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_roulette_keyboard():
    """Выбор для рулетки"""
    keyboard = [
        [
            InlineKeyboardButton("🔴 Красное", callback_data="roul_red"),
            InlineKeyboardButton("⚫ Черное", callback_data="roul_black")
        ],
        [
            InlineKeyboardButton("2️⃣ Четное", callback_data="roul_even"),
            InlineKeyboardButton("1️⃣ Нечетное", callback_data="roul_odd")
        ],
        [InlineKeyboardButton("🎯 Выбрать число (0-36)", callback_data="roul_number")],
        [InlineKeyboardButton("❌ Отмена", callback_data="cancel")]
    ]
    return InlineKeyboardMarkup(keyboard)