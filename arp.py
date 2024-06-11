import ast
import datetime as time
from time import sleep
import scapy.all as scapy
from scapy.layers.dot11 import Dot11, Dot11Deauth, RadioTap 
from tkinter import *

import telebot

config_file = 'config.txt'

def read_config(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    
    config_dict = ast.literal_eval(content)
    token = config_dict.get('token', "")
    id = config_dict.get('id', "")
    known_mac_addresses = config_dict.get('known_mac_addresses', [])
    ap_mac = config_dict.get('ap_mac', "")
    
    return token, id, known_mac_addresses, ap_mac

# Чтение конфигурации
token, id, known_mac_addresses, ap_mac = read_config(config_file)

bot = telebot.TeleBot(token)

set_deauth = False
stop = True
set_interval = False
deauth_menu = False
main_menu = True

@bot.message_handler(commands=['start'])
def start(message):
    global stop, send_deauth, main_menu
    stop = True
    markup = telebot.types.ReplyKeyboardMarkup()
    btn1 = telebot.types.KeyboardButton("Одно сканирование")
    btn2 = telebot.types.KeyboardButton("Сканирование с интервалом")
    if(set_deauth == False):
        btn3 = telebot.types.KeyboardButton("❌ Управление режимом деаунтификации")
    else:
        btn3 = telebot.types.KeyboardButton("✅ Управление режимом деаунтификации")
    markup.add(btn1, btn2, btn3)
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}! Укажи вариант защиты', reply_markup=markup)
    main_menu = True

@bot.message_handler(content_types=['text'])   
def handle_message(message):
    global main_menu, deauth_menu, set_deauth, set_interval, stop
    if(message.text == "Стоп"):
        bot.send_message(message.chat.id, text="Все процессы приостановлены")
        set_deauth = False
        set_interval = False
        deauth_menu = False
        main_menu = False
        stop = False
    elif main_menu:
        if message.text in ["❌ Управление режимом деаунтификации", "✅ Управление режимом деаунтификации"]:
            markup = telebot.types.ReplyKeyboardMarkup()
            btn1 = telebot.types.KeyboardButton("Включить")
            btn2 = telebot.types.KeyboardButton("Отключить")
            back = telebot.types.KeyboardButton("Вернуться в главное меню")
            markup.add(btn1, btn2, back)
            bot.send_message(message.chat.id, text="Выбери режим", reply_markup=markup)
            deauth_menu = True
            main_menu = False
        elif message.text == "Одно сканирование":
            if not set_deauth:
                scan("192.168.0.0/28", 0)
            else:
                scan("192.168.0.0/28", 2)
        elif message.text == "Сканирование с интервалом":
            markup_back = telebot.types.ReplyKeyboardMarkup()
            btn_back = telebot.types.KeyboardButton("Назад")
            markup_back.add(btn_back)
            bot.send_message(message.chat.id, text="Задай интервал", reply_markup=markup_back)
            set_interval = True
            main_menu = False
        else:
            bot.send_message(message.chat.id, text="Непонятная команда!")
    elif deauth_menu:
        if message.text == "Включить":
            set_deauth = True
            bot.send_message(message.chat.id, text="Режим деаунтификации включен")
        elif message.text == "Отключить":
            set_deauth = False
            bot.send_message(message.chat.id, text="Режим деаунтификации отключен")
        elif message.text == "Вернуться в главное меню":
            markup = telebot.types.ReplyKeyboardMarkup()
            btn1 = telebot.types.KeyboardButton("Одно сканирование")
            btn2 = telebot.types.KeyboardButton("Сканирование с интервалом")
            if(set_deauth == False):
                btn3 = telebot.types.KeyboardButton("❌ Управление режимом деаунтификации")
            else:
                btn3 = telebot.types.KeyboardButton("✅ Управление режимом деаунтификации")
            markup.add(btn1, btn2, btn3)
            bot.send_message(message.chat.id, 'Укажи вариант защиты', reply_markup=markup)
            main_menu = True
            deauth_menu = False
        else:
            bot.send_message(message.chat.id, text="Непонятная команда!")
    elif(set_interval == True):
        if(message.text == "Назад"):
            markup = telebot.types.ReplyKeyboardMarkup()
            btn1 = telebot.types.KeyboardButton("Одно сканирование")
            btn2 = telebot.types.KeyboardButton("Сканирование с интервалом")
            if(set_deauth == False):
                btn3 = telebot.types.KeyboardButton("❌ Управление режимом деаунтификации")
            else:
                btn3 = telebot.types.KeyboardButton("✅ Управление режимом деаунтификации")
            markup.add(btn1, btn2, btn3)
            bot.send_message(message.chat.id, "Укажи вариант защиты", reply_markup=markup)
            main_menu = True
            set_interval = False
        else:
            try:
                settings = int(message.text)
                if not set_deauth:
                    while stop:
                        scan("192.168.0.0/28", 1)
                        sleep(settings)
                    main_menu = True
                else:
                    while stop:
                        scan("192.168.0.0/28", 3)
                        sleep(settings)
                    main_menu = True
            except ValueError:
                bot.send_message(message.chat.id, text="Неверное значение!")
    elif(stop == False):
        bot.send_message(message.chat.id, text="Все процессы приостановлены, перезапустите /start")
        set_deauth = False
        set_interval = False
        deauth_menu = False
        main_menu = False
        stop = False

         
def send(mac):
    bot.send_message(id, f"{time.datetime.now()}\nВНИМАНИЕ! \nОбнаружено неизвестное устройство\n{mac}")

def send_deauth(ap, client, interval, count, iface="wlan0"):
    dot11 = Dot11(addr1=client, addr2=ap, addr3=ap)
    packet = RadioTap()/dot11/Dot11Deauth(reason=7)
    scapy.sendp(packet, iface=iface, count=count, inter = interval)

def scan(ip, a):
    global set_deauth
    global stop
    print(set_deauth)
    print(time.datetime.now())
    arp_request = scapy.ARP(pdst=ip)
    arp_br = scapy.Ether(dst = "ff:ff:ff:ff:ff:ff")
    combined = arp_br / arp_request
    answer_list, un_list = scapy.srp(combined, timeout=3)
    answer_list.summary()
    
    for sent, received in answer_list:
        mac = received.hwsrc
        if mac not in known_mac_addresses:
            if a == 0:
                send(mac)
                break
            elif a == 1:
                send(mac)
            elif a == 2:
                send(mac)
                bot.send_message(id, "Переход в режим экстренной деаутентификации")
                while(stop):
                    send_deauth(ap_mac, mac, interval = 1, count=5, iface="wlan0")
                break
            elif a == 3:
                send(mac)
                bot.send_message(id, "Переход в режим экстренной деаутентификации")
                while(stop):
                    send_deauth(ap_mac, mac, interval = 1, count=5, iface="wlan0")
    if (a == 0):
        bot.send_message(id, f"Сканирование завершено\nКоличество устройств:{len(answer_list)}")


bot.polling(non_stop=True)