import random

from sqlalchemy import select, update
from app.database.models import async_session, User, TemporaryEvent

from second_try.app.database.models import Discipline, UserDiscipline


async def add_temporary_event_user(username: str, first_name: str, last_name: str):
    async with async_session() as session:
        new_user = TemporaryEvent(username=username, first_name=first_name, last_name=last_name)
        session.add(new_user)
        await session.commit()
#проверить есть ли с таким же username



async def get_activity_name(activity_type: str, activity_id: str) -> str:
    if activity_type == "subgroup":
        subgroups = {
            "1": "СПО (1 группа)",
            "2": "СПО (2 группа)",
            "3": "ОАиП (1 группа)",
            "4": "ОАиП (2 группа)",
            "5": "Физика (1 группа)",
            "6": "Физика (2 группа)"
        }
        return subgroups.get(activity_id, "Неизвестно")
    elif activity_type == "joint":
        joints = {
            "1": "СПО",
            "2": "ОАиП"
        }
        return joints.get(activity_id, "Неизвестно")
    return "Неизвестно"




# requests.py
async def add_user_to_db(user_id: int, username: str, first_name: str, last_name: str):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.user_id == user_id))
        user = result.scalars().first()
        if not user:
            new_user = User(user_id=user_id, username=username, first_name=first_name, last_name=last_name)
            session.add(new_user)
        else:
            user.first_name = first_name
            user.last_name = last_name
        await session.commit()


# requests.py
async def add_new_discipline(title: str, discipline_type: str):
    async with async_session() as session:
        result = await session.execute(select(Discipline).where(Discipline.title == title))
        discipline = result.scalars().first()
        if not discipline:
            new_discipline = Discipline(title=title, type=discipline_type)
            session.add(new_discipline)
            await session.commit()
# requests.py
async def update_user_want(user_id: int, username: str, discipline_id: int, want: int):
    async with async_session() as session:
        # Проверяем, есть ли уже запись
        result = await session.execute(
            select(UserDiscipline).where(
                UserDiscipline.user_id == user_id,
                UserDiscipline.discipline_id == discipline_id
            )
        )
        user_discipline = result.scalars().first()

        if user_discipline:
            # Если запись есть, обновляем значение want
            user_discipline.want = bool(want)
        else:
            # Если записи нет, создаем новую
            new_user_discipline = UserDiscipline(
                user_id=user_id,
                username=username,
                discipline_id=discipline_id,
                want=bool(want)
            )
            session.add(new_user_discipline)

        await session.commit()
# requests.py



async def dump_discipline(discipline_id: int, last_user: int):
    async with async_session() as session:
        temp = await get_last_user(discipline_id)
        start_id = int(temp.first)
        end_id = int(temp.last)
        # Шаг 1: Обновляем last_user в таблице Discipline
        discipline = await session.get(Discipline, discipline_id)
        if not discipline:
            raise ValueError("Дисциплина не найдена")
        await session.execute(
            update(Discipline)
            .where(Discipline.id == discipline_id)
            .values(last_user=last_user)
        )

        # Шаг 2: Находим user_id пользователей в диапазоне start_id - end_id
        users_query = select(User.username).where(User.id.between(start_id, end_id))
        users_result = await session.execute(users_query)
        user_ids = users_result.scalars().all()  # Список user_id из диапазона

        if not user_ids:
            return

        # Шаг 3: Сбрасываем want на 0 для записей с этими user_id и discipline_id
        await session.execute(
            update(UserDiscipline)
            .where(
                UserDiscipline.discipline_id == discipline_id,
                UserDiscipline.username.in_(user_ids)
            )
            .values(want=False)
        )

        await session.commit()

async def get_list(discipline_id: int) -> int:
    async with async_session() as session:
        temp = await get_last_user(discipline_id)
        last_student = int(temp.last_user)
        start_id = int(temp.first)
        end_id = int(temp.last)
        # Шаг 1: Получаем пользователей из промежутка start_id до end_id
        users_query = select(User).where(User.id.between(last_student+1, end_id))
        users_result = await session.execute(users_query)
        users = users_result.scalars().all()

        # Шаг 2: Формируем список пользователей с want == 1 для данной дисциплины
        response_lines = []
        student_count = 0  # Счетчик для нумерации студентов

        for user in users:
            # Проверяем запись в UserDiscipline
            ud_query = select(UserDiscipline).where(
                UserDiscipline.username == user.username,
                UserDiscipline.discipline_id == discipline_id
            )
            ud_result = await session.execute(ud_query)
            user_discipline = ud_result.scalars().first()

            # Если запись существует и want == True, добавляем пользователя в список
            if user_discipline and user_discipline.want:
                student_count += 1
                response_lines.append(f"{student_count}. {user.first_name} {user.last_name}")



