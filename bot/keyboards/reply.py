from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🚗 Buyurtma berish")],
            [KeyboardButton(text="📞 Aloqa")],
            [KeyboardButton(text="ℹ️ Yordam")]
        ],
        resize_keyboard=True
    )

def get_cancel_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❌ Bekor qilish")]
        ],
        resize_keyboard=True
    )