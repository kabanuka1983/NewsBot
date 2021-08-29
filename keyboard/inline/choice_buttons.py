from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

news_callback = CallbackData("news", "level", "section_name", "category")


def make_callback_data(level, section_name="0", category="0"):
    return news_callback.new(level=level, section_name=section_name, category=category)


async def start_keyboard():
    CURRENT_LEVEL = 0

    markup = InlineKeyboardMarkup(row_width=1)
    markup.row(InlineKeyboardButton(text="Выбор разделов",
                                    callback_data=make_callback_data(level=CURRENT_LEVEL+1,
                                                                     section_name="categories")))
    markup.row(InlineKeyboardButton(text="Мои подписки",
                                    callback_data=make_callback_data(level=CURRENT_LEVEL+1,
                                                                     section_name="my_categories")))

    return markup


async def categories_keyboard(section_name, subscriber):
    CURRENT_LEVEL = 1

    markup = InlineKeyboardMarkup(row_width=1)
    categories = subscriber.get_categories_dict()
    if section_name == "my_categories":
        markup.row(InlineKeyboardButton(text="⬅Назад",
                                        callback_data=make_callback_data(level=CURRENT_LEVEL-1)))
    elif section_name == "categories":
        for category, status in categories.items():
            if status:
                text_button = f"✅   {category}"
            else:
                text_button = f"❌   {category}"
            callback_data = make_callback_data(level=CURRENT_LEVEL+1,
                                               section_name=section_name,
                                               category=category)
            markup.insert(InlineKeyboardButton(text=text_button,
                                               callback_data=callback_data))
        markup.row(InlineKeyboardButton(text="⬅Назад",
                                        callback_data=make_callback_data(level=CURRENT_LEVEL-1)))
    return markup


async def categories_keyboard2(section_name, subscriber):
    CURRENT_LEVEL = 2

    markup = InlineKeyboardMarkup(row_width=1)
    categories = subscriber.get_categories_dict()
    if section_name == "my_categories":
        markup.row(InlineKeyboardButton(text="⬅Назад",
                                        callback_data=make_callback_data(level=CURRENT_LEVEL-2)))
    elif section_name == "categories":
        for category, status in categories.items():
            if status:
                text_button = f"✅   {category}"
            else:
                text_button = f"❌   {category}"
            callback_data = make_callback_data(level=CURRENT_LEVEL,
                                               section_name=section_name,
                                               category=category)
            markup.insert(InlineKeyboardButton(text=text_button,
                                               callback_data=callback_data))
        markup.row(InlineKeyboardButton(text="⬅Назад",
                                        callback_data=make_callback_data(level=CURRENT_LEVEL-2)))
    return markup