#############################
                # Шаг 1: Получаем пользователей из промежутка start_id до end_id
                users_query = select(User).where(User.id.between(start_id, last_student))
                users_result = await session.execute(users_query)
                users = users_result.scalars().all()

                # Шаг 2: Формируем список пользователей с want == 1 для данной дисциплины
                response_lines = []
                student_count = 0  # Счетчик для нумерации студентов

                for user in users:
                    # Проверяем запись в UserDiscipline
                    ud_query = select(UserDiscipline).where(
                        UserDiscipline.username == user.username,
                        UserDiscipline.discipline_id == discipline_id
                    )
                    ud_result = await session.execute(ud_query)
                    user_discipline = ud_result.scalars().first()

                    # Если запись существует и want == True, добавляем пользователя в список
                    if user_discipline and user_discipline.want:
                        student_count += 1
                        response_lines.append(f"{student_count}. {user.first_name} {user.last_name}")

        # Шаг 3: Формируем итоговый ответ
        if not response_lines:
            return "Список пуст или никто не выбрал эту дисциплину."
        return "\n".join(response_lines)

# requests.py
async def get_discipline_id(title: str) -> int:
    async with async_session() as session:
        result = await session.execute(select(Discipline).where(Discipline.title == title))
        discipline = result.scalars().first()
        return discipline.id if discipline else None

async def get_last_user(id: int) -> int:
    async with async_session() as session:
        result = await session.execute(select(Discipline).where(Discipline.id == id))
        discipline = result.scalars().first()
        return discipline
async def populate_disciplines():
    async with async_session() as session:
        disciplines = [
            {"title": "СПО (1 группа)", "type": "subgroup", "last_user": random.randint(1, 15), "first": 1, 'last': 15},
            {"title": "СПО (2 группа)", "type": "subgroup", "last_user": random.randint(16, 30), "first": 16, 'last': 30},
            {"title": "ОАиП (1 группа)", "type": "subgroup", "last_user": random.randint(1, 15), "first": 1, 'last': 15},
            {"title": "ОАиП (2 группа)", "type": "subgroup", "last_user": random.randint(16, 30), "first": 16, 'last': 30},
            {"title": "Физика (1 группа)", "type": "subgroup", "last_user": random.randint(1, 15), "first": 1, 'last': 15},
            {"title": "Физика (2 группа)", "type": "subgroup", "last_user": random.randint(16, 30), "first": 16, 'last': 30},
            {"title": "СПО", "type": "joint", "last_user": random.randint(1, 30), "first": 1, 'last': 30},
            {"title": "ОАиП", "type": "joint", "last_user": random.randint(1, 30), "first": 1, 'last': 30}
        ]
        for disc in disciplines:
            result = await session.execute(select(Discipline).where(Discipline.title == disc["title"]))
            if not result.scalars().first():
                session.add(Discipline(title=disc["title"], type=disc["type"], last_user=disc['last_user'], first=disc['first'], last=disc['last']))
        await session.commit()

