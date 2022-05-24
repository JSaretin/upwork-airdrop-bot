from os import environ
from telebot.async_telebot import AsyncTeleBot as TeleBot
from dotenv import load_dotenv

load_dotenv('.env')
bot = TeleBot(environ['BOT_TOKEN'])


from airdrop import admin
from airdrop import user


