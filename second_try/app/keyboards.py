from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from second_try.app.database.requests import get_all, get_types, get_subgroups

# async def keyboard_all():
#     all_categories = await get_all()
#     keyboard = InlineKeyboardBuilder()
#     for category in all_categories:
#         keyboard.add(InlineKeyboardButton(text=category.title, callback_data=f"all_{category.id}"))
#     keyboard.add(InlineKeyboardButton(text='На главную', callback_data='to_main'))
#     return keyboard.adjust(2).as_markup()
#
# async def keyboard_types():
#     all_categories = await get_types()
#     keyboard = InlineKeyboardBuilder()
#     for category in all_categories:
#         keyboard.add(InlineKeyboardButton(text=category.title, callback_data=f"type_{category.id}"))
#     keyboard.add(InlineKeyboardButton(text='На главную', callback_data='to_main'))
#     return keyboard.adjust(2).as_markup()
#
# async def keyboard_subgroups():
#     all_categories = await get_subgroups()
#     keyboard = InlineKeyboardBuilder()
#     for category in all_categories:
#         keyboard.add(InlineKeyboardButton(text=category.title, callback_data=f"category_{category.id}"))
#     keyboard.add(InlineKeyboardButton(text='На главную', callback_data='to_main'))
#     return keyboard.adjust(2).as_markup()

# main = ReplyKeyboardMarkup(keyboard=[
#     [KeyboardButton(text='Создать заказ')],
#     [KeyboardButton(text='Комментарий к заказу')]
# ], resize_keyboard=True, input_field_placeholder="Выберите опцию")
