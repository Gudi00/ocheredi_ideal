import os
from aiogram import Router, types, Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.config import load_config
# from app.database.requests import add_temporary_event_user

from app.database.requests import update_user_want, get_activity_name, get_list, add_user_to_db

router = Router()
config = load_config()

class Form(StatesGroup):
    waiting_for_name = State()
    waiting_for_surname = State()

from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

router = Router()

main = InlineKeyboardMarkup(inline_keyboard=[
        # [InlineKeyboardButton(text="Временные мероприятия", callback_data="temp_events")],
        [InlineKeyboardButton(text="Занятия по подгруппам", callback_data="subgroups")],
        [InlineKeyboardButton(text="Совместные пары", callback_data="joint_pairs")]
    ])

@router.message(Command("start"))
async def start_command(message: Message):
    await message.answer("Это бот для очередей)\nЧтобы занять очередь на любой предмет нужно выбрать один из пунктов меню, под следующем сообщением. И далее выбрать нужный предмет и подгруппу.\n\nЕсли нажать на кнопку 'ДА', значит вы планируете отвечать на слудующей паре по этому предмету, 'НЕТ' - не планируете ответчать.\n\nЕсли будут вопросы, пишите @misha_iosko")
    await message.answer("Выберите тип мероприятия:", reply_markup=main)
    admin_chat_id = config['ADMIN_CHAT_ID']
    await message.bot.send_message(admin_chat_id,
                                   f"Новый пользователь @{message.from_user.username} ({message.from_user.id}) начал использовать бота.")

@router.callback_query(F.data == "to_main")
async def to_main(callback: CallbackQuery):
    await callback.answer("Вы вернулись в стартовое меню")
    await callback.message.answer("Выберите тип мероприятия:", reply_markup=main)

@router.callback_query(F.data == "temp_events")
async def temporary_events(callback: CallbackQuery, state: FSMContext):
    await callback.answer('X_X')
    await callback.message.answer("Введите ваше имя:")
    await state.set_state(Form.waiting_for_name)

@router.message(Form.waiting_for_name)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите вашу фамилию:")
    await state.set_state(Form.waiting_for_surname)

@router.message(Form.waiting_for_surname)
async def get_surname(message: Message, state: FSMContext):
    user_data = await state.get_data()
    name = user_data['name']
    surname = message.text
    username = message.from_user.username

    # await add_temporary_event_user(username, name, surname)
    await message.answer(f"Вы записаны на временное мероприятие как {name} {surname}.")
    await state.clear()

@router.callback_query(lambda c: c.data == "subgroups")
async def subgroups_selected(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="СПО (1 группа)", callback_data="activity_subgroup_1")],
        [InlineKeyboardButton(text="СПО (2 группа)", callback_data="activity_subgroup_2")],
        [InlineKeyboardButton(text="ОАиП (1 группа)", callback_data="activity_subgroup_3")],
        [InlineKeyboardButton(text="ОАиП (2 группа)", callback_data="activity_subgroup_4")],
        [InlineKeyboardButton(text="Физика (1 группа)", callback_data="activity_subgroup_5")],
        [InlineKeyboardButton(text="Физика (2 группа)", callback_data="activity_subgroup_6")],
        [InlineKeyboardButton(text="На главную", callback_data="to_main")]
    ])
    await callback.answer('X_X')
    await callback.message.answer("Выберите занятие по подгруппам:", reply_markup=keyboard)

@router.callback_query(lambda c: c.data == "joint_pairs")
async def joint_pairs_selected(callback: CallbackQuery):
    await callback.answer('X_X')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="СПО", callback_data="activity_joint_1")],
        [InlineKeyboardButton(text="ОАиП", callback_data="activity_joint_2")],
        [InlineKeyboardButton(text="На главную", callback_data="to_main")]
    ])
    await callback.message.answer("Выберите совместное занятие:", reply_markup=keyboard)

@router.callback_query(lambda c: c.data.startswith("activity_"))
async def activity_selected(callback: CallbackQuery):
    await callback.answer('X_X')
    parts = callback.data.split("_")
    activity_type = parts[1]  # subgroup или joint
    activity_id = int(parts[2])
    activity_name = await get_activity_name(activity_type, activity_id)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Показать список", callback_data=f"show_list_{activity_type}_{activity_id}")],
        [InlineKeyboardButton(text="ДА", callback_data=f"want_{activity_type}_{activity_id}_1")],
        [InlineKeyboardButton(text="НЕТ", callback_data=f"want_{activity_type}_{activity_id}_0")],
        [InlineKeyboardButton(text="На главную", callback_data="to_main")]
    ])
    await callback.message.answer(f"Вы хотите отвечать на следующей паре по {activity_name}", reply_markup=keyboard)




@router.callback_query(lambda c: c.data.startswith("show_list_"))
async def show_list_handler(callback: CallbackQuery):
    await callback.answer('(👉ﾟヮﾟ)👉')
    parts = callback.data.split("_")
    activity_type = parts[2]
    activity_id = int(parts[3])
    new = activity_id
    if activity_type == 'joint':
        new += 6
    list_result = await get_list(new)
    await callback.message.answer(f"Список для {await get_activity_name(activity_type, activity_id)}:\n{list_result}")

@router.callback_query(lambda c: c.data.startswith("want_"))
async def save_preference(callback: CallbackQuery):
    await callback.answer('X_X')
    parts = callback.data.split("_")
    activity_type = parts[1]
    activity_id = int(parts[2])
    new = activity_id
    if activity_type == 'joint':
        new += 6

    want = int(parts[3])
    await update_user_want(callback.from_user.id, callback.from_user.username, new, want)
    activity_name = await get_activity_name(activity_type, activity_id)
    await callback.message.answer(f"Ваш выбор для '{activity_name}' сохранен: {'ДА' if want else 'НЕТ'}")

async def get_activity_name(activity_type: str, activity_id: int) -> str:
    subgroups = {1: "СПО (1 группа)", 2: "СПО (2 группа)", 3: "ОАиП (1 группа)",
                 4: "ОАиП (2 группа)", 5: "Физика (1 группа)", 6: "Физика (2 группа)"}
    joints = {1: "СПО", 2: "ОАиП"}
    return subgroups.get(activity_id, "Неизвестно") if activity_type == "subgroup" else joints.get(activity_id, "Неизвестно")




def register_main_handlers(dp: Dispatcher):
    dp.include_router(router)