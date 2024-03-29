"""
Файл, содержащий необходимые переменные
"""

import configparser

# Объект парсера
config = configparser.ConfigParser()

if len(config.read("settings.ini")) == 0:
    print('Добавьте файл settings.ini')
    exit()

# Токен пользователя
USER_TOKEN = config.get('settings', 'user_token')

# Токен приложения
TOKEN_PHOTO = config.get('settings', 'photo_token')

# База данных
CONNSTR = config.get("database", "connstr")
