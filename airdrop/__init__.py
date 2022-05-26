from os import environ
from telebot.async_telebot import AsyncTeleBot as TeleBot


bot = TeleBot(environ['TELEGRAM_TOKEN'])


from airdrop import admin
from airdrop import user


