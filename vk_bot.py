
import vk_api
from sqlalchemy.testing.plugin.plugin_base import logging

from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from db import Saver
from config import CONNSTR, USER_TOKEN, TOKEN_PHOTO

def send_message(interlocutor_id, message, keyboard, attachments):
    session.method('messages.send', {
        'user_id': interlocutor_id,
        'message': message,
        'random_id': 0,
        'keyboard': keyboard.get_keyboard(),
        'attachment': attachments
    }
                   )

def vk_bot(session, session_photo):

    for event in VkLongPoll(session).listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            attachments = []
            text = event.text.lower()
            interlocutor_id = event.user_id
            keyboard = VkKeyboard()
            keyboard.add_button('Запустить поиск Кандидатов ', VkKeyboardColor.PRIMARY)
            db = Saver(CONNSTR)

            if text == 'привет':
                send_message(interlocutor_id, 'Будем искать Знакомство?', keyboard, attachments)

            if text == 'запустить поиск кандидатов' or text == 'далее':
                param_find = session.method('users.get', {'user_ids': interlocutor_id, 'fields': 'bdate, sex, city'})
                city_find = param_find[0]['city']['title']
                city_id_find = param_find[0]['city']['id']
                sex = param_find[0]['sex']
                age_find = int(param_find[0]['bdate'][-4::1])
                if sex == 1:
                    sex_find_text = 'Мужчину'
                    sex_find = 2
                elif sex == 2:
                    sex_find_text = 'Женщину'
                    sex_find = 1
                else:
                    sex_find_text = 'Незнамо кого'
                    sex_find = 0

                send_message(interlocutor_id, f'Будем искать {sex_find_text} '
                                              f'в городе {city_find}, примерно {age_find} '
                                              f'года рождения', keyboard, attachments)

                buttons = ['В Избранное', 'В Черный список', 'Далее']
                buttons_colors = [VkKeyboardColor.POSITIVE, VkKeyboardColor.NEGATIVE, VkKeyboardColor.PRIMARY]
                keyboard = VkKeyboard()
                for btn, btn_colors in zip(buttons, buttons_colors):
                    keyboard.add_button(btn, btn_colors)
                keyboard.add_line()
                keyboard.add_button('Показать Избранное и Закончить', VkKeyboardColor.SECONDARY)
                send_message(interlocutor_id,'Идет поиск кандидатов', keyboard, attachments)

                result_profile = user_profile(city_id_find, age_find, sex_find, db, interlocutor_id, keyboard, attachments)

                if result_profile.user_id == None:
                    send_message(interlocutor_id, f'Из 999 - попыток Кандидат не найден. '
                                                  f'Нажмите "Далее" для повторного поиска', keyboard, attachments)
                else:
                    attachments = get_top_photos(session_photo, result_profile.user_id)
                    if attachments == None:
                        send_message(interlocutor_id, f'- {result_profile.first_name} {result_profile.last_name},\n'
                                                      f'- ссылка на профиль: {result_profile.url},\n'
                                                      f'-У Кандидата нет фото в профиле', keyboard, attachments)
                        db.save_candidate(candidate_id=result_profile.user_id, first_name=result_profile.first_name, last_name=result_profile.last_name,
                                          link=result_profile.url)
                        db.save_photos(attachment_photo='У Кандидата нет фото в профиле', candidate_id=result_profile.user_id)

                    else:
                        send_message(interlocutor_id, f'- {result_profile.first_name} {result_profile.last_name},\n'
                                                      f'- ссылка на профиль: {result_profile.url},\n'
                                                      f'- У кандидата в профиле {len(attachments)} фотографий',
                                     keyboard, attachments=None)
                        db.save_candidate(candidate_id=result_profile.user_id, first_name=result_profile.first_name, last_name=result_profile.last_name,
                                          link=result_profile.url)

                        if len(attachments) > 3:
                            n_photos = 3
                        else:
                            n_photos = len(attachments)
                        for i_photo in range(n_photos):
                            send_message(interlocutor_id, f'Фото {i_photo + 1}',
                                         keyboard, attachments[i_photo])
                            db.save_photos(attachment_photo=attachments[i_photo], candidate_id=result_profile.user_id)

            if text == 'в избранное':
                db.save_favorite_list(candidate_id=result_profile.user_id)

            if text == 'в черный список':
                db.save_black_list(candidate_id=result_profile.user_id)

            if text == 'показать избранное и закончить':
                list_user_candidate_id = db.get_candidate_favorites()
                list_favorites_candidates = [db.get_user_candidate(candidate_id=user_candidate) for user_candidate in
                                             list_user_candidate_id]

                for favorites_candidates_in_list in list_favorites_candidates:
                    send_message(interlocutor_id,
                                 f'\nКАНДИДАТ ИЗ ИЗБРАННОГО\n'
                                 f'- {favorites_candidates_in_list[0]} {favorites_candidates_in_list[1]},\n'
                                 f'- ссылка на профиль: {favorites_candidates_in_list[2]},\n',
                                 keyboard, attachments=None)
                    print("Candidate: ", favorites_candidates_in_list)
                    favorites_candidate_photos_list = favorites_candidates_in_list[3]
                    for photo_number in range(len(favorites_candidate_photos_list)):
                        send_message(interlocutor_id, f'Фото {photo_number + 1}',
                                     keyboard, favorites_candidate_photos_list[photo_number])

                send_message(interlocutor_id, 'Поиск закончен', keyboard, attachments)
                break


