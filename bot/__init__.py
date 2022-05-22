from os import environ
from telebot.async_telebot import AsyncTeleBot as TeleBot

bot = TeleBot(environ['BOT_TOKEN'])

from bot import register_handlers