from random import randrange
import vk_api
import logging
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor



def send_message(interlocutor_id, message, keyboard, attachments):
    session.method('messages.send', {
        'user_id': interlocutor_id,
        'message': message,
        'random_id': 0,
        'keyboard': keyboard.get_keyboard(),
        'attachment': attachments
    }
                   )

def vk_bot(session, session_photo, number_attempts):
    # upload = VkUpload(session)
    for event in VkLongPoll(session).listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            attachments = []
            text = event.text.lower()
            interlocutor_id = event.user_id
            print(interlocutor_id)
            print(text)
            keyboard = VkKeyboard() #one_time=True)
            keyboard.add_button('Запустить поиск Кандидатов ', VkKeyboardColor.PRIMARY)
            if text == 'привет':
                send_message(interlocutor_id, 'Будем искать Знакомство?', keyboard, attachments)

            if text == 'запустить поиск кандидатов' or text == 'далее':
                param_find = session.method('users.get', {'user_ids': interlocutor_id, 'fields': 'bdate, sex, city'})
                city_find = param_find[0]['city']['title']
                sex = param_find[0]['sex']
                age_find = int(param_find[0]['bdate'][-4::1])
                if sex == 1:
                    sex_find_text = 'Мужчину'
                    sex_find = 2
                elif sex == 2:
                    sex_find_text = 'Женщину'
                    sex_find = 1
                else:
                    sex_find_text = 'Незномо кого'
                    sex_find = 0

                send_message(interlocutor_id, f'Будем искать {sex_find_text} '
                                              f'в городе {city_find}, примерно {age_find} '
                                              f'года рождения', keyboard, attachments)

                buttons = ['Избранное', 'Черный список', 'Далее']
                buttons_colors = [VkKeyboardColor.POSITIVE, VkKeyboardColor.NEGATIVE, VkKeyboardColor.PRIMARY]
                keyboard = VkKeyboard()
                for btn, btn_colors in zip(buttons, buttons_colors):
                    keyboard.add_button(btn, btn_colors)
                send_message(interlocutor_id,'Идет поиск кандидатов', keyboard, attachments)
                first_name, last_name, url, user_id = user_profile(session, city_find, age_find, sex_find, number_attempts)
                if first_name == last_name == url == user_id == 0:
                    send_message(interlocutor_id, f'Из {number_attempts} - попыток Кандидат не найден. Нажмите "Далее" для повторного поиска', keyboard, attachments)
                else:
                    attachments = get_top_photos(session_photo, user_id)

                    print(attachments)

                    if attachments == None:
                        send_message(interlocutor_id, f'- {first_name} {last_name},\n'
                                                      f'- ссылка на профиль: {url},\n'
                                                      f'-У Кандидата нет фото в профиле', keyboard, attachments)
                    else:
                        send_message(interlocutor_id, f'- {first_name} {last_name},\n'
                                                      f'- ссылка на профиль: {url},\n'
                                                      f'- У кандидата в профиле {len(attachments)} фотографий',
                                     keyboard, attachments=None)
                        if len(attachments) > 4:
                            n_photos = 3
                        else:
                            n_photos = len(attachments)
                        for i_photo in range(n_photos):
                            send_message(interlocutor_id, f'Фото {i_photo + 1}',
                                         keyboard, attachments[i_photo])

                    # if text == 'избранное':

                    # if text == 'черный список':



def get_top_photos(session_photo, user_id):
    api = session_photo.get_api()
    try:
        photos = api.photos.getAll(owner_id=user_id, extended=1)
        if photos['count'] == 0:
            return None

        # Сортировка фотографий по популярности (лайки)
        popular_photos = sorted(
            photos["items"],
            key=lambda x: x["likes"]["count"],
            reverse=True
        )

        # Создание списка отсортированных фотографий в формате attachments
        attachments = ['photo{}_{}'.format(popular_photos[photo_nub]['owner_id'], popular_photos[photo_nub]['id']) for photo_nub in range(len(popular_photos))]
        print(attachments)
        return attachments

    except vk_api.exceptions.ApiError as error:
        logging.error("Ошибка при получении фото пользователя: %s", error)
        return None


def user_profile(session, city_find, age_find, sex_find, number_attempts):
    lost_attempts = 0
    while lost_attempts < number_attempts:
        lost_attempts += 1
        user_id = randrange(10 ** 7)
        print(user_id, lost_attempts)
        profile = session.method('users.get', {'user_ids': user_id, 'fields': 'bdate, sex, city'})
        # print(profile)
        if 'bdate' in profile[0]:
            if '.' in profile[0]['bdate'][-4::1]:
                profile_age = 0
            else:
                profile_age = int(profile[0]['bdate'][-4::1])
        else:
            profile_age = 0

        if ('city' in profile[0] and
                'deactivated' not in profile[0] and
                'sex' in profile[0] and
                profile[0]['is_closed'] != True):
            # print(profile[0]['city']['title'], profile_age, profile[0]['sex'], profile_sex, sex)
            if (profile[0]['city']['title'] == city_find
                    and (profile_age - 5 < age_find < profile_age + 5 or profile_age == 0)
                    and sex_find == profile[0]['sex']):
                first_name = profile[0]['first_name']
                last_name = profile[0]['last_name']
                url = f'https://vk.com/id{user_id}'
                print(profile)
                print()
                return first_name, last_name, url, user_id
    return 0, 0, 0, 0


if __name__ == '__main__':
    # токен сообщества
    token = '!!!!!!!!!!!'
    # токен приложения
    token_photo = '!!!!!!!!!!!!'
    session = vk_api.VkApi(token=token)
    session_photo = vk_api.VkApi(token=token_photo)
    number_attempts = 999
    vk_bot(session, session_photo, number_attempts)
