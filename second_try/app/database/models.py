from sqlalchemy import BigInteger, String, Column, Integer, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

DATABASE_URL = 'sqlite+aiosqlite:///db.sqlite3'

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()

# models.py
class Discipline(Base):
    __tablename__ = 'disciplines'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True, index=True)  # Название дисциплины, например "СПО (1 группа)"
    type = Column(String, index=True)  # Тип: "subgroup" или "joint"
    last_user = Column(Integer, index=True)
    first = Column(Integer, index=True)
    last = Column(Integer, index=True)
# models.py
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, index=True, default=None)
    username = Column(String, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)

# models.py
class UserDiscipline(Base):
    __tablename__ = 'user_discipline'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id'), index=True)
    username = Column(String, index=True)
    discipline_id = Column(Integer, ForeignKey('disciplines.id'), index=True)
    want = Column(Boolean, default=False, index=True)  # 1 или 0 (True/False)

    # Связи для удобства (опционально)
    user = relationship("User", back_populates="disciplines")
    discipline = relationship("Discipline", back_populates="users")

# Добавляем обратные связи в модели
User.disciplines = relationship("UserDiscipline", back_populates="user")
Discipline.users = relationship("UserDiscipline", back_populates="discipline")
class TemporaryEvent(Base):
    __tablename__ = 'temporary_events'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)

async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)