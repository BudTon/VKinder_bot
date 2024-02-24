import logging
import sys

from sqlalchemy import create_engine, Column, Integer, inspect, String, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from sqlalchemy_utils import database_exists, create_database

from config import CONNSTR

Base = declarative_base()

'''
Определение моделей
'''

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
    attachment_photo = Column(String)
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
        candidate = Candidate(
            candidate_id=candidate_id,
            first_name=first_name,
            last_name=last_name,
            link=link
        )
        self.session.add(candidate)
        self.session.commit()


    def save_black_list(self, candidate_id):
        black_list = BlackList(candidate_id=candidate_id)
        self.session.add(black_list)
        self.session.commit()


    def save_favorite_list(self, candidate_id):
        favorite_list = FavoriteList(candidate_id=candidate_id)
        self.session.add(favorite_list)
        self.session.commit()


    def save_photos(self, attachment_photo, candidate_id):
        attachment_photo = Photos(
            attachment_photo=attachment_photo,
            candidate_id=candidate_id
        )
        self.session.add(attachment_photo)
        self.session.commit()


    def get_candidate_favorites(self):
        try:
            favorites_list_all = self.session.query(FavoriteList).all()
            return [favorite.candidate_id for favorite in favorites_list_all]
        except Exception as error:
            self.logger.warning(error)
            return []


    def get_candidate_black_list(self):
        try:
            black_list_all = self.session.query(BlackList).all()
            return [black_list.black_list_id for black_list in black_list_all]
        except Exception as error:
            self.logger.warning(error)
            return []


    def get_list_candidate_id(self):
        try:
            list_candidate_id_all = self.session.query(Candidate).all()
            return [list_candidate_id.candidate_id for list_candidate_id in list_candidate_id_all]
        except Exception as error:
            self.logger.warning(error)
            return []


    def get_user_photos(self, candidate_id):
        try:
            photos = self.session.query(Photos).filter_by(candidate_id=candidate_id).all()
            return [photo.attachment_photo for photo in photos]
        except Exception as error:
            self.logger.warning(error)
            return []


    def get_user_candidate(self, candidate_id):
        try:
            candidates = self.session.query(Candidate).filter_by(candidate_id=candidate_id).all()
            photos = self.session.query(Photos).filter_by(candidate_id=candidate_id).all()
            photos_list = [photo.attachment_photo for photo in photos]
            result = [[candidate.first_name, candidate.last_name, candidate.link, [photos_list][0]]
                      for candidate in candidates]
            return result[0]
        except Exception as error:
            self.logger.warning(error)
            return []


if __name__ == '__main__':
    Saver(CONNSTR)
