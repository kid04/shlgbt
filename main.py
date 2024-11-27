import telebot
from save_load import *
from sharefile import *
from keyboards import *
from messages import *
from get_url import get_video_title
import json
from UserJSON import user_json
import datetime
import threading

import os
for dirname, dirnames, filenames in os.walk('.'):
    # print path to all subdirectories first.
    for subdirname in dirnames:
        print(os.path.join(dirname, subdirname))
    # print path to all filenames.
    for filename in filenames:
        print(os.path.join(dirname, filename))
    # Advanced usage:
    # editing the 'dirnames' list will stop os.walk() from recursing into there.
    if '.git' in dirnames:
        # don't go into any .git directories.
        dirnames.remove('.git')
    if 'venv' in dirnames:
            # don't go into any .git directories.
            dirnames.remove('venv')




bot = telebot.TeleBot("6984896175:AAEnN3vBZ5Ms5S3t0DKN3xBkVQIeuCVkTt0")

user_dict = {}
user_comment_to = {}
f = open('data.json', 'r')
data = json.load(f)
f.close()

class MainFilter(telebot.custom_filters.AdvancedCustomFilter):

    key = 'text'

    @staticmethod
    def check(message, text):
        return message.text in text


class CallbackFilter(telebot.custom_filters.AdvancedCustomFilter):
    """
    Авторский фильтр для обработки функции обратного вызова

    Истино, если текст сообщения соответствует значению text
    """
    key = 'message_text'

    @staticmethod
    def check(call, text):
        return text == call.message.text


class CallbackFilterSoft(telebot.custom_filters.AdvancedCustomFilter):
    """
    Авторский фильтр для обработки функции обратного вызова

    Истино, если текст сообщения содержит text
    """
    key = 'message_contains'

    @staticmethod
    def check(call, text):
        return text in call.message.text


@bot.message_handler(commands=['restore_friendship'])
def restore_friendship(message):
    """
    Обработчик команды по обновлению списка друзей

    :param message: сообщение от пользователя
    """
    user = message.from_user.username
    data[user]['friends'].clear()
    for friend in data:
        if user in data[friend]["friends"]:
            data[user]["friends"].append(friend)
    save(data)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    """
    Обработчик команды начала работы с ботом
    :param message: сообщение от пользователя
    """
    keyboard = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(text="начать слать шлягеры!", callback_data="poehali")
    keyboard.add(button1)
    bot.reply_to(message, start_message, reply_markup=mainmenu_keyboard)

    if message.from_user.username not in data:
        print("Новый челик!")
        data[message.from_user.username] = user_json
        data[message.from_user.username]['chat_id'] = message.chat.id
        save(data)


@bot.message_handler(text=['разослать шлягер'])
def send_music(message):
    """
    Обработчик команды рассылки музыки друзьям
    :param message: сообщение от пользователя
    """
    if data[message.from_user.username]['friends']:
        user_dict[message.chat.id] = Sharing()
        user_dict[message.chat.id].sender = message.from_user.username
        user_dict[message.chat.id].to_send = True
        if data[message.from_user.username]['reciever_options']:
            text = 'Кому отправляем? (введи числа через пробел)'
            i = 0
            for f in data[message.from_user.username]['friends']:
                text = text + '\n' + str(i + 1) + '. @' + f
                i += 1
            msg = bot.send_message(message.chat.id, text)
            bot.register_next_step_handler(msg, process_share_music_step)
        else:
            process_share_music_step(message)
    else:
        bot.send_message(message.chat.id, "У вас нет друзей, чтобы с ними делиться!")


@bot.message_handler(text=['настройки'])
def process_settings(message):
    """
    Обработчик команды открытия меню настроек
    :param message: сообщение от пользователя
    """
    bot.send_message(message.chat.id, "настройки", reply_markup=settings_keyboard)

@bot.message_handler(text=['добавить друга'])
def add_friend(message):
    """
    Обработчик команды добавления друга
    :param message: сообщение от пользователя
    """
    msg = bot.send_message(message.chat.id,
                           'Кого вы хотите добавить в друзья? пришлите ник в тг (пример: @schlagerbot)')
    bot.register_next_step_handler(msg, process_friend_request_step)


