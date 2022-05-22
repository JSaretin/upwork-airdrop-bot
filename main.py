from fastapi import FastAPI
import asyncio
from airdrop import bot




# bot.set_webhook('https://airdrop-bot.herokuapp.com/')
app = FastAPI()


if __name__ == '__main__':
    print('online')
    asyncio.run(bot.polling())