def get_top_photos(session_photo, user_id):
    api = session_photo.get_api()
    try:
        photos = api.photos.getAll(owner_id=user_id, extended=1)
        if photos['count'] == 0:
            return None

        # Сортировка фотографий по популярности (лайки + комментарии)
        popular_photos = sorted(
            photos["items"],
            key=lambda x: x["likes"]["count"],
            reverse=True
        )

        # Создание списка отсортированных фотографий в формате attachments
        attachments = ['photo{}_{}'.format(popular_photos[photo_nub]['owner_id'],
                                           popular_photos[photo_nub]['id']) for photo_nub in range(len(popular_photos))]
        return attachments

    except vk_api.exceptions.ApiError as error:
        logging.error("Ошибка при получении фото пользователя: %s", error)
        return None

class Profile:
    def __init__(self, first_name='', last_name='', url='', user_id=None):
        self.first_name = first_name
        self.last_name = last_name
        self.url = url
        self.user_id = user_id


def user_profile(city_id_find, age_find, sex_find, db, interlocutor_id, keyboard, attachments):
    list_candidate = db.get_list_candidate_id()
    request_params = {
        'count': 999,  # Количество результатов
        'domain': 'https://api.vk.com/',
        'fields': 'city, id, first_name, last_name, sex, bdate ',
        'city_id': city_id_find,
        'sex': sex_find,
    }
    limiting_attempts = 0
    while limiting_attempts < 1:
        result_profile = Profile
        response = session_photo.method('users.search', request_params)
        for profile in response['items']:
            if 'bdate' in profile:
                if '.' in profile['bdate'][-4::1]:
                    profile_age = 0
                else:
                    profile_age = int(profile['bdate'][-4::1])
            else:
                profile_age = 0
            '''
            Для исключения повторного вывода уже найденных кандидатов вводим условия 
            profile['id'] not in list_candidate
            '''
            if ('city' in profile
                    and 'deactivated' not in profile
                    and 'sex' in profile
                    and profile['is_closed'] != True
                    and profile['id'] not in list_candidate):
                """
                Для увеличения количество кандидатов profile_age == 0
                """
                if (profile['city']['id'] == city_id_find
                        and (profile_age - 5 < age_find < profile_age + 5 or profile_age == 0)
                        and sex_find == profile['sex']):
                    result_profile.first_name = profile["first_name"]
                    result_profile.last_name = profile["last_name"]
                    result_profile.user_id = profile["id"]
                    result_profile.url = f'https://vk.com/id{profile['id']}'
                    return result_profile


        send_message(interlocutor_id, f'Из 999 - попыток Кандидат не найден. '
                                               f'Нажмите "Далее" для повторного поиска', keyboard, attachments)



if __name__ == '__main__':
    # токен сообщества
    token = USER_TOKEN
    # токен приложения
    token_photo = TOKEN_PHOTO
    session = vk_api.VkApi(token=token)
    session_photo = vk_api.VkApi(token=token_photo)
    vk_bot(session, session_photo)
