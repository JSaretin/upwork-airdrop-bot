from os import environ
from telebot.async_telebot import AsyncTeleBot as TeleBot




bot = TeleBot(environ.get('BOT_TOKEN', '5303775819:AAGHnHmhPIUQDVxNYD9y5Z4uFZbbpwqNdwE'))



from airdrop import admin
from airdrop import user


