import os
from aiogram import Router, types, Bot, Dispatcher
from aiogram.types import Message, InputFile, CallbackQuery
from aiogram.filters import Command



from app.config import load_config


from app.database.requests import dump_discipline

router = Router()
config = load_config()
bot = Bot(token=config['BOT_TOKEN'])
ADMIN_CHAT_ID = config['ADMIN_CHAT_ID']

# @router.message(Command("add_discipline"))
# async def add_discipline_command(message: Message):
#     if str(message.from_user.id) != ADMIN_CHAT_ID:  # Замени на свой ID админа
#         await message.answer("Эта команда доступна только админу!")
#         return
#     await message.answer("Введите название новой дисциплины:")

# @router.message(lambda message: message.text and message.from_user.id == int(ADMIN_CHAT_ID))
# async def discipline_title_received(message: Message):
#     title = message.text
#     await add_new_discipline(title)
#     await message.answer(f"Дисциплина '{title}' добавлена!")
@router.message(Command("dump"))
async def dump_command(message: Message):
    # Проверяем, что пользователь — админ
    if str(message.from_user.id) != config["ADMIN_CHAT_ID"]:
        await message.answer("Эта команда доступна только администратору!")
        return

    # Парсим аргументы из команды
    try:
        args = message.text.split()[1:]  # Пропускаем "/dump"
        if len(args) != 2:
            raise ValueError
        discipline_id = int(args[0])
        last_user = int(args[1])
    except (IndexError, ValueError):
        await message.answer("Использование: /dump <discipline_id> <last_user>\nПример: /dump 4 3")
        return

    # Выполняем обновление
    await dump_discipline(discipline_id, last_user)
    await message.answer(f"Дисциплина {discipline_id} обновлена: last_user = {last_user}, все want сброшены на 0.")
async def add_new_discipline(title: str):
    # Логика добавления дисциплины в базу данных
    pass  # Реализуй по своей структуре базы данных

#сделать очистку временных мероприятий
# добавлять новые дисциплины через админку список, а дальше через рандом всех



def register_admin_handlers(dp: Dispatcher):
    dp.include_router(router)