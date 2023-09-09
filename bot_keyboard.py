from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def start_kb():
    kb1 = KeyboardButton('/add')
    kb2 = KeyboardButton('/view')
    kb3 = KeyboardButton('/view_detail')
    kb4 = KeyboardButton("/delete")
    kb5 = KeyboardButton("/update")
    panel = ReplyKeyboardMarkup(resize_keyboard=True)
    panel.add(kb1).insert(kb2).add(kb3).insert(kb4).add(kb5)
    return panel