def process_share_music_step(message):
    """
    Обработчик второго шага рассылки музыки друзьям
    :param message: сообщение от пользователя
    """
    try:
        if data[message.from_user.username]['reciever_options']:
            shares = message.text.split(' ')
            for i in shares:
                user_dict[message.chat.id].friends.append(data[message.from_user.username]['friends'][int(i) - 1])
        else:
            for friend in data[message.from_user.username]['friends']:
                user_dict[message.chat.id].friends.append(friend)
        bot.send_message(message.chat.id, "Когда отправить?", reply_markup=time_keyboard)


    except Exception as e:
        bot.reply_to(message, 'oooops')


@bot.callback_query_handler(func=lambda call: True, message_text='Когда отправить?')
def set_time_step(call):
    """
    Обработчик выбора времени рассылки
    """
    if call.data == "now":
        set_type_step(call.message)
    if call.data == "notification":
        sharing_time[user_dict[call.message.chat.id]] = data[user_dict[call.message.chat.id].sender][
            'notifications']['share_notification']
        set_type_step(call.message)
    if call.data == "set_time":
        msg = bot.send_message(call.message.chat.id, "Введите час, когда надо будет отправить шлягер")
        bot.register_next_step_handler(msg, set_time_step)
    bot.answer_callback_query(call.id)


def set_time_step(message):
    """
    Обработчик выбора точного времени рассылки
    :param message: сообщение пользователя
    """
    try:
        sharing_time[user_dict[message.chat.id]] = [message.text]
        set_type_step(message)
    except Exception as e:
        bot.send_message(message.chat.id, "Что-то пошло не так")


def set_type_step(message):
    """
    Обработчик выбора типа рассылаемого контента
    """
    keyboard = types.InlineKeyboardMarkup()

    button1 = types.InlineKeyboardButton(text="Шлягер", callback_data="solo")
    button2 = types.InlineKeyboardButton(text="Плейлист", callback_data="album")
    keyboard.add(button1, button2)
    bot.send_message(message.chat.id, 'Шлягер или плейлист?', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True, message_text='настройки')
def settings(call):
    """
    Обработчик выбора подменю настроек
    """
    if call.data == "settings_friend":
        bot.edit_message_text("настройки друзей", call.message.chat.id, call.message.message_id,
                              reply_markup=settings_friend_keyboard)
    elif call.data == "settings_reminder":
        bot.edit_message_text("как часто напоминать присылать шлягер?", call.message.chat.id, call.message.message_id,
                              reply_markup=settings_notifications_keyboard)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: True, message_text='настройки друзей')
def settings_friend(call):
    """
    Обработчик выбора пункта "Друзья" в подменю настроек
    """
    if call.data == "reciever_options":
        bot.edit_message_text("спрашивать кому слать шлягер?", call.message.chat.id, call.message.message_id,
                              reply_markup=yesno_keyboard)
    if call.data == "mute_friend":
        bot.edit_message_text("Приглушённые друзья", call.message.chat.id, call.message.message_id,
                              reply_markup=mute_settings_keyboard)
        #mute_friend(call.from_user)
    if call.data == "delete_friend":
        delete_friend(call.from_user)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: True, message_text='Приглушённые друзья')
def settings_friend(call):
    """
    Обработчик выбора пункта "Приглушенные друзья" в подменю настроек
    """
    if call.data == "mute_friend":
        mute_friend(call.from_user)
    if call.data == "unmute_friend":
        unmute_friend(call.from_user)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: True, message_text='как часто напоминать присылать шлягер?')
