import logging
import sys
from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, inspect, String, ForeignKey, DateTime
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from sqlalchemy_utils import database_exists, create_database

from config import CONNSTR

Base = declarative_base()


# Определение моделей
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String)
    profile_url = Column(String)
    age = Column(Integer)
    gender = Column(String)
    city_id = Column(Integer, ForeignKey('cities.id'))
    interests = Column(String)

    searches = relationship("UserSearches", back_populates="user")
    favorites = relationship("Favorites", back_populates="user")


class City(Base):
    __tablename__ = 'cities'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    users = relationship("User", back_populates="city")


class UserSearchResults(Base):
    __tablename__ = 'user_search_results'
    id = Column(Integer, primary_key=True)
    search_id = Column(Integer, ForeignKey('user_searches.id'))
    found_user_id = Column(Integer)

    search = relationship("UserSearches", back_populates="results")


class UserSearches(Base):
    __tablename__ = 'user_searches'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    timestamp = Column(DateTime, default=datetime.utcnow)
    criteria_id = Column(Integer, ForeignKey('search_criteria.id'))

    results = relationship("UserSearchResults", back_populates="search")


class SearchCriteria(Base):
    __tablename__ = 'search_criteria'
    id = Column(Integer, primary_key=True)
    age_range = Column(String)
    gender_preference = Column(String)
    city_id = Column(Integer, ForeignKey('cities.id'))
    interests = Column(String)

    search = relationship("UserSearches", back_populates="criteria")


class MatchResult(Base):
    __tablename__ = 'match_results'
    id = Column(Integer, primary_key=True)
    search_id = Column(Integer, ForeignKey('user_searches.id'))
    matched_user_id = Column(Integer)

    search = relationship("UserSearches", back_populates="results")


class Favorites(Base):
    __tablename__ = 'favorites'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    favorite_user_id = Column(Integer)

    user = relationship("User", back_populates="favorites")


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
        for table in [User.__tablename__,
                      City.__tablename__,
                      SearchCriteria.__tablename__,
                      MatchResult.__tablename__]:
            if not inspector.has_table(table):
                response = input(f'Таблица {table} не существует. Создать таблицы? (Y/N): ').upper()
                if response == 'Y':
                    self.table_create()
                    self.logger.info(f'Таблицы созданы.')
                    break
                else:
                    self.logger.info('Выход...')
                    sys.exit(0)

    def save_search_criteria(self, user_id, age_range,
                             gender_preference, city_id, status):
        """
        Сохраняет критерии поиска пользователя.
        :param user_id: ID пользователя ВКонтакте.
        :param age_range: Возрастной диапазон.
        :param gender_preference: Пол.
        :param city_id: ID города.
        :param status: Семейное положение.
        """
        criteria = SearchCriteria(user_id=user_id,
                                  age_range=age_range,
                                  gender_preference=gender_preference,
                                  city_id=city_id,
                                  status=status)
        self.session.add(criteria)
        self.session.commit()

    def save_match_result(self, searcher_id, matched_user_id, score):
        """
        Сохраняет результаты поиска.
        :param searcher_id: ID искателя.
        :param matched_user_id: ID найденного пользователя.
        :param score: Оценка совпадения.
        """
        match = MatchResult(searcher_id=searcher_id,
                            matched_user_id=matched_user_id,
                            score=score)
        self.session.add(match)
        self.session.commit()

    def get_user_search_history(self, user_id):
        """
        Получает историю поисков для заданного пользователя.
        :param user_id: ID пользователя ВКонтакте.
        :return: Список истории поисков.
        """
        search_history = self.session.query(UserSearches).filter_by(user_id=user_id).all()
        return [(search.id, search.timestamp, search.criteria_id) for search in search_history]

    def get_user_favorites(self, user_id):
        """
        Получает список избранных пользователей для заданного пользователя.
        :param user_id: ID пользователя ВКонтакте.
        :return: Список избранных пользователей.
        """
        favorites = self.session.query(Favorites).filter_by(user_id=user_id).all()
        return [favorite.favorite_user_id for favorite in favorites]


if __name__ == '__main__':
    Saver(CONNSTR)
