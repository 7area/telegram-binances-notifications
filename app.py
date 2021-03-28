#!/usr/bin/python
#TelegramBOT: бот для оповещания смены статуса заказов Binance
#Разработчик: Илья Вяткин
#GitHub: https://github.com/7area

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton 


from binance.client import Client
import asyncio

import db
import re

#------------------------------------------
#------------------КОНФИГ------------------
#------------------------------------------

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

#------------------------------------------
#----------------КЛАВИАТУРА----------------
#------------------------------------------

button_list_account = KeyboardButton('Список аккаунтов')
button_list_order = KeyboardButton('Список заказов')
button_info = KeyboardButton('Информация')

main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(button_list_order,button_list_account).add(button_info)

#------------------------------------------
#-------------НАЧАЛО ДИАЛОГА---------------
#------------------------------------------
@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message, query):
    db.add_user(query.from_user.id)
    await message.answer("Привет!\nЭто бот для оповещания смены статуса заказов на сервисе обмена цифровых валют Binance.", reply_markup = main_keyboard)

#------------------------------------------
#-----------------ЭНДПОИНТЫ----------------
#------------------------------------------
@dp.callback_query_handler(lambda query: True)
async def endpoints(query):
    state = str(query.data)
    if state.startswith("/add"):
        reg = r"\/add\s(\S+)\s(\S+)"
        matches = re.search(reg, state)
        client = Client(str(matches[1]), str(matches[2]))
        status = client.get_system_status()
        if status["status"] == "0":
            list_accounts = db.search_accounts(query.message.chat.id)   
            for account in list_accounts:
                if account[2] == str(matches[1]):
                    await bot.send_message("Этот аккаунт уже есть в вашем списке")
                    break
            else:        
                db.add_account(query.from_user.id, str(matches[1]), str(matches[2]))
                orders = client.get_all_orders()
                for order in orders:
                    db.easy_add_order(account[1], str(matches[1]), str(matches[2]), order["status"], order["symbol"])

    elif state.startswith("/rmv"):
        reg = r"\/rmv\s(\S+)"
        matches = re.search(reg, state)

        accounts = db.search_accounts(query.from_user.id)
        for account in accounts:
            if account[2]:
                db.remove_account(query.from_user.id, str(matches[1]))
                break
        else:
            await bot.send_message("В вашем списке нет этого аккаунта")

    elif state.startswith("/ntf"):
        reg = r"\/ntf\s(\S+)"
        matches = re.search(reg, state)
        changed = db.change_status_notification(query.from_user.id, str(matches[1]))
        if changed[0] and changed[1] == "1":
            await bot.send_message(f'Уведомления аккаунта {str(matches[1])} включены')
        elif changed[0] and changed[1] == "0":
            await bot.send_message(f'Уведомления аккаунта {str(matches[1])} отключены')
        elif changed[0] and changed[1] == True:
            await bot.send_message(f'В вашем списке нет аккаунта {str(matches[1])}')
        else:
            await bot.send_message('Я тебя не понимаю:(')
        
    else:
        await bot.send_message('Я тебя не понимаю:(')

#------------------------------------------
#------------------КНОПКИ------------------
#------------------------------------------
@dp.message_handler(lambda message: message.text == "Список аккаунтов")
async def process_print_list_apis(message: types.Message, query):
    list_accounts = db.search_accounts(query.message.chat.id)   
    
    if not list_accounts: 
        await bot.send_message("У вас нет привязанных аккаунтов")
    
    msg = str()
    for account in list_accounts:
        msg = msg.join(f"{account[2]}")
        if account[4] == "1":
            msg = msg.join(f" - оповещания вкл./n")
        else:
            msg = msg.join(f" - оповещания откл./n")
    await bot.send_message(msg)

@dp.message_handler(lambda message: message.text == "Список заказов")
async def process_print_list_apis(message: types.Message, query):
    list_orders = db.search_orders(query.message.chat.id)   
    
    if list_orders: 
        await bot.send_message("У вас нет привязанных аккаунтов")
    
    msg = str()
    for account in list_orders:
        msg = msg.join(f"{account[2]} - {account[4]} - {account[5]}/n")
    await bot.send_message(msg)

@dp.message_handler(lambda message: message.text == "Информация")
async def process_print_info(message: types.Message):
    await bot.send_message(
        """
        /add API-KEY API-SECRET - добавляет аккаунт в Ваш отслеживаем список/n
        /rmv API-KEY - удаляет аккаунт из Вашего списка отслеживания/n
        /ntf API-KEY - вкл./откл. оповещание о изменение статуса заказов аккаунта/n
        Кнопка /"Список аккаунтов/" - возвращает список всех аккаунтов/n
        Кнопка /"Список заказов/" - возвращает список всех заказов/n
        """
        )

#------------------------------------------
#--------------ПРОВЕРКА СТАТУСОВ-----------
#------------------------------------------ 
async def checker(wait_for):
    while True:
        await asyncio.sleep(wait_for)

        accounts = db.print_all_accounts()
        for account in accounts:
            client = Client(account[2], account[3])
            orders = client.get_all_orders()
            for order in orders:
                checker = db.add_order(account[1], account[2], account[3], order["status"], order["symbol"])
                if checker[0]:
                    if checker[1]:
                        await bot.send_message(account[1], f'Зарегистрирован новый заказ на криптовалюту {order["symbol"]}/nСтатус заказа {order["symbol"]}')
                    else:
                        await bot.send_message(account[1], f'Статус заказа на криптовалюту {order["symbol"]} обновлен: {order["symbol"]}')
                else:
                    continue


if __name__ == '__main__':
    dp.loop.create_task(checker(10))
    executor.start_polling(dp, skip_updates=True)