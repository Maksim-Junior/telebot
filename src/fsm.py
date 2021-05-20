import sqlalchemy as sa
from sqlalchemy.orm import declarative_base, sessionmaker
from config import settings

engine = sa.create_engine(settings.database_url)
Session = sessionmaker(bind=engine)
Base = declarative_base()


class UserModel(Base):
    __tablename__ = "users"

    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer)
    blog_user_id = sa.Column(sa.Integer)
    blog_username = sa.Column(sa.Text)


def select_user_from_db(user_id: int) -> UserModel:
    ...


async def get_or_create_user(user_id: int) -> "User2":
    record = select_user_from_db(user_id)
    if not record:
        await insert_user(user_id)
        record = await select_user_from_db(user_id)

    user = User2.parse_obj(record)
    return user
