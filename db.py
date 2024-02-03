import logging
import sys

from sqlalchemy import create_engine, Column, Integer, inspect, String, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from sqlalchemy_utils import database_exists, create_database

from config import CONNSTR

Base = declarative_base()


# Определение моделей
class Candidate(Base):
    __tablename__ = 'candidates'
    candidate_id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    link = Column(String)
    photos = relationship("Photos", back_populates="candidate")


class Photos(Base):
    __tablename__ = 'photos'
    photos_id = Column(Integer, primary_key=True)
    photos_ids = Column(Integer)
    candidate_id = Column(Integer, ForeignKey('candidates.candidate_id'))
    candidate = relationship("Candidate", back_populates="photos")


class FavoriteList(Base):
    __tablename__ = 'favorite_list'
    favorite_list_id = Column(Integer, primary_key=True)
    candidate_id = Column(Integer, ForeignKey('candidates.candidate_id'))


class BlackList(Base):
    __tablename__ = 'black_list'
    black_list_id = Column(Integer, primary_key=True)
    candidate_id = Column(Integer, ForeignKey('candidates.candidate_id'))


class Saver:
    def __init__(self, connstr: str = None):
        self.logger = logging.getLogger(__name__)
        self.engine = create_engine(connstr)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        self.database_check()
        self.table_check()

    def database_check(self):
        """
        Создает базу данных, если она не существует.
        """
        # Создание базы данных, если она не существует
        if not database_exists(self.engine.url):
            self.logger.info(f"База данных не найдена. Создаем базу данных.")
            create_database(self.engine.url)
        else:
            self.logger.info(f"База данных уже существует.")

    def table_create(self):
        """
        Создание таблиц, если они не существуют.
        """
        Base.metadata.create_all(self.engine)

    def table_check(self):
        """
        Проверка существования таблиц, создание при необходимости.
        """
        inspector = inspect(self.engine)
        for table in [Candidate.__tablename__,
                      Photos.__tablename__,
                      FavoriteList.__tablename__,
                      BlackList.__tablename__]:
            if not inspector.has_table(table):
                response = input(f'Таблица {table} не существует. Создать таблицы? (Y/N): ').upper()
                if response == 'Y':
                    self.table_create()
                    self.logger.info(f'Таблицы созданы.')
                    break
                else:
                    self.logger.info('Выход...')
                    sys.exit(0)

    def save_candidate(self, candidate_id, first_name, last_name, link):
        """
        Сохраняет кандидата.
        :param candidate_id: ID пользователя ВКонтакте
        :param first_name: Имя.
        :param last_name: Фамилия.
        :param link: URL.
        """
        candidate = Candidate(
            candidate_id=candidate_id,
            first_name=first_name,
            last_name=last_name,
            link=link
        )
        self.session.add(candidate)
        self.session.commit()

    def save_black_list(self, black_list_id, candidate_id):
        """
        Сохраняет в черный список.
        :param black_list_id: ID пользователя ВКонтакте
        :param candidate_id: ID пользователя ВКонтакте
        """
        black_list = BlackList(
            black_list_id=black_list_id,
            candidate_id=candidate_id,
        )
        self.session.add(black_list)
        self.session.commit()

    def save_favorite_list(self, favorite_list_id, candidate_id):
        """
        Сохраняет в список избранного.
        :param favorite_list_id: ID пользователя ВКонтакте
        :param candidate_id: ID пользователя ВКонтакте
        """
        favorite_list = FavoriteList(
            favorite_list_id=favorite_list_id,
            candidate_id=candidate_id,
        )
        self.session.add(favorite_list)
        self.session.commit()

    def save_photos(self, photos_ids, candidate_id):
        """
        Сохраняет фото
        :param photos_ids: ID фото
        :param candidate_id: ID пользователя ВКонтакте
        """
        photos_ids = Photos(
            photos_ids=photos_ids,
            candidate_id=candidate_id,
        )
        self.session.add(photos_ids)
        self.session.commit()

    def get_candidate_favorites(self, candidate_id):
        """
        Получает список избранных пользователей для заданного пользователя.
        :param candidate_id: ID пользователя ВКонтакте.
        :return: Список избранных пользователей.
        """
        try:
            favorites_list = self.session.query(FavoriteList).filter_by(candidate_id=candidate_id).all()
            return [favorite.favorite_list_id for favorite in favorites_list]
        except Exception as error:
            self.logger.warning(error)
            return None

    def get_candidate_black_list(self, candidate_id):
        """
        Получает черный список для заданного пользователя.
        :param candidate_id: ID пользователя ВКонтакте.
        :return: Список пользователей в черном списке.
        """
        try:
            black_list = self.session.query(BlackList).filter_by(candidate_id=candidate_id).all()
            return [black_list.black_list_id for black_list in black_list]
        except Exception as error:
            self.logger.warning(error)
            return None

    def get_user_photos(self, candidate_id):
        """
        Получает список фото для заданного пользователя.
        :param candidate_id: ID пользователя ВКонтакте.
        :return: Список идентификаторов фото.
        """
        try:
            photos = self.session.query(Photos).filter_by(candidate_id=candidate_id).all()
            return [photo.photos_ids for photo in photos]
        except Exception as error:
            self.logger.warning(error)
            return None


if __name__ == '__main__':
    Saver(CONNSTR)