def settings_notifications(call):
    """
    Обработчик выбора пункта "Уведомления" в подменю настроек
    """
    if call.data == "1_time":
        data[call.from_user.username]['notifications']['share_notification'] = ["12"]
        bot.send_message(call.message.chat.id, "Готово! Теперь вы будете получать уведомления в 12 часов")
    elif call.data == "never":
        data[call.from_user.username]['notifications']['share_notification'] = []
        bot.send_message(call.message.chat.id, "Готово! Теперь вы не будете получать уведомления")
    elif call.data == "4_time":
        data[call.from_user.username]['notifications']['share_notification'] = ["8", "12", "16", "20"]
        bot.send_message(call.message.chat.id, "Готово! Теперь вы будете получать уведомления в 8, 12, 16 и 20 часов")
    elif call.data == "hourly":
        data[call.from_user.username]['notifications']['share_notification'] = ["1", "2", "3", "4", "5", "6", "7", "8",
                                                                                "9", "10", "11", "12", "13", "14", "15",
                                                                                "16", "17", "18", "19", "20", "21",
                                                                                "22", "23", "24"]
        bot.send_message(call.message.chat.id, "Готово! Теперь вы будете получать уведомления ежечасно!")
    elif call.data == "set_time":
        msg = bot.send_message(call.message.chat.id,
                               "Введите часы, в которые вы хотели бы получать уведомления(через пробел")
        bot.register_next_step_handler(msg, share_notifications_time_step)
    save(data)
    bot.answer_callback_query(call.id)


def share_notifications_time_step(message):
    """
    Функция установления времени уведомлений
    :message: перечисленные через пробел числа - часы, в которые пользователь хочет получать уведомления
    """
    try:
        times = message.text.split(' ')
        data[message.from_user.username]['notifications']['share_notification'] = times
        bot.send_message(message.chat.id, "Готово! Теперь вы будете получать уведомления в указанные вами часы")
        save(data)
    except Exception as e:
        bot.send_message(message.chat.id, "что-то пошло не так")


def mute_friend(user):
    """
    Функция приглушения друзей. Отправляет пользователю список неприглушенных друзей для возможного приглушения
    """
    if data[user.username]['friends']:
        text = 'Кого приглушаем? (введи числа через пробел)'
        i = 0
        for f in data[user.username]['friends']:
            if f not in data[user.username]['muted_friends']:
                text = text + '\n' + str(i + 1) + '. @' + f
                i += 1
        if i != 0:
            msg = bot.send_message(data[user.username]['chat_id'], text)
            bot.register_next_step_handler(msg, process_mute_friends_step)
        else:
            bot.send_message(data[user.username]['chat_id'], "У вас нет неприглушённых друзей")
    else:
        bot.send_message(data[user.username]['chat_id'], "У вас нет друзей, чтобы их приглушить!")


def unmute_friend(user):
    """
    Функция отмены приглушения друзей. Отправляет пользователю список приглушенных друзей для возможной отмены
    приглушения
    """
    print(data[user.username]['muted_friends'])
    if data[user.username]['muted_friends']:
        text = 'Кого перестаём приглушать? (введи числа через пробел)'
        i = 0
        for f in data[user.username]['friends']:
            text = text + '\n' + str(i + 1) + '. @' + f
            i += 1
        msg = bot.send_message(data[user.username]['chat_id'], text)
        bot.register_next_step_handler(msg, process_unmute_friends_step)
    else:
        bot.send_message(data[user.username]['chat_id'], "У вас нет приглушённых друзей!")


def process_unmute_friends_step(message):
    """Функция отмены приглушения друзей. Отменяет приглушения для выбранных друзей.
    message: номера друзей, которых надо перестать приглушать, перечисленные через пробел
    """
    try:
        mutes = message.text.split(' ')
        for i in mutes:
            print(data[message.from_user.username]['muted_friends'])
            data[message.from_user.username]['muted_friends'].remove(
                data[message.from_user.username]['friends'][int(i) - 1])
        bot.send_message(message.chat.id, "Ваших друзей больше не приглушают!")
        save(data)
    except Exception as e:
        bot.send_message(message.chat.id,
                         "Это не похоже на список друзей, которых ты хочешь перестать приглушать. Ладно, ничего не изменится.")