async def populate_user():
    async with async_session() as session:
        pass
        prices = [
            {"user_id": 1, "username": "dharrisss", "first_name": "Денис", "last_name": "Александренков", "want": 0},
            {"user_id": 1, "username": "ne_romchick", "first_name": "Роман", "last_name": "Амельченко", "want": 0},
            {"user_id": 1, "username": "qeliuns", "first_name": "Илья", "last_name": "Борисюк", "want": 0},
            {"user_id": 1, "username": "trista_baksov", "first_name": "Иван", "last_name": "Винников", "want": 0},
            {"user_id": 1, "username": "Seniaaaaaaaaaaa", "first_name": "Ксения", "last_name": "Гайдукевич", "want": 0},
            {"user_id": 1, "username": "alex_red_star", "first_name": "Александра", "last_name": "Гузова", "want": 0},
            {"user_id": 1, "username": "DanvFox12", "first_name": "Данила", "last_name": "Гуренков", "want": 0},
            {"user_id": 1, "username": "kausaustralis", "first_name": "Вероника", "last_name": "Драпеза", "want": 0},
            {"user_id": 1, "username": "misha_iosko", "first_name": "Михаил", "last_name": "Иосько", "want": 0},
            {"user_id": 1, "username": "genii_na_prikole", "first_name": "Андрей", "last_name": "Кацубо", "want": 0},
            {"user_id": 1, "username": "aokihagaraxd", "first_name": "Андрей", "last_name": "Кирилушкин", "want": 0},
            {"user_id": 1, "username": "paveel4", "first_name": "Павел", "last_name": "Козлюк", "want": 0},
            {"user_id": 1, "username": "g4rn0x", "first_name": "Владислав", "last_name": "Колесник", "want": 0},
            {"user_id": 1, "username": "triglet", "first_name": "Илья", "last_name": "Королев", "want": 0},
            {"user_id": 1, "username": "derevyannymackintosh", "first_name": "Дмитрий", "last_name": "Куновский",
             "want": 0},
            {"user_id": 1, "username": "mirrwsdcle", "first_name": "Дана", "last_name": "Леоновец", "want": 0},
            {"user_id": 1, "username": "tamb1masaev", "first_name": "Рустам", "last_name": "Мамедов", "want": 0},
            {"user_id": 1, "username": "droripan_kirya", "first_name": "Кирилл", "last_name": "Марчук", "want": 0},
            {"user_id": 1, "username": "Bul_Bashka", "first_name": "Егор", "last_name": "Матусевич", "want": 0},
            {"user_id": 1, "username": "andrewnewhite", "first_name": "Илья", "last_name": "Мидляр", "want": 0},
            {"user_id": 1, "username": "Qwenger", "first_name": "Тимофей", "last_name": "Могилевчик", "want": 0},
            {"user_id": 1, "username": "tamakey", "first_name": "Андрей", "last_name": "Попов", "want": 0},
            {"user_id": 1, "username": "GRRAMPUMS", "first_name": "Алексей", "last_name": "Рогаль", "want": 0},
            {"user_id": 1, "username": "kfc_serbia", "first_name": "Тимофей", "last_name": "Савин", "want": 0},
            {"user_id": 1, "username": "ykyshy11", "first_name": "Екатерина", "last_name": "Савостикова", "want": 0},
            {"user_id": 1, "username": "CEHR55555", "first_name": "Арсений", "last_name": "Третьяк", "want": 0},
            {"user_id": 1, "username": "vika_tuzova", "first_name": "Виктория", "last_name": "Тузова", "want": 0},
            {"user_id": 1, "username": "xxx_moti_xxx", "first_name": "Матвей", "last_name": "Хмара", "want": 0},
            {"user_id": 1, "username": "liza371", "first_name": "Василиса", "last_name": "Шпаковская", "want": 0},
            {"user_id": 1, "username": "lexayanush", "first_name": "Алексей", "last_name": "Янушковский", "want": 0},
        ]

        for price in prices:
            # Проверка, существует ли уже запись с таким именем
            result = await session.execute(select(User).where(User.username == price["username"]))
            existing_price = result.scalars().first()

            if not existing_price:
                new_price = User(
                    user_id=price["user_id"],
                    username=price["username"],
                    first_name=price["first_name"],
                    last_name=price["last_name"],

                )
                session.add(new_price)

        await session.commit()

# async def update_prices(prices: dict):
#     async with async_session() as session:
#         for name, value in prices.items():
#             stmt = update(Price).where(Price.name == name).values(value=value)
#             await session.execute(stmt)
#         await session.commit()

# async def update_referral(username: str, user_id: int):
#     async with async_session() as session:
#         async with session.begin():
#             if username[0] == '@':
#                 username = username[1:]
#
#             result = await session.execute(
#                 select(User).where(User.username == username)
#             )
#             user = result.scalar_one_or_none()
#             if user:
#                 ref_value = user.tg_id
#                 result = await session.execute(
#                     select(User).where(User.tg_id == user_id)
#                 )
#                 user = result.scalar_one_or_none()
#                 if user.ref == 0:
#                     stmt = update(User).where(User.tg_id == user_id).values(
#                         ref=ref_value)  # Создаем запрос на обновление
#                     await session.execute(stmt)  # Выполняем запрос
#                     await session.commit()
#                     disc = await get_discount(user_id)
#
#                     if disc < 0.1:
#                         disc = 0.1
#                         await set_discount(user_id, 0.1)
#                     return disc, ref_value
#                 return 1, 0
#             return 0, 0
#
#
# async def update_prices(prices: dict):
#     async with async_session() as session:
#         for name, value in prices.items():
#             stmt = update(Price).where(Price.name == name).values(value=value)
#             await session.execute(stmt)
#         await session.commit()
#