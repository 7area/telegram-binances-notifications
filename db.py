#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3
import os
import re

path_database = f'{os.getcwd()}//database.db'
database = sqlite3.connect(path_database)
cursor_db = database.cursor()

#------------------------------------------
#------------------ВЫВОД-------------------
#------------------------------------------
def print_all_accounts():
    with sqlite3.connect(path_database):
        cursor_db.execute('''SELECT * FROM "ACCOUNTS"''')
        rows = cursor_db.fetchall()
        return rows

def print_all_orders():
    with sqlite3.connect(path_database):
        cursor_db.execute('''SELECT * FROM "ORDERS"''')
        rows = cursor_db.fetchall()
        return rows

#------------------------------------------
#------------------АККАУНТЫ----------------
#------------------------------------------
def add_account(id_telegram, api_key, api_secret):
    with sqlite3.connect(path_database):
        cursor_db.execute('''
                        INSERT INTO "ACCOUNTS" (
                            "id_telegram",
                            "api_key",
                            "api_secret",
                            "notification"
                        ) VALUES (
                            ?,
                            ?,
                            ?,
                            ?
                        )''',
                        (id_telegram,
                        api_key,
                        api_secret,
                        "1"
                        )
                    )  
    
    database.commit()

def remove_account(id_telegram, api_key):
    with sqlite3.connect(path_database):
        cursor_db.execute('''DELETE FROM "ACCOUNTS" 
            WHERE 
            "id_telegram" = ? 
            AND 
            "api_key" = ?
            ''', 
            (
            id_telegram, 
            api_key
            )
        )    
        database.commit()

def change_status_notification(id_telegram, api_key):
    status = search_status_notification(id_telegram, api_key)
    if status[0]:
        if status[1] == "1":
            status = "0"
        else:
            status = "1"
    else:
        if status[1]:
            return (False, True)
        else:
            return (False, False)

    with sqlite3.connect(path_database):
        cursor_db.execute('''UPDATE "ACCOUNTS" 
            SET
            "status_notification" = ?
            WHERE 
            "id_telegram" = ? 
            AND 
            "api_key" = ?
            ''', 
            (
            status,
            id_telegram, 
            api_key
            )
        )   

    database.commit()
    return (True, status)

def search_status_notification(id_telegram, api_key):
    rows = print_all_accounts()
    for row in rows:
        if row[1] == id_telegram and row[2] == api_key and row[3] == "1":
            database.commit()
            return True, "1"
        
        elif row[1] == id_telegram and row[2] == api_key and row[3] == "0":
            database.commit()
            return True, "0"
        
        else:
            continue
    if rows:
        return (False, True)
    else:
        return (False, False)

def search_accounts(id_telegram):
    rows = print_all_accounts()
    accounts = list()
    for row in rows:
        if row[1] == id_telegram:
            accounts.append(row)
    return accounts

#------------------------------------------
#------------------ЗАКАЗЫ------------------
#------------------------------------------
def add_order(id_telegram, api_key, api_secret, symbol, status):
    checker = check_order(id_telegram, api_key, symbol, status)
    if checker[0] == False and checker[1] == False:
        with sqlite3.connect(path_database):
            cursor_db.execute('''
                            INSERT INTO "ORDERS" (
                                "id_telegram",
                                "api_key",
                                "api_secret",
                                "symbol",
                                "status"
                            ) VALUES (
                                ?,
                                ?,
                                ?,
                                ?,
                                ?
                            )''',
                            (
                            id_telegram, 
                            api_key, 
                            api_secret, 
                            symbol, 
                            status
                            )
                        )         
        database.commit()
        return (True, True)

    elif checker[0] == True and checker[1] == False:
        update_status_order(id_telegram, api_key, symbol, status)
        return (True, False)

    else:
        return (False, False)

def update_status_order(id_telegram, api_key, symbol, status):
    with sqlite3.connect(path_database):
        cursor_db.execute('''UPDATE "ORDERS" 
            SET
            "status" = ?
            WHERE 
            "id_telegram" = ?
            AND
            "api_key" = ?
            AND
            "symbol" = ?
            ''', 
            (
            status,
            id_telegram,
            api_key,
            symbol
            )
        )   

    database.commit()

def remove_order(id_telegram, api_key, symbol, status):
    checker = check_order(id_telegram, api_key, symbol, status)
    if checker[0] == True:
        with sqlite3.connect(path_database):
            cursor_db.execute('''DELETE FROM "ORDERS" 
                WHERE 
                "api_key" = ?
                ''', 
                (
                api_key
                )
            )    
        
        database.commit()
        return True
    else:
        return False

def check_order(id_telegram, api_key, symbol, status):
    rows = print_all_orders()
    for row in rows:
        if row[1] == id_telegram and row[2] == api_key and row[4] == symbol:
            if row[5] == status:
                return (True, True)
            else:
                return (True, False)
        else:
            continue
    return (False, False)

def search_orders(id_telegram):
    rows = print_all_orders()
    orders = list()
    for row in rows:
        if row[1] == id_telegram:
            orders.append(row)
    return orders

def easy_add_order(id_telegram, api_key, api_secret, symbol, status):
    with sqlite3.connect(path_database):
        cursor_db.execute('''
                        INSERT INTO "ORDERS" (
                            "id_telegram",
                            "api_key",
                            "api_secret",
                            "symbol",
                            "status"
                        ) VALUES (
                            ?,
                            ?,
                            ?,
                            ?,
                            ?
                        )''',
                        (
                        id_telegram, 
                        api_key, 
                        api_secret, 
                        symbol, 
                        status
                        )
                    )         
    database.commit()
#------------------------------------------
#------------------ЮЗЕРЫ-------------------
#------------------------------------------
def add_user(id_telegram):
    with sqlite3.connect(path_database):
        cursor_db.execute('''
                        INSERT INTO "users" (
                            "id_telegram"
                        ) VALUES (
                            ?
                        )''',
                        (
                        id_telegram
                        )
                    )  
    
    database.commit()