def process_mute_friends_step(message):
    """Функция  приглушения друзей. Приглушает выбранных друзей.
    message: номера друзей, которых надо приглушить, перечисленные через пробел
    """
    try:
        mutes = message.text.split(' ')
        for i in mutes:
            data[message.from_user.username]['muted_friends'].append(
                data[message.from_user.username]['friends'][int(i) - 1])
        bot.send_message(message.chat.id, "Ваши друзья были приглушены!")
        save(data)
    except Exception as e:
        bot.send_message(message.chat.id,
                         "Это не похоже на список друзей, которых ты хочешь заглушить. Ладно, никто не будет заглушен")


def delete_friend(user):
    """
    Функция удаления друзей. Отправляет пользователю список неприглушенных друзей для возможного удаления
    """
    if data[user.username]['friends']:
        text = 'Кому удаляем? (введи числа через пробел)'
        i = 0
        for f in data[user.username]['friends']:
            text = text + '\n' + str(i + 1) + '. @' + f
            i += 1
        msg = bot.send_message(data[user.username]['chat_id'], text)
        bot.register_next_step_handler(msg, process_delete_friends_step)
    else:
        bot.send_message(data[user.username]['chat_id'], "У вас и так уже нет друзей!")


def process_delete_friends_step(message):
    """Функция  удаления друзей. Удаляет выбранных друзей.
       message: номера друзей, которых надо удалить, перечисленные через пробел
       """
    try:
        deletes = message.text.split(' ')
        for i in deletes:
            data[data[message.from_user.username]['friends'].pop(int(i) - 1)]['friends'].remove(message.from_user.username)
        bot.send_message(message.chat.id, "Вы и эти люди больше не друзья!")
        save(data)
    except Exception as e:
        bot.send_message(message.chat.id,
                         "Это не похоже на список друзей, которых ты хочешь удалить. Ладно, никто не будет удален")


@bot.callback_query_handler(func=lambda call: True, message_text='спрашивать кому слать шлягер?')
def set_asking(call):
    """
    Обработчик настройки уведомлений
    """
    if call.data == "yes":
        data[call.from_user.username]['reciever_options'] = True
        bot.send_message(call.message.chat.id, "хорошо")
    if call.data == "no":
        data[call.from_user.username]['reciever_options'] = False
        bot.send_message(call.message.chat.id, "хорошо")
    save(data)
    bot.edit_message_text("настройки", call.message.chat.id, call.message.message_id, reply_markup=settings_keyboard)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: True, message_contains="предлагает вам дружбу")
def apply_friendship(call):
    """
    Обработчик добавления друзей
    """
    friend = call.message.text.split(' ')[0][1:]
    recipient = call.from_user.username
    if call.data == "yes":
        data[recipient]['friend_requests'].remove(friend)
        data[recipient]['friends'].append(friend)
        data[friend]['friends'].append(recipient)
        bot.send_message(data[recipient]['chat_id'], "Вы добавили @" + friend + " в друзья.")
        bot.send_message(data[friend]['chat_id'], "@" + recipient + " и вы теперь друзья.")

    if call.data == "no":
        data[recipient]['friend_requests'].remove(friend)
        bot.send_message(data[recipient]['chat_id'], "Вы отказались от дружбы с @" + friend)
    save(data)
    bot.answer_callback_query(call.id)


@bot.message_handler(commands=['delayed'])
def debug_delay(message):
    """
    Вывод музыки, которая будет отправлена позднее. Для целей отладки
    """
    for music in sharing_time:
        print(music.title, sharing_time[music])


def process_send_url_step(message):
    """
    Функция рассылки URL
    """
    user_dict[message.chat.id].url = message.text
    user = user_dict[message.chat.id]
    try:
        user.title, user.author = get_video_title(user.url)
        keyboard = types.InlineKeyboardMarkup()

        button1 = types.InlineKeyboardButton(text="Хочу", callback_data="commentary")
        button2 = types.InlineKeyboardButton(text="Отправить так", callback_data="no_com")
        keyboard.add(button1, button2)

        bot.send_message(message.chat.id, "Получил, скоро отправлю друзьям. Хочешь добавить что-то ещё?",
                         reply_markup=keyboard)

    except Exception as e:
        bot.send_message(message.chat.id, "Ссылка оформлена неправильно! Нажми разослать шлягер и попробуй еще раз (обрати внимание чтобы кроме ссылки других символов не было)")


