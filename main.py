from bot import bot
import asyncio

if __name__ == '__main__':
    print('online')
    asyncio.run(bot.polling())
