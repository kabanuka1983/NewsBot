from typing import Union

from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.types import CallbackQuery, Message

from data.loader import dp
from data.urls import URL
from keyboard.default.menu import menu
from keyboard.inline.choice_buttons import start_keyboard, news_callback, categories_keyboard, categories_keyboard2
from utils import database

db = database.DBCommands()


@dp.message_handler(Command('start', prefixes='/'))
async def show_menu(message: types.Message):
    await db.add_new_subscriber(message.from_user)
    await message.answer(text='Я бот который поможет следить за интересующими тебя новостями. '
                              'Ты можешь подключить лишь интересующие тебя разделы и регулярно получать обновления.\n\n'
                              'Нажми /menu для того, чтобы подписаться на уведомления по выбранным разделам',
                         reply_markup=menu)


@dp.message_handler(Command(['menu', 'еню'], prefixes=['/', 'М']))
async def menu_command(message: types.Message):
    await start_choice(message)


async def start_choice(message: Union[CallbackQuery, Message], **kwargs):
    markup = await start_keyboard()
    if isinstance(message, Message):
        await message.answer(text="Меню управления подписками", reply_markup=markup)
    elif isinstance(message, CallbackQuery):
        await message.message.edit_text(text="Меню управления подписками", reply_markup=markup)


async def category_choice(callback: CallbackQuery, section_name, **kwargs):
    subscriber = await db.get_subscriber(callback.from_user.id)
    markup = await categories_keyboard(section_name, subscriber)
    if section_name == "categories":
        text = "Выберите категорию \n\nУсловные обозначения: \n✅ - Вы подписаны на категорию \n" \
               "❌ - Вы не подписаны на категорию"
        await callback.message.edit_text(text=text, reply_markup=markup, disable_web_page_preview=True)
    elif section_name == "my_categories":
        category_string = ""
        for category, status in subscriber.get_categories_dict().items():
            if status:
                category_string += f"<a href='{URL.get(category)}'>{category}</a>\n"
        text = f"Вы подписаны на категории: \n\n{category_string}"
        await callback.message.edit_text(text=text, reply_markup=markup, disable_web_page_preview=True)


async def subscribe(callback: CallbackQuery, section_name, category):
    await db.update_subscriber(callback.from_user.id, category)
    subscriber = await db.get_subscriber(callback.from_user.id)
    markup = await categories_keyboard2(section_name, subscriber)
    text = "Выберите категорию \n\nУсловные обозначения: \n✅ - Вы подписаны на категорию \n" \
           "❌ - Вы не подписаны на категорию"
    await callback.message.edit_text(text=text, reply_markup=markup)


@dp.callback_query_handler(news_callback.filter())
async def navigate(call: CallbackQuery, callback_data: dict):
    current_level = callback_data.get("level")
    section_name = callback_data.get("section_name")
    category = callback_data.get("category")

    levels = {
        "0": start_choice,
        "1": category_choice,
        "2": subscribe
    }

    current_level_function = levels[current_level]

    await current_level_function(
        call,
        section_name=section_name,
        category=category
    )
