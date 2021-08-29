from datetime import datetime

from aiogram.types import User
from gino import Gino
from gino.schema import GinoSchemaVisitor
from sqlalchemy import sql, Column, Integer, BigInteger, Boolean, Sequence, Text, Float

from data.config import DB_USER, DB_PASS, HOST
from data.urls import URL

db = Gino()


class Subscriber(db.Model):
    __tablename__ = "subscribers"
    query: sql.Select

    id = Column(Integer, Sequence('subscriber_id_seq'), primary_key=True)
    subscriber_id = Column(BigInteger)
    for key, _ in URL.items():
        attr = f'{key} = Column(Boolean, default=False)'
        exec(attr)
    subscription = Column(Boolean)

    def get_categories_dict(self):
        cat_dict = {}
        for key, _ in URL.items():
            attr = f"self.{key}"
            cat_dict.update([(key, eval(attr))])
        return cat_dict

    def __repr__(self):
        repr_string = ""
        for key, _ in URL.items():
            attr = f"self.{key}"
            repr_string += f"{key}='{eval(attr)}', "
        return f"<Subscriber(id='{self.id}', subscribers_id='{self.subscriber_id}', " \
               f"subscription='{self.subscription}'), categories({repr_string})>"


class Publication(db.Model):
    __tablename__ = "publications"
    query: sql.Select

    category = Column(Text)
    publications = Column(Text)
    last_publication_timestamp = Column(Float)

    def __repr__(self):
        last_date = datetime.fromtimestamp(self.last_publication_timestamp)
        return f"<Publication(category='{self.category}', " \
               f"last_publication_timestamp='{last_date.strftime('%d-%m-%Y %H:%M')}', " \
               f"publications='{self.publications}')>"


class DBCommands:

    @staticmethod
    async def get_subscriber(subscriber_id):
        subscriber = await Subscriber.query.where(Subscriber.subscriber_id == subscriber_id).gino.first()
        return subscriber

    async def add_new_subscriber(self, subscriber: User):
        old_subs = await self.get_subscriber(subscriber.id)
        if old_subs:
            return None
        new_subs = Subscriber()
        new_subs.subscriber_id = subscriber.id
        new_subs.subscription = True
        await new_subs.create()
        return new_subs

    async def update_subscriber(self, subscriber_id, category):
        db_subscriber = await self.get_subscriber(subscriber_id)
        b = f'db_subscriber.{category}==False'
        status_false = eval(b)
        if status_false:
            status = True
        else:
            status = False
        attr = f'Subscriber.update.values({category}={status}).where(Subscriber.subscriber_id == subscriber_id).gino.status()'
        await eval(attr)

    @staticmethod
    async def get_subscribers_for_posting():
        subscribers = await Subscriber.query.where(Subscriber.subscription == True).gino.all()
        return subscribers

    @staticmethod
    async def get_publications():
        publications = await Publication.query.gino.all()
        return publications

    @staticmethod
    async def get_category(category):
        db_category = await Publication.query.where(Publication.category == category).gino.first()
        return db_category

    async def add_new_category(self, category, timestamp):
        is_category = await self.get_category(category)
        if is_category:
            return None
        new_category = Publication()
        new_category.category = category
        new_category.publications = None
        new_category.last_publication_timestamp = timestamp
        await new_category.create()

    @staticmethod
    async def update_publications(category, all_pages_list, now_date):
        if len(all_pages_list) == 0:
            last_publication_timestamp = now_date
        else:
            last_publication_timestamp = all_pages_list[0][2]
        await Publication.update.values(publications=str(all_pages_list),
                                        last_publication_timestamp=last_publication_timestamp). \
            where(Publication.category == category).gino.status()


async def create_db():
    await db.set_bind(f'postgresql://{DB_USER}:{DB_PASS}@{HOST}/nogino')

    db.gino: GinoSchemaVisitor
    # await db.gino.drop_all()
    await db.gino.create_all()