def add_commentary(message):
    """
    Функция добавления комментария
    """
    user_dict[message.chat.id].commentary = message.text
    if user_dict[message.chat.id] not in sharing_time:
        share_music(user_dict[message.chat.id])
        bot.send_message(message.chat.id, "Шлягер в пути!")
    else:
        bot.send_message(message.chat.id, "Шлягер будет доставлен вовремя!")


def share_music(user):
    """
    Функция рассылки музыки
    user: пользователь-отправитель
    """
    if user.to_send:
        user.to_send = False
        for friend in user.friends:
            if user.sender not in data[friend]['muted_friends']:
                bot.send_message(data[friend]['chat_id'],
                                 "Твой друг @" + user.sender + " поделился с тобой " + user.type + "ом " +
                                 user.author + " - " + user.title + "! Хочешь послушать?",
                                 reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(text="Разослать шлягер в ответ",
                                 callback_data='music')).add(types.InlineKeyboardButton(text="Прокоментировать шлягер", callback_data='commentary')))
                bot.send_message(data[friend]['chat_id'], user.url)
                if not user.commentary == "":
                    bot.send_message(data[friend]['chat_id'], ">" + user.commentary + "\n \- @" + user.sender,
                                     parse_mode='MarkdownV2')
            else:
                if 'muted_share' not in data[friend]:
                    data[friend]['muted_share'] = {}
                if user.sender not in data[friend]['muted_share']:
                    data[friend]['muted_share'][user.sender] = []
                q = Mute_sharing(user)
                data[friend]['muted_share'][user.sender].append(q.__dict__)
                save(data)


@bot.callback_query_handler(func=lambda call: True, message_contains=" Новых шлягеров! Хочешь послушать?" )
def mute_message(call):
    """
    Фукция рассылки уведомлений от заглушенных друзей
    """
    text = ""
    i = 1
    for song in data[call.from_user.username]['muted_share'][call.data]:
        text += str(i)+'. '+song['author']+' '+song['title']+'\n'+song['url']+'\n'+song['commentary']+' - @'+call.data+'\n\n'
        i += 1
    bot.send_message(call.message.chat.id, text)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: True, message_contains='! Хочешь послушать?')
def share_music_back(call):
        """
        Функция отправки музыки или комментария в ответ
        """
        txt = call.message.text
        username = txt.split(' ')[2][1:]
        print(username)
        type = txt.split(" поделился с тобой ")[1].split("ом ")[0]
        author = txt.split("ом ")[1].split(" - ")[0]
        title = txt.split(" - ")[1].split("!")[0]

        back_type = call.data
        if back_type == 'music':
            user_dict[call.message.chat.id] = Sharing()
            user_dict[call.message.chat.id].sender = call.from_user.username
            user_dict[call.message.chat.id].to_send = True
            user_dict[call.message.chat.id].friends = [username]
            set_type_step(call.message)
        if back_type == 'commentary':

            msg = bot.edit_message_text(call.message.message_id, call.message.chat.id, "Напиши свой комментарий к этому треку!")
            user_comment_to[call.message.chat.id] = [username, type, author, title]
            bot.register_next_step_handler(msg, give_commentary_back)
        bot.answer_callback_query(call.id)


def give_commentary_back(message):
    """
    Функция отправки комментария
    """
    receiver_id = data[user_comment_to[message.chat.id][0]]['chat_id']
    type = user_comment_to[message.chat.id][1]
    author = user_comment_to[message.chat.id][2]
    title = user_comment_to[message.chat.id][3]
    bot.send_message(receiver_id, "Твой друг прокомментировал отправленный тобой "+type+": "+author+" - "+title+"!")
    bot.send_message(receiver_id, ">" + message.text + "\n \- @" + message.from_user.username,
                     parse_mode='MarkdownV2')


