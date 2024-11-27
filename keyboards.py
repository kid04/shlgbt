from telebot import types
"""Список всех используемых клавиатур бота"""
mainmenu_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True).add("добавить друга").add("разослать шлягер").add("настройки")

settings_button1 = types.InlineKeyboardButton(text="настройки друзей", callback_data="settings_friend")
settings_button2 = types.InlineKeyboardButton(text="настройки напоминаний", callback_data="settings_reminder")
settings_button3 = types.InlineKeyboardButton(text="настройки отправки", callback_data="settings_send")
settings_button4 = types.InlineKeyboardButton(text="настройки получения", callback_data="settings_recieve")
settings_keyboard = types.InlineKeyboardMarkup().add(settings_button1).add(settings_button2).add(settings_button3).add(
    settings_button4)

friendbutt1 = types.InlineKeyboardButton(text="Приглушённые друзья", callback_data="mute_friend")
friendbutt2 = types.InlineKeyboardButton(text="напоминание о приглушенных", callback_data="mute_reminder")
friendbutt3 = types.InlineKeyboardButton(text="ограничение рассылки", callback_data="reciever_options")
friendbutt4 = types.InlineKeyboardButton(text="удалить друга", callback_data="delete_friend")
friendbutt5 = types.InlineKeyboardButton(text="список приглашений", callback_data="friendrequest_list")
settings_friend_keyboard = types.InlineKeyboardMarkup().add(friendbutt1).add(friendbutt2).add(friendbutt3).add(
    friendbutt4).add(friendbutt5)

mute_button = types.InlineKeyboardButton(text="Приглушить друзей", callback_data="mute_friend")
unmute_button = types.InlineKeyboardButton(text="Перестать приглушать друзей", callback_data="unmute_friend")

mute_settings_keyboard = types.InlineKeyboardMarkup().add(mute_button).add(unmute_button)

no_button = types.InlineKeyboardButton(text="Не напоминать", callback_data='never')
oncebutton = types.InlineKeyboardButton(text="1 раз в день", callback_data="1_time")
fourbutton = types.InlineKeyboardButton(text="4 раза в день", callback_data="4_time")
hourlybutton = types.InlineKeyboardButton(text="Каждый час", callback_data="hourly")
settimebutton = types.InlineKeyboardButton(text="Настроить время", callback_data="set_time")
settings_notifications_keyboard = types.InlineKeyboardMarkup().add(no_button).add(oncebutton).add(fourbutton).add(hourlybutton).add(
    settimebutton)


button_yes = types.InlineKeyboardButton(text="да", callback_data="yes")
button_no = types.InlineKeyboardButton(text="нет", callback_data="no")
yesno_keyboard = types.InlineKeyboardMarkup().add(button_yes, button_no)

button_now = types.InlineKeyboardButton(text="Сейчас", callback_data="now")
button_notification = types.InlineKeyboardButton(text="Во время напоминания", callback_data="notification")
button_set_time = types.InlineKeyboardButton(text="Выбрать время", callback_data="set_time")
time_keyboard = types.InlineKeyboardMarkup().add(button_now, button_notification).add(button_set_time)

share_notification_keyboard = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(text="Разослать шлягер",
                                                                                          callback_data="share"))

share_back_keyboard = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(
    text="Разослать шлягер в ответ", callback_data="share_back")).add(types.InlineKeyboardButton(
    text="Прокомментировать шлягер", callback_data="commentary_back"))