@bot.callback_query_handler(func=lambda call: True)
def process_pick_type_step(call):
    """
    Общий обработчик кнопок
    """
    try:
        if call.data == "solo":
            user_dict[call.message.chat.id].type = "шлягер"
            msg = bot.send_message(call.message.chat.id, "Шли ссыль на шлягер")
            bot.register_next_step_handler(msg, process_send_url_step)
        if call.data == "album":
            user_dict[call.message.chat.id].type = "плейлист"
            msg = bot.send_message(call.message.chat.id, "Шли ссыль на плейлист")
            bot.register_next_step_handler(msg, process_send_url_step)
        if call.data == "commentary":
            msg = bot.send_message(call.message.chat.id, 'что хочешь добавить?')
            bot.register_next_step_handler(msg, add_commentary)
        if call.data == "no_com":
            if user_dict[call.message.chat.id] not in sharing_time:
                share_music(user_dict[call.message.chat.id])
                bot.send_message(call.message.chat.id, "Шлягер в пути!")
            else:
                bot.send_message(call.message.chat.id, "Шлягер будет доставлен вовремя!")
        if call.data == "poehali":
            bot.send_message(call.message.chat.id, 'отлично, поехали')
        if call.data == "share":
            call.message.from_user = call.from_user
            send_music(call.message)
        bot.answer_callback_query(call.id)
    except Exception as e:
        bot.send_message(call.message.chat.id, "Эта кнопка не работает :(")


@bot.message_handler(text=['добавить друга'])
def send_request(message):
    """
    Обработчик отправки приглашения дружды
    """
    msg = bot.send_message(message.chat.id, 'Кого вы хотите добавить в друзья?')
    bot.register_next_step_handler(msg, process_friend_request_step)


def process_friend_request_step(message):
    """
    Функция рассылки приглашения дружбы
    """
    try:
        chat_id = message.chat.id
        friend = message.text[1:]

        if friend in data:
            if message.from_user.username in data[friend]['friend_requests']:
                bot.send_message(chat_id, "Вы уже отправили приглашение")
            elif friend in data[message.from_user.username]['friends']:
                bot.send_message(chat_id, "Вы и @" + friend + " уже друзья!")
            else:
                keyboard = types.InlineKeyboardMarkup()

                button1 = types.InlineKeyboardButton(text="Принять", callback_data="yes")
                button2 = types.InlineKeyboardButton(text="Отклонить", callback_data="no")
                keyboard.add(button1, button2)
                bot.send_message(data[friend]['chat_id'], '@' + message.from_user.username + ' предлагает вам дружбу',
                                 reply_markup=keyboard)
                data[friend]['friend_requests'].append(message.from_user.username)
                bot.send_message(chat_id, "Ваш приглос подружиться был отправлен")
        else:
            if message.text[0] == "@":
                bot.send_message(chat_id, "Этого человека ещё нет в боте")
        save(data)
    except Exception as e:
        bot.reply_to(message, 'oooops')


saved_time = ""


def message_timer():
    """Функция рассылки сообщений, назначенных на определённое время"""
    global saved_time
    while 1:
        if str(datetime.datetime.now().strftime("%H")) != saved_time:
            saved_time = str(datetime.datetime.now().strftime("%H"))
            for user in data:
                if str(int(saved_time)) in data[user]['notifications']['share_notification']:
                    bot.send_message(data[user]['chat_id'], "Хей-хей, самое время разослать шлягер!", reply_markup=share_notification_keyboard)
                if str(int(saved_time)) in data[user]['notifications']['muted_friends']:
                    if not 'muted_share' in data[user]:
                        data[user]['muted_share'] = []
                    for friend in data[user]['muted_share']:
                        if data[user]['muted_share'][friend]:
                            bot.send_message(data[user]['chat_id'], "Твой друг @"+friend+" прислал тебе "+str(len(data[user]['muted_share'][friend]))+" Новых шлягеров! Хочешь послушать?", reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Показать список', callback_data=friend)))
            for music in sharing_time:
                if str(int(saved_time)) in sharing_time[music]:
                    share_music(music)
                    sharing_time.pop(music)


x = threading.Thread(target=message_timer)
x.start()


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    ...


bot.add_custom_filter(MainFilter())
bot.add_custom_filter(CallbackFilter())
bot.add_custom_filter(CallbackFilterSoft())
bot.infinity_polling()
